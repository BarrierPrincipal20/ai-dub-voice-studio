# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.6.x   | yes       |
| 0.5.x   | security fixes only |

## Reporting a vulnerability

Open a private security advisory on GitHub or email
security@ai-dub-voice-studio.dev. Do not open a public issue for
vulnerabilities involving:

- Arbitrary code execution via a malicious model checkpoint (pickle /
  torch.load paths).
- Path traversal in the project file loader (`*.dubproj`).
- Command injection through ffmpeg argument construction.
- SSRF via the optional cloud-translation adapter.

We aim to acknowledge within 72 hours.

## Threat model notes

The tool loads user-supplied audio and model files. Two areas get scrutiny:

1. **Checkpoint loading.** We default to `weights_only=True` for
   `torch.load`. Never disable this in a release build. ONNX checkpoints
   are loaded through `onnxruntime`, which does not execute arbitrary code.
2. **Subprocess calls.** All ffmpeg invocations go through
   `adapters/ffmpeg_adapter.py`, which builds argument lists, never shell
   strings. If you find a `shell=True` anywhere, that's a bug — file it.

## Disclaimers

This is a hobbyist/educational tool. Voice cloning target voices is the
user's responsibility — get consent from anyone whose voice you clone.
Output is provided "as is", no warranty.