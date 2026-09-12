---
name: test-and-verify
description: Select and run Laptop Guard verification after code or configuration changes. Use when validating a fix/feature, diagnosing failures, preparing a PR, or deciding whether work is complete.
---

# Test and verify

Use progressive verification. Do not start with the noisiest/fullest command if a
focused test can fail faster.

1. Identify changed modules and the closest relevant tests.
2. Run focused tests first, for example:

   ```bash
   .venv/bin/python -m pytest -q tests/test_config.py
   ```

3. For a normal runtime/code change, finish with the applicable project checks:

   ```bash
   .venv/bin/python -m pytest -q
   .venv/bin/python -m compileall -q laptop_guard tests
   bash -n install.sh run.sh doctor.sh repair-opencv.sh
   .venv/bin/python -m pip check
   git diff --check
   ```

4. Never use real tokens/passwords/private media in tests. Keep provider/hardware
   tests mocked or fake unless the user explicitly performs target-device checks.
5. If a command fails, report its exit status, failing tests/checks, relevant error
   excerpt, likely cause, and the next smallest diagnostic.
6. Consult `docs/TESTING.md` and list required manual validation for camera,
   microphone, screen/input, Wayland/X11, OS lock, systemd/autostart, and live
   Telegram/Bale behavior affected by the change.
7. Do not claim hardware/provider behavior passed when only unit tests ran.
