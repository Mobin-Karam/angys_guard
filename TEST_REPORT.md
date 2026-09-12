# Laptop Guard v9.0.0 — Test report

Build date: 2026-09-12

## Automated validation

- Python compileall: PASS
- Pytest regression suite: 21/21 PASS
- Shell syntax checks: PASS
- Warning image asset checks: PASS
- RTL/LTR regression tests: PASS
- Exit-lock watchdog regression tests: PASS
- Persian TTS configuration/default tests: PASS
- Persian TTS documented async API integration test with a fake `PersianTTS`: PASS
- Persian TTS voice persistence test: PASS
- Credential/token literal scan: PASS

## TTS integration basis

Laptop Guard v9 integrates `py-persian-tts==3.0.2` through the documented `PersianTTS` API:

```python
PersianTTS(default_voice="man2", rate_limit=0.5)
await tts.speak_async(text, voice="man2", filename="output.wav")
await tts.shutdown()
```

The build environment does not have outbound package-network access, so it could not perform a live PyPI install or a live external TTS synthesis. The wrapper is regression-tested against the documented async API contract. On the target laptop, `./install.sh` installs the package and `./doctor.sh` verifies that it imports.

## Target-laptop checks

After installation run:

```bash
./doctor.sh
./run.sh
```

Then send these from Bale:

```text
/ttstest
/say سلام. این یک تست است.
/ttsvoices
/ttsmode on
```

The generated sound requires one local playback backend such as `ffplay`, `paplay`, `pw-play`, or `aplay`.
