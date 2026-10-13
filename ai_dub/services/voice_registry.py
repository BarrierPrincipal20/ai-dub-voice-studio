"""Voice profile registry. Filesystem-backed, one folder per voice."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from ai_dub.models.voice import VoiceProfile


class VoiceRegistry:
    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def list_all(self) -> list[VoiceProfile]:
        profiles: list[VoiceProfile] = []
        for manifest in self._root.glob("*/profile.json"):
            profiles.append(VoiceProfile.model_validate_json(manifest.read_text(encoding="utf-8")))
        return sorted(profiles, key=lambda p: p.voice_id)

    def register(self, voice_id: str, reference_wav: Path, lang: str = "multi") -> VoiceProfile:
        dest = self._root / voice_id
        dest.mkdir(parents=True, exist_ok=True)
        target = dest / "reference.wav"
        shutil.copy2(reference_wav, target)
        profile = VoiceProfile(
            voice_id=voice_id,
            display_name=voice_id.replace("_", " ").title(),
            lang=lang,
            reference_wav=target,
        )
        (dest / "profile.json").write_text(profile.model_dump_json(indent=2), encoding="utf-8")
        return profile

    def delete(self, voice_id: str) -> None:
        dest = self._root / voice_id
        if dest.exists():
            shutil.rmtree(dest)