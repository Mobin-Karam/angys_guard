---
name: test-and-verify
description: Select and run Laptop Guard verification after code or configuration changes. Use when validating a fix/feature, diagnosing failures, preparing a PR, or deciding whether work is complete.
---

# Test and verify

Use progressive verification and `docs/GRAPHIFY_NAVIGATION.md`.

1. Check Graphify freshness and use it to map changed/failing production symbols
   to the closest tests, fixtures, config/state/storage, and failure boundaries.
2. Confirm the selected tests in current source; do not load raw graph.json.
3. Run focused graph-identified tests first, for example:

   ```bash
   .venv/bin/python -m pytest -q tests/test_config.py
   ```

4. For a normal runtime/code change, finish with applicable project checks:

   ```bash
   .venv/bin/python -m pytest -q
   .venv/bin/python -m compileall -q laptop_guard tests
   bash -n install.sh run.sh doctor.sh repair-opencv.sh
   .venv/bin/python -m pip check
   git diff --check
   ```

5. Never use real tokens/passwords/private media in tests. Keep provider/hardware
   tests mocked/fake unless explicitly performing target-device checks.
6. If a command fails, report exit status, failing tests/checks, relevant error
   excerpt, likely cause, and the next smallest diagnostic.
7. Consult `docs/TESTING.md` and list manual validation for affected camera,
   microphone, screen/input, Wayland/X11, OS lock, systemd/autostart, and live
   Telegram/Bale behavior.
8. Do not claim hardware/provider behavior passed when only unit tests ran.
9. Report Graphify freshness and refresh the graph after material relationship
   changes when available.
