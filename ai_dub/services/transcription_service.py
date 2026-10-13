"""ASR wrapper. Uses faster-whisper; falls back to CPU on CUDA OOM."""
from __future__ import annotations

import logging
from pathlib import Path

from ai_dub.config.settings import StudioSettings
from ai_dub.models.segment import TranscriptSegment

log = logging.getLogger(__name__)


class TranscriptionService:
    def __init__(self, settings: StudioSettings) -> None:
        self._settings = settings
        self._model = None

    def _ensure_model(self, device: str):
        if self._model is not None:
            return self._model
        from faster_whisper import WhisperModel  # local import: slow to load

        self._model = WhisperModel(
            self._settings.asr_model,
            device=device,
            compute_type=self._settings.asr_compute_type,
        )
        return self._model

    def transcribe(self, media: Path, lang_hint: str | None = None) -> list[TranscriptSegment]:
        device = self._settings.asr_device
        if device == "auto":
            device = "cuda"
        try:
            model = self._ensure_model(device)
            segments, _info = model.transcribe(str(media), language=lang_hint, vad_filter=True)
        except RuntimeError as exc:
            if "out of memory" in str(exc).lower() and device != "cpu":
                log.warning("CUDA OOM on ASR, falling back to CPU")
                self._model = None
                model = self._ensure_model("cpu")
                segments, _info = model.transcribe(str(media), language=lang_hint, vad_filter=True)
            else:
                raise

        return [
            TranscriptSegment(
                index=i,
                start_s=s.start,
                end_s=s.end,
                text=s.text.strip(),
                confidence=max(0.0, 1.0 - s.no_speech_prob),
            )
            for i, s in enumerate(segments)
            if s.text.strip()
        ]