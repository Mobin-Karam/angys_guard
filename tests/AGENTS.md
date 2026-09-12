# Test instructions

These rules apply under `tests/` in addition to the root `AGENTS.md`.

- Keep tests deterministic, offline, and free of real credentials.
- Mock/fake Telegram, Bale, camera, microphone, screen, input, systemd, journal,
  and OS-lock integrations unless a test is explicitly a target-device test.
- Never require a real password, bot token, chat ID, captured image/video, or
  private user data in fixtures.
- Prefer focused regression tests next to the behavior being changed.
- Test authorization denial and unavailable/error paths for security-sensitive
  behavior, not only success paths.
- Avoid sleeps when state/time can be injected or monkeypatched.
- Keep temporary config/state under pytest temporary directories.
- Verify secret-free serialization and restrictive permissions where applicable.

Standard suite:

```bash
.venv/bin/python -m pytest -q
```

When debugging, run the smallest failing node/file first, then rerun the full
suite before completion.
