"""ffmpeg/ffprobe adapter. Argument lists only — never shell strings."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


class FfmpegAdapter:
    @staticmethod
    def available_filters() -> list[str]:
        out = subprocess.run(
            ["ffmpeg", "-hide_banner", "-filters"],
            capture_output=True, text=True, check=True,
        )
        return [line.split()[1] for line in out.stdout.splitlines() if line.startswith(" ")]

    @staticmethod
    def probe_duration(media: Path) -> float:
        out = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json", str(media),
            ],
            capture_output=True, text=True, check=True,
        )
        return float(json.loads(out.stdout)["format"]["duration"])

    @staticmethod
    def mix_tracks(
        stems: list[Path], source: Path, out: Path, keep_background: bool = True
    ) -> Path:
        concat_list = out.with_suffix(".concat.txt")
        concat_list.write_text(
            "\n".join(f"file '{s.as_posix()}'" for s in stems), encoding="utf-8"
        )
        args = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat_list),
            "-i", str(source),
            "-filter_complex",
            "[0:a]volume=1.0[dub];[1:a]volume=0.25[bg];[dub][bg]amix=inputs=2:duration=longest[out]",
            "-map", "[out]", "-map", "0:v?",
            str(out),
        ]
        subprocess.run(args, check=True)
        concat_list.unlink(missing_ok=True)
        return out