"""Voice profile and synthesis request models."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class VoiceProfile(BaseModel):
    """A cloned or preset voice, backed by a speaker embedding + reference clip."""

    voice_id: str
    display_name: str
    lang: str = "multi"
    reference_wav: Path
    embedding_path: Path | None = None
    gender: Literal["male", "female", "neutral", "unknown"] = "unknown"
    tags: list[str] = Field(default_factory=list)

    def is_ready(self) -> bool:
        return self.reference_wav.exists()


class SynthesisRequest(BaseModel):
    """One TTS unit of work."""

    text: str
    voice_id: str
    lang: str
    target_duration_s: float | None = None
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    style: Literal["neutral", "narration", "dialogue"] = "neutral"