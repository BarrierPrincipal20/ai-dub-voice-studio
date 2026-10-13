"""Pulls ASR/TTS checkpoints into models/weights/ on first run."""
from __future__ import annotations

from pathlib import Path

import httpx
from rich.progress import Progress

_CHECKPOINTS = {
    "xtts_v2": "https://huggingface.co/coqui/XTTS-v2/resolve/main/model.pth",
    "nllb_600m": "https://huggingface.co/facebook/nllb-200-distilled-600M/resolve/main/pytorch_model.bin",
}


class WeightBootstrap:
    def __init__(self, dest: Path = Path("models/weights")) -> None:
        self._dest = dest

    def run(self) -> None:
        self._dest.mkdir(parents=True, exist_ok=True)
        with Progress() as progress:
            for name, url in _CHECKPOINTS.items():
                target = self._dest / f"{name}.bin"
                if target.exists():
                    continue
                task = progress.add_task(f"[cyan]{name}", total=None)
                with httpx.stream("GET", url, follow_redirects=True, timeout=None) as resp:
                    resp.raise_for_status()
                    with target.open("wb") as fh:
                        for chunk in resp.iter_bytes(1 << 20):
                            fh.write(chunk)
                progress.update(task, completed=True)