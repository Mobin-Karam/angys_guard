# Testing and validation

## Automated suite

Install the test extra and run pytest:

```bash
.venv/bin/pip install -e '.[test]'
.venv/bin/python -m pytest -q
```

The current suite covers configuration defaults/migrations, secret-free config
round trips, setup checkpoints, Bale request serialization, camera capability
fallbacks, event/state persistence, offline outbox behavior, profile defaults,
local API construction, app allowlisting, chat files, input privacy, native
screen parsers, warning launch behavior, warning media metadata, Persian TTS,
RTL/LTR direction, stop-PIN hashing, and one-time watchdog authorization.

Audit validation on 2026-09-12 initially covered 52 tests. The modularization
pass brings the current suite to 76 tests and adds coverage for feature
conflicts/lifecycle, runtime transport selection,
proxy policy, shared persistent state, event mirroring, and CLI exit codes.
It also covers autostart command construction and failed-login parsing,
filtering, notification, and burst deduplication.

- 52 current tests passed using a local fixture-compatible runner.
- Python compile/import checks passed.
- `bash -n` passed for `install.sh`, `run.sh`, and `doctor.sh`.
- `pip check` reported no broken installed requirements.
- Doctor returned success on the inspected machine.
- The warning MP4 was verified as 1920×1080, 30 fps, 150 frames / 5 seconds.
- `git diff --check` passed.

A normal pytest invocation and isolated wheel build could not be rerun in that
audit environment because pytest/setuptools/build were missing and package
network access was unavailable. Package metadata now declares the test extra
and warning media package data, but a clean wheel-install smoke test remains
recommended.

## Target-device checks

```bash
./run.sh doctor
./run.sh test camera
./run.sh test microphone
./run.sh test bot
./run.sh test screen
./run.sh test input
```

Also validate an armed intrusion, fullscreen player visibility/focus, actual OS
lock, Ctrl+C PIN plus owner approval, rejection/timeout behavior, abrupt-process
watchdog locking, Bale media upload/download, Persian speech playback, and the
systemd service after login. These surfaces depend on the desktop session,
hardware, permissions, and external Bale service and are not proven by unit
tests.

After `./run.sh doctor`, intentionally enter one wrong desktop password and
confirm exactly one Bale alert plus a `failed_login` event. Never automate this
check using a real password.

Historical `.legacy.py` copies were removed because their behavior is covered by
the current collected migration/configuration/chat tests.
