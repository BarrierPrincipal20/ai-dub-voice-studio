"""Top-level job and result models."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from ai_dub.models.segment import TranslatedSegment


class DubJob(BaseModel):
    """A queued dubbing task."""

    job_id: str
    source_path: Path
    target_lang: str
    voice_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    keep_background: bool = True
    duck_db: float = -12.0


class DubResult(BaseModel):
    """Outcome of a completed dub."""

    job_id: str
    out_path: Path
    duration_s: float
    segments: list[TranslatedSegment] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)