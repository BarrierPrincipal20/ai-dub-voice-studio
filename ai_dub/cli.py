"""Headless CLI for batch dubbing. Mirrors the desktop pipeline."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ai_dub.adapters.ffmpeg_adapter import FfmpegAdapter
from ai_dub.config.settings import StudioSettings
from ai_dub.services.dub_pipeline import DubPipeline
from ai_dub.services.translation_service import TranslationService
from ai_dub.services.transcription_service import TranscriptionService
from ai_dub.services.voice_synthesis_service import VoiceSynthesisService

app = typer.Typer(help="AI dubbing / translation voice generator")
console = Console()


@app.command()
def dub(
    source: Path = typer.Argument(..., exists=True, dir_okay=False),
    target_lang: str = typer.Option("es", "--to", help="ISO 639-1 target language"),
    voice: str = typer.Option("default_female", "--voice"),
    out: Path = typer.Option(Path("renders/dub.wav"), "--out"),
) -> None:
    """Dub a single media file end to end."""
    settings = StudioSettings.load()
    pipeline = DubPipeline(
        transcription=TranscriptionService(settings),
        translation=TranslationService(settings),
        synthesis=VoiceSynthesisService(settings),
    )
    result = pipeline.run_sync(source, target_lang=target_lang, voice_id=voice, out_path=out)
    console.print(f"[green]rendered[/green] {result.out_path} ({result.duration_s:.1f}s)")


@app.command("bootstrap-weights")
def bootstrap_weights() -> None:
    """Download ASR + TTS checkpoints into models/weights/."""
    from ai_dub.services.weight_bootstrap import WeightBootstrap

    WeightBootstrap().run()


@app.command()
def devices() -> None:
    """List audio devices the Windows adapter can see."""
    console.print(FfmpegAdapter.available_filters())


if __name__ == "__main__":
    app()