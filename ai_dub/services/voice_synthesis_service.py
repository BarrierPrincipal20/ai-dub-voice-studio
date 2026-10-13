"""TTS service. Batches segments and time-fits each to its source slot."""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import numpy as np
import soundfile as sf

from ai_dub.config.settings import StudioSettings
from ai_dub.models.segment import TranslatedSegment
from ai_dub.models.voice import SynthesisRequest

log = logging.getLogger(__name__)


class VoiceSynthesisService:
    def __init__(self, settings: StudioSettings) -> None:
        self._settings = settings
        self._engine = None

    def _load_engine(self):
        if self._engine is not None:
            return self._engine
        if self._settings.tts_engine == "xtts":
            from TTS.api import TTS  # noqa: PLC0415

            self._engine = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        else:
            raise NotImplementedError(f"tts_engine {self._settings.tts_engine} not wired yet")
        return self._engine

    async def synthesize_batch(
        self, segments: list[TranslatedSegment], voice_id: str
    ) -> list[Path]:
        render_dir = self._settings.render_dir / "segments"
        render_dir.mkdir(parents=True, exist_ok=True)
        tasks = [
            self._synthesize_one(seg, voice_id, render_dir / f"{seg.source.index:04d}.wav")
            for seg in segments
        ]
        return await asyncio.gather(*tasks)

    async def _synthesize_one(
        self, segment: TranslatedSegment, voice_id: str, out: Path
    ) -> Path:
        voice_ref = self._settings.voice_profile_dir / voice_id / "reference.wav"
        if not voice_ref.exists():
            raise FileNotFoundError(f"voice profile missing: {voice_ref}")

        req = SynthesisRequest(
            text=segment.target_text,
            voice_id=voice_id,
            lang=segment.target_lang,
            target_duration_s=segment.source.duration_s,
        )
        loop = asyncio.get_running_loop()
        wav_path = await loop.run_in_executor(None, self._render_blocking, req, voice_ref, out)
        return self._time_fit(wav_path, req.target_duration_s or 0.0)

    def _render_blocking(self, req: SynthesisRequest, voice_ref: Path, out: Path) -> Path:
        engine = self._load_engine()
        engine.tts_to_file(
            text=req.text,
            speaker_wav=str(voice_ref),
            language=req.lang,
            file_path=str(out),
            speed=req.speed,
        )
        return out

    def _time_fit(self, wav: Path, target_s: float) -> Path:
        """Linear time-stretch so dubbed speech lands in the source slot."""
        if target_s <= 0:
            return wav
        audio, sr = sf.read(wav, always_2d=False)
        current = len(audio) / sr
        if abs(current - target_s) / target_s < 0.12:
            return wav
        ratio = current / target_s
        if ratio < 0.5 or ratio > 2.0:
            log.warning("time-stretch ratio %.2f clipped for %s", ratio, wav.name)
            ratio = float(np.clip(ratio, 0.5, 2.0))
        n_out = int(len(audio) / ratio)
        idx = np.linspace(0, len(audio) - 1, n_out)
        stretched = np.interp(idx, np.arange(len(audio)), audio)
        sf.write(wav, stretched.astype(audio.dtype), sr)
        return wav