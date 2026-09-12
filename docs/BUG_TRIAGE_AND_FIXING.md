# Bug triage and fixing playbook

Use this guide when something is broken, inconsistent, failing only on some
machines, reported in a GitHub issue, or discovered during testing. The goal is
to move from **symptom** to **reproducible cause** to **small verified fix**
without guessing across the entire codebase.

Read `AGENTS.md` and `docs/GRAPHIFY_NAVIGATION.md` first. Runtime changes also
inherit `laptop_guard/AGENTS.md`; test changes inherit `tests/AGENTS.md`.

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

## 2. Map the symptom with Graphify before broad searching

After collecting the symptom/error/entry point, check Graphify freshness and ask
the smallest relationship question that can reduce the search area:

```bash
graphify query "where is <symptom/command/behavior> handled?"
graphify explain "<symbol from traceback/error>"
graphify query "what tests cover <symbol/behavior>?"
graphify path "<entry point>" "<suspected state/store/side effect>"
```

Use Graphify to identify likely owners, callers/dependencies, config/state/storage,
side effects, and tests. Then open only those source/test ranges and confirm them.
Do not load the complete `graphify-out/graph.json` into context.

If the graph is stale and can be refreshed, run `graphify update .` first. If it
cannot be used, keep direct fallback search narrow and state the reason.

## 3. Classify the failure

Use the Graphify map plus the symptom class to narrow the subsystem:

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

`docs/FILE_REFERENCE.md` is the curated ownership map; use it after Graphify when
ownership needs human-maintained context. `docs/SYSTEM_AUDIT.md` documents current
runtime evidence and known boundaries.

## 4. Reproduce the smallest failing case

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
Graphify map
   -> make it reproducible
   -> locate/write failing regression test
   -> confirm exact owning path
   -> smallest root-cause fix
   -> targeted tests
   -> broader verification + review
   -> refresh Graphify after material relationship changes
```

If you cannot reproduce the bug, do not make speculative broad changes. Improve
logging/diagnostics or ask for the one missing piece of evidence that would
separate the likely causes.

## 5. Use canonical docs only after navigation is narrowed

Graphify finds the live relationship neighborhood. Then use canonical docs for
the relevant rules/intent:

1. `docs/FILE_REFERENCE.md` — curated module ownership/context.
2. `docs/SYSTEM_AUDIT.md` — current runtime/data/control-flow evidence.
3. `docs/ARCHITECTURE.md` / `docs/architecture/` — target boundaries for refactors.
4. `docs/CONFIGURATION.md` — defaults, persistence, secrets, migration.
5. `docs/SECURITY.md` — trust/authorization/privacy requirements.
6. `docs/EXTENDING.md` / `docs/FEATURE_LIFECYCLE.md` — feature ownership/change rules.
7. `docs/TESTING.md` — test/manual verification boundaries.
8. `docs/AI_AGENT_WORKFLOW.md` — agent/skill handoffs.

Current source remains authoritative if generated Graphify output or older docs
disagree with actual behavior.

## 6. Read failures in layers

A visible error may be several layers away from the actual cause. Use Graphify
paths to guide the layer trace, then verify each important transition in source.

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

## 7. Convert the bug into a regression test

Use Graphify to identify existing tests connected to the owning symbol/behavior.
Before or alongside the fix, add a test that fails for the reported behavior and
passes after the root-cause change.

A good regression test:

- reproduces the smallest bad input/state;
- does not require real credentials/private media;
- tests observable behavior, not implementation trivia;
- covers failure/denial when security-sensitive;
- uses temporary files/paths and fake providers/hardware;
- has a name that explains the bug scenario.

If only reproducible on real Wayland/X11, camera, microphone, or systemd, add the
strongest unit coverage possible and record manual validation separately.

## 8. Fix the root cause, not the symptom

Common bad fixes to avoid:

- catching `Exception` and silently continuing when state is corrupted;
- disabling a security/authorization check to make an action work;
- retrying forever instead of bounding retries/timeouts;
- adding a second special-case path around the owning abstraction;
- logging secrets/full provider payloads to diagnose auth problems;
- replacing atomic persisted state with ad-hoc writes;
- using shell interpolation for convenience;
- making optional hardware failure crash the whole guard unnecessarily;
- deleting historical events/config without a migration decision.

Prefer a fix in the module that owns the invariant. If several callers are wrong
in the same way, repair the shared boundary rather than each caller separately.

## 9. Determine severity and GitHub handling

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
Graphify owning path / relevant nodes (if available):
Acceptance criteria:
Manual validation required:
```

Do not paste secrets or private evidence.

## 10. AI-agent workflows for finding and fixing bugs

### Unknown cause

```text
Have navigator map the symptom/error to likely owners, callers/dependencies, and
tests with Graphify. Then have tester reproduce it. Have architect reason about
root cause using that graph/source evidence. Do not edit until sufficiently narrowed.
```

### Reproducible bug

```text
Use Graphify to confirm the owner and connected tests. Use implementer to add or
locate a failing regression test and make the smallest root-cause fix. Then tester
runs targeted/full checks and reviewer inspects graph-identified blast radius.
```

### Security-sensitive bug

```text
Have navigator/architect trace the failing entry point to authorization/secrets/
capture/network/process/OS-control boundaries. Implement the bounded fix, have
tester verify success and denial paths, then security_reviewer confirm trust-boundary
behavior using graph paths plus source verification.
```

### Existing GitHub issue

```text
$issue-to-pr implement issue #<number>. The skill must Graphify-map the issue to
code/tests/docs before implementation and keep the acceptance criteria visible.
```

### CI failure

```text
Have tester use Graphify to connect the failing test/job to production modules and
dependencies, classify code vs fixture/environment/package failure, and return the
smallest diagnostic/fix.
```

## 11. Verification after the fix

Run focused graph-identified tests first. Then run applicable full checks from
`docs/TESTING.md`, normally including:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q laptop_guard tests
bash -n install.sh run.sh doctor.sh repair-opencv.sh
.venv/bin/python -m pip check
git diff --check
```

Also rerun the exact user reproduction. If hardware/session/provider behavior is
involved, perform required target-device checks instead of claiming unit tests
prove them.

Refresh Graphify after material code/docs relationship changes when the tool is
available.

## 12. Bug-fix completion checklist

- [ ] Graphify freshness checked and owning neighborhood mapped, or fallback reason recorded;
- [ ] problem reproduced or evidence sufficient to identify cause;
- [ ] owning module/call path confirmed in current source;
- [ ] no secret/private evidence copied into artifacts;
- [ ] regression test added/updated where practical;
- [ ] root cause fixed rather than hidden;
- [ ] authorization/privacy at least as strict as before;
- [ ] targeted test passes;
- [ ] applicable full checks pass;
- [ ] original reproduction passes;
- [ ] target-device validation recorded;
- [ ] user-facing diagnostics/docs updated if behavior changed;
- [ ] Graphify refreshed after material relationship changes when possible;
- [ ] reviewer/security review completed when appropriate.
