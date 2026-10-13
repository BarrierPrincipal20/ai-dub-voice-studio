"""End-to-end dubbing pipeline: transcribe -> translate -> synthesize -> mix.

Concurrency: run_sync is blocking and safe to call from a worker thread.
run() is the async variant for CLI/parallel batching.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from ai_dub.adapters.ffmpeg_adapter import FfmpegAdapter
from ai_dub.models.dub_job import DubResult
from ai_dub.models.segment import TranslatedSegment
from ai_dub.services.transcription_service import TranscriptionService
from ai_dub.services.translation_service import TranslationService
from ai_dub.services.voice_synthesis_service import VoiceSynthesisService

log = logging.getLogger(__name__)


class DubPipeline:
    def __init__(
        self,
        transcription: TranscriptionService,
        translation: TranslationService,
        synthesis: VoiceSynthesisService,
    ) -> None:
        self._asr = transcription
        self._mt = translation
        self._tts = synthesis

    def run_sync(
        self,
        source: Path,
        target_lang: str,
        voice_id: str,
        out_path: Path,
    ) -> DubResult:
        return asyncio.run(self.run(source, target_lang, voice_id, out_path))

    async def run(
        self,
        source: Path,
        target_lang: str,
        voice_id: str,
        out_path: Path,
    ) -> DubResult:
        warnings: list[str] = []
        segments = self._asr.transcribe(source)

        translated: list[TranslatedSegment] = []
        for seg in segments:
            try:
                translated.append(await self._mt.translate_segment(seg, target_lang))
            except Exception as exc:  # noqa: BLE001 — keep pipeline alive
                warnings.append(f"segment {seg.index} untranslated: {exc}")
                translated.append(
                    TranslatedSegment(
                        source=seg, target_text=seg.text, target_lang=target_lang, engine="passthrough"
                    )
                )

        stems = await self._tts.synthesize_batch(translated, voice_id=voice_id)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        mixed = FfmpegAdapter.mix_tracks(stems, source, out_path, keep_background=True)

        log.info("dub complete: %s -> %s", source.name, out_path.name)
        return DubResult(
            job_id=f"{source.stem}-{target_lang}",
            out_path=mixed,
            duration_s=FfmpegAdapter.probe_duration(mixed),
            segments=translated,
            warnings=warnings,
        )