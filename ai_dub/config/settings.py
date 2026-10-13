"""Runtime settings, loaded from config/default.yaml + env overrides."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StudioSettings(BaseSettings):
    """All tunables for the studio. Env vars override YAML, prefix AI_DUB_."""

    model_config = SettingsConfigDict(env_prefix="AI_DUB_", env_file=".env", extra="ignore")

    asr_model: str = "large-v3"
    asr_device: Literal["cuda", "cpu", "auto"] = "auto"
    asr_compute_type: str = "float16"

    tts_engine: Literal["xtts", "vits", "piper"] = "xtts"
    tts_sample_rate: int = 24000
    voice_profile_dir: Path = Path("voices")

    translation_provider: Literal["local_nllb", "libretranslate", "deepl"] = "local_nllb"
    translation_endpoint: str | None = None

    ffmpeg_path: str = "ffmpeg"
    render_dir: Path = Path("renders")
    max_workers: int = Field(default=4, ge=1, le=32)

    @classmethod
    def load(cls, path: Path | None = None) -> "StudioSettings":
        defaults = Path(__file__).with_name("default.yaml")
        data: dict = {}
        if defaults.exists():
            data = yaml.safe_load(defaults.read_text(encoding="utf-8")) or {}
        if path and path.exists():
            data = {**data, **(yaml.safe_load(path.read_text(encoding="utf-8")) or {})}
        return cls(**data)