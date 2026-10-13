"""Windows WASAPI capture/loopback via sounddevice."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf


class WindowsAudioAdapter:
    @