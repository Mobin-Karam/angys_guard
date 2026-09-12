# Testing and validation

Use this document after feature work, bug fixes, configuration changes, AI-workspace
changes, and release preparation.

For the workflow before testing:

- feature add/change/remove/fix: `docs/FEATURE_LIFECYCLE.md`;
- bug/issue investigation and repair: `docs/BUG_TRIAGE_AND_FIXING.md`;
- AI-assisted verification: `$test-and-verify` in `docs/AI_AGENT_WORKFLOW.md`.

## Progressive verification

Do not start with the broadest/noisiest command when a focused check can identify
the problem faster.

Recommended order:

1. reproduce the reported behavior or run the closest focused test;
2. run the changed module's test file(s);
3. run the full automated suite;
4. compile/check shell/package consistency;
5. rerun the exact user reproduction;
6. perform target-device checks for hardware/session/provider behavior.

## Automated suite

Install the test extra and run pytest:

```bash
.venv/bin/pip install -e '.[test]'
.venv/bin/python -m pytest -q
```

The suite covers configuration defaults/migrations, secret-free config round
trips, setup checkpoints, provider/Bale request serialization, feature registry
conflicts/lifecycle, runtime transport/state, event/outbox persistence,
service/autostart behavior, failed-login parsing/deduplication, camera capability
fallbacks, input privacy, screen parsers, warning behavior/assets, Persian TTS,
RTL/LTR direction, stop-PIN hashing, app allowlisting, chat persistence, local API
construction, AI workspace configuration, Codex hook policy, and documentation
link/index integrity.

### Documentation regression checks

`tests/test_documentation_links.py` verifies that:

- local Markdown links in repository/docs/AI instruction files resolve to real
  files/directories;
- `docs/README.md` links the canonical maintenance guides;
- root `AGENTS.md` routes AI work to the canonical maintenance guides.

When you add/rename/remove a documentation file, update links before merging.
Do not bypass this check by converting useful local links into plain text.

## Standard completion checks

For normal Python/runtime changes, the applicable completion set is:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q laptop_guard tests
bash -n install.sh run.sh doctor.sh repair-opencv.sh
.venv/bin/python -m pip check
git diff --check
```

Use focused subsets first when debugging. A failure in one of these commands
should be investigated rather than hidden or skipped.

## Regression-test rule for bug fixes

A reproducible bug should normally gain a regression test that fails before the
fix and passes after it.

Prefer the smallest deterministic reproduction:

- config bug -> temporary config fixture;
- command/callback bug -> direct manager/handler input;
- provider bug -> fake provider/HTTP boundary;
- state/event bug -> temporary state/database path;
- service/process bug -> mock subprocess argument lists;
- hardware capability bug -> fake backend/capability result.

Do not put real credentials, passwords, private media, or personal logs into test
fixtures.

If the bug cannot be represented fully in CI because it depends on a real Linux
desktop/hardware/provider, add the strongest unit coverage possible and record
the remaining manual validation explicitly.

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
systemd service after login when the changed area depends on them.

These surfaces depend on the desktop session, hardware, permissions, and external
provider services and are not proven by unit tests.

After `./run.sh doctor`, failed-login monitoring may be manually validated with a
controlled authentication failure on the target machine, confirming exactly one
sanitized owner alert plus the expected event. Never automate this check using a
real password.

## Environment-specific validation

When a change touches screen/input/capture or service behavior, record the target
environment separately:

```text
OS/distribution:
Python:
Desktop/session (GNOME/KDE/etc.):
X11 or Wayland:
Camera/microphone backend:
Provider mode:
Relevant permissions:
Result:
```

A pass on X11 does not prove Wayland behavior, and a passing unit suite does not
prove OS lock, compositor capture, camera permissions, or systemd login-session
behavior.

## CI failure triage

When GitHub Actions fails:

1. identify the exact job, step, and first meaningful failing test/error;
2. determine whether the failure is product code, test/fixture, dependency,
   Python-version compatibility, packaging, or environment/flakiness;
3. reproduce locally or with the smallest equivalent test when possible;
4. fix the cause rather than weakening/skipping the check;
5. rerun the failed focused test before the full suite.

For Codex:

```text
Have tester triage the failing CI job using docs/TESTING.md and
BUG_TRIAGE_AND_FIXING.md. Return the exact failing step/test, classification,
root-cause evidence, and smallest next fix/diagnostic. Do not change unrelated
code.
```

## Verification report format

Record what was actually proven:

```text
Focused tests:
Full pytest:
Compile/shell/pip/diff checks:
Original reproduction:
GitHub CI:
Repository Safety:
Manual target-device checks:
Not tested / still required:
```

Do not state that camera, microphone, lock, provider, Wayland/X11, or systemd
behavior passed when only unit tests ran.
