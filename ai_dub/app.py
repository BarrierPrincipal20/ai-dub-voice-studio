"""Qt application bootstrap. Wires services into the main window."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ai_dub.config.settings import StudioSettings
from ai_dub.services.dub_pipeline import DubPipeline
from ai_dub.services.translation_service import TranslationService
from ai_dub.services.transcription_service import TranscriptionService
from ai_dub.services.voice_synthesis_service import VoiceSynthesisService
from ai_dub.ui.main_window import MainWindow


def build_pipeline(settings: StudioSettings) -> DubPipeline:
    return DubPipeline(
        transcription=TranscriptionService(settings),
        translation=TranslationService(settings),
        synthesis=VoiceSynthesisService(settings),
    )


def main() -> int:
    settings = StudioSettings.load()
    app = QApplication(sys.argv)
    app.setApplicationName("AI Dub Voice Studio")
    app.setOrganizationName("ai-dub-voice-studio")

    pipeline = build_pipeline(settings)
    window = MainWindow(pipeline=pipeline, settings=settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())