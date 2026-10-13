# Contributing to ai-dub-voice-studio

Thanks for wanting to help dub the world. This project is a Windows desktop
tool for AI-driven dubbing and translation voice generation — you feed it
audio, it transcribes, translates, and re-synthesizes in a target voice.

## Development setup

```
git clone https://github.com/<org>/ai-dub-voice-studio
cd ai-dub-voice-studio
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

Model weights are not committed. Run `python -m ai_dub.cli bootstrap-weights`
on first setup to pull the ASR and TTS checkpoints into `models/weights/`.

## Architecture

The codebase is service-oriented:

- `handlers/` — thin. Validate input, call a service, return. No business logic.
- `services/` — the meat. Orchestration, transcription, translation, synthesis.
- `adapters/` — platform edges. Windows audio devices, ONNX runtime, ffmpeg, GPU.
- `models/` — data models (pydantic). No I/O.
- `config/` — settings schemas and defaults.

If you're adding a feature, put logic in a service and expose it through a
handler. If you need to talk to the OS or an external binary, add an adapter.

## Style

- ruff + black, line length 100.
- Type hints required on all public functions. mypy strict on `services/` and `models/`.
- No blocking calls on the Qt main thread. Use `asyncio` or a QThread worker.

## Tests

```
pytest -q
pytest --cov=ai_dub services tests
```

Integration tests that touch real audio live under `tests/integration/` and
are skipped unless `AI_DUB_RUN_INTEGRATION=1`.

## Pull requests

- One feature per PR.
- Update `CHANGELOG.md` under `## Unreleased`.
- Include a sample input/output clip if the change affects synthesis quality.