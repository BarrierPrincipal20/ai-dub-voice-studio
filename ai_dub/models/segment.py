"""Transcript and translation segment models."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    """A single timed utterance from the ASR stage."""

    index: int = Field(ge=0)
    start_s: float = Field(ge=0)
    end_s: float = Field(ge=0)
    text: str
    speaker: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

    @property
    def duration_s(self) -> float:
        return max(0.0, self.end_s - self.start_s)


class TranslatedSegment(BaseModel):
    """A transcript segment carried through translation."""

    source: TranscriptSegment
    target_text: str
    target_lang: str
    engine: str

    def stretched_for_dub(self, words_per_sec: float = 3.2) -> float:
        """Estimate duration needed to speak target_text at natural pace."""
        word_count = max(1, len(self.target_text.split()))
        return word_count / words_per_sec