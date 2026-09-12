# Bug triage and fixing playbook

Use this guide when something is broken, inconsistent, failing only on some
machines, reported in a GitHub issue, or discovered during testing. The goal is
to move from **symptom** to **reproducible cause** to **small verified fix**
without guessing across the entire codebase.

Read `AGENTS.md` first. Runtime changes also inherit `laptop_guard/AGENTS.md`;
test changes inherit `tests/AGENTS.md`.

## 1. Start with evidence, not code changes

Collect only the information needed to reproduce the problem. Do not copy real
bot tokens, chat IDs, stop PINs, captured media, or private user logs into issues,
prompts, tests, or commits.

Capture:

- exact user-visible symptom;
- expected behavior;
- command/action that triggered it;
- whether it happens every time;
- operating system / desktop session when relevant;
- Python version;
- provider mode (Bale/Telegram/local) when relevant;
- whether `./run.sh doctor` reports a missing required capability;
- recent sanitized event/status output;
- smallest traceback/error excerpt that identifies the failing path.

Useful first commands:

```bash
./run.sh status
./run.sh doctor
./run.sh events --limit 20
python --version
```

For a specific subsystem, use the existing manual checks:

```bash
./run.sh test camera
./run.sh test microphone
./run.sh test bot
./run.sh test screen
./run.sh test input
```

See `docs/TESTING.md` for target-device validation rules.

## 2. Classify the failure

Classifying the symptom reduces the search area.

| Symptom | Likely first area |
|---|---|
| App does not start / config error | `cli.py`, `runtime_config.py`, `config.py`, setup/doctor |
| Bot auth/pairing/send failure | provider/runtime API, token storage, pairing, network/proxy |
| Command ignored/wrong callback | authorization/dispatch, `FeatureManager`, feature module |
| Camera detection/recording failure | `camera_devices.py`, `camera.py`, OpenCV/system device access |
| Mouse/keyboard detection issue | `input_monitor.py`, evdev/pynput permissions/backend |
| Screenshot/screen video issue | `screen_capture.py`, Wayland/X11/compositor dependencies |
| Audio/TTS/intercom issue | audio/intercom/speech modules and local playback backend |
| Warning not visible / lock not executed | warning sequence, system actions, desktop session backend |
| Service/autostart problem | `service.py`, generated systemd user unit, config startup state |
| Wrong persisted state/events | `state.py`, `runtime_state.py`, events/storage |
| Failed-login alert issue | `features/failed_login.py`, journal access, filtering/deduplication |
| UI/RTL/chat problem | `chat_surface.py`, `chat_window.py`, `text_direction.py` |
| Test-only failure | changed module + failing test + fixture assumptions |

Use `docs/FILE_REFERENCE.md` for file ownership and `docs/SYSTEM_AUDIT.md` for
runtime flow and known boundaries.

## 3. Reproduce the smallest failing case

Do not debug the full application when a smaller component can reproduce the
problem.

Examples:

- configuration bug -> load/save one temporary config in a unit test;
- callback parsing bug -> call the handler/manager with the failing payload;
- provider serialization bug -> fake HTTP/provider object;
- state bug -> temporary `RuntimeStateStore`/event store;
- camera capability bug -> fake detection result rather than real camera in CI;
- service command bug -> mock subprocess and assert the argument list;
- migration bug -> load a minimal old-format fixture.

The preferred fix loop is:

```text
make it reproducible
        |
        v
write/locate failing regression test
        |
        v
trace exact owning path
        |
        v
smallest root-cause fix
        |
        v
targeted tests
        |
        v
broader verification + review
```

If you cannot reproduce the bug, do not make speculative broad changes. Improve
logging/diagnostics or ask for the one missing piece of evidence that would
separate the likely causes.

## 4. Trace the cause using the repository docs

Use the documentation as a navigation system:

1. `docs/README.md` — choose the relevant documentation area.
2. `docs/FILE_REFERENCE.md` — identify the module that owns the behavior.
3. `docs/SYSTEM_AUDIT.md` — understand the current runtime/data/control flow.
4. `docs/CONFIGURATION.md` — verify defaults, persistence, secrets, migration.
5. `docs/SECURITY.md` — check trust/authorization/privacy requirements.
6. `docs/EXTENDING.md` / `docs/FEATURE_LIFECYCLE.md` — understand feature
   registration and safe change/removal patterns.
7. `docs/TESTING.md` — find existing test and manual verification boundaries.
8. `docs/AI_AGENT_WORKFLOW.md` — choose the correct agent/skill workflow.

For broad cross-file investigation, use `graphify-out/graph.json` only as a
navigation aid if present; current source remains authoritative.

## 5. Read failures in layers

A visible error may be several layers away from the actual cause. Trace it from
outside inward.

### Startup/configuration

```text
run.sh
 -> laptop_guard.cli
 -> runtime_config / config
 -> LaptopGuard construction
```

Check whether the failure is missing configuration, invalid persisted data,
permissions, missing dependency, provider validation, or an actual code defect.
Expected configuration failures should become actionable user messages, not raw
tracebacks.

### Remote command/callback

```text
provider update
 -> owner authorization
 -> command/callback dispatch
 -> FeatureManager or existing command path
 -> feature/service
 -> reply/event/state
```

Verify authorization before handler logic. Never "fix" a command by bypassing an
owner/confirmation check.

### Hardware/desktop behavior

Separate these questions:

1. Is the Python logic correct?
2. Is the backend installed?
3. Does the current user have permission?
4. Does the desktop/compositor expose the capability?
5. Is the target device/session different from CI?

A unit test can prove #1 but not necessarily #2–#5.

## 6. Convert the bug into a regression test

Before or alongside the fix, add a test that fails for the reported behavior and
passes after the root-cause change.

A good regression test:

- reproduces the smallest bad input/state;
- does not require real credentials/private media;
- tests observable behavior, not internal implementation trivia;
- covers the failure/denial path when security-sensitive;
- uses temporary files/paths and fake providers/hardware;
- has a name that explains the bug scenario.

If the bug is only reproducible on a real Wayland/X11 session, camera, microphone,
or systemd environment, add the strongest unit coverage possible and record the
remaining manual validation separately.

## 7. Fix the root cause, not the symptom

Common bad fixes to avoid:

- catching `Exception` and silently continuing when state is corrupted;
- disabling a security/authorization check to make an action work;
- retrying forever instead of bounding retries/timeouts;
- adding a second special-case code path around the owning abstraction;
- logging secrets/full provider payloads to diagnose auth problems;
- replacing atomic persisted state with ad-hoc writes;
- using shell interpolation for convenience;
- making optional hardware failure crash the whole guard unnecessarily;
- deleting historical events/config without a migration decision.

Prefer a fix in the module that owns the invariant. If several callers are wrong
in the same way, repair the shared boundary rather than each caller separately.

## 8. Determine severity and GitHub handling

Use a normal GitHub issue for reproducible product defects that do not disclose a
vulnerability.

Suggested priority:

- **P0** — credential exposure, auth bypass, destructive/unsafe remote behavior,
  severe privacy issue, unusable startup for all supported users;
- **P1** — core protection/alert/lock/setup feature broken, major regression;
- **P2** — partial capability failure with workaround, platform-specific bug;
- **P3** — cosmetic/docs/minor diagnostics issue.

Security vulnerabilities should follow `SECURITY.md`, not a normal issue.

An issue should contain:

```text
Problem:
Expected:
Actual:
Reproduction steps:
Environment:
Doctor/status evidence (sanitized):
Suspected area (if known):
Acceptance criteria:
Manual validation required:
```

Do not paste secrets or private evidence.

## 9. AI-agent workflows for finding and fixing bugs

### Unknown cause

Use the read-only architect first:

```text
Have architect investigate this bug without editing code. Use
BUG_TRIAGE_AND_FIXING.md, FILE_REFERENCE.md, SYSTEM_AUDIT.md, TESTING.md, and the
actual failing test/error. Return the most likely root cause, exact paths/symbols,
a minimal reproduction plan, and the smallest safe fix plan.
```

### Reproducible bug

```text
Use implementer to reproduce and fix this bug. Add a failing regression test
first where practical. Keep the patch limited to the owning abstraction. Then
have tester run targeted and full applicable verification, and reviewer inspect
the final diff.
```

### Security-sensitive bug

```text
Have architect trace the bug and trust boundary first. Then use implementer for
the bounded fix, tester for regression coverage, and security_reviewer to review
authorization, secrets, capture/privacy, network, subprocess, and OS-control
impact before completion.
```

### Existing GitHub issue

```text
$issue-to-pr implement issue #<number>. Start by reproducing the issue using
BUG_TRIAGE_AND_FIXING.md. Do not merge until the regression test and required
checks are green.
```

### CI failure

```text
Have tester triage the failing CI job. Identify whether it is a code regression,
test/fixture bug, packaging/dependency problem, or environment-specific failure.
Return the smallest diagnostic/fix; do not make unrelated changes.
```

## 10. Verification after the fix

Run focused tests first. Then run the applicable full checks described in
`docs/TESTING.md`, normally including:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q laptop_guard tests
bash -n install.sh run.sh doctor.sh repair-opencv.sh
.venv/bin/python -m pip check
git diff --check
```

Also rerun the exact user reproduction steps. If hardware/session/provider
behavior is involved, list and perform the required target-device checks instead
of claiming the unit suite proves them.

## 11. Bug-fix completion checklist

- [ ] problem reproduced or evidence is sufficient to identify the cause;
- [ ] owning module/call path identified;
- [ ] no secret/private evidence was copied into artifacts;
- [ ] regression test added/updated where practical;
- [ ] root cause fixed rather than hidden;
- [ ] authorization/privacy behavior is at least as strict as before;
- [ ] targeted test passes;
- [ ] applicable full checks pass;
- [ ] original reproduction steps now pass;
- [ ] required target-device validation recorded;
- [ ] user-facing diagnostics/docs updated if behavior changed;
- [ ] reviewer/security review completed when appropriate.
