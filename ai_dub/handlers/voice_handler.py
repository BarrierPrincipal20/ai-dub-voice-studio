"""Handler for voice profile operations."""
from __future__ import annotations

from pathlib import Path

from ai_dub.models.voice import VoiceProfile
from ai_dub.services.voice_registry import VoiceRegistry


class VoiceHandler:
    def __init__(self, registry: VoiceRegistry) -> None:
        self._registry = registry

    def list_profiles(self) -> list[VoiceProfile]:
        return self._registry.list_all()

    def register(self, voice_id: str, reference_wav: Path, lang: str = "multi") -> VoiceProfile:
        if not reference_wav.exists():
            raise FileNotFoundError(f"reference wav missing: {reference_wav}")
        if reference_wav.stat().st_size < 16_000:
            raise ValueError("reference clip too short (<0.5s)")
        return self._registry.register(voice_id=voice_id, reference_wav=reference_wav, lang=lang)

    def delete(self, voice_id: str) -> None:
        self._registry.delete(voice_id)