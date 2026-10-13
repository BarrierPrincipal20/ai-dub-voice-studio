"""Handler for dub jobs coming from UI or CLI. Thin — no business logic."""
from __future__ import annotations

from pathlib import Path

from ai_dub.models.dub_job import DubJob, DubResult
from ai_dub.services.dub_pipeline import DubPipeline


class DubHandler:
    def __init__(self, pipeline: DubPipeline) -> None:
        self._pipeline = pipeline

    def submit(
        self,
        source: Path,
        target_lang: str,
        voice_id: str,
        keep_background: bool = True,
    ) -> DubResult:
        if not source.exists():
            raise FileNotFoundError(f"source media not found: {source}")
        if not target_lang or len(target_lang) < 2:
            raise ValueError("target_lang must be an ISO 639-1 code")

        job = DubJob(
            job_id=f"job-{source.stem}-{target_lang}",
            source_path=source,
            target_lang=target_lang,
            voice_id=voice_id,
            keep_background=keep_background,
        )
        return self._pipeline.run_sync(job.source_path, target_lang, voice_id, out_path=Path("renders") / f"{job.job_id}.wav")