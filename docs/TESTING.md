# Testing and validation

Use this document after feature work, bug fixes, configuration changes, AI-workspace
changes, Graphify/navigation changes, repository-presentation changes, and release
preparation.

For the workflow before testing:

- repository discovery: `docs/GRAPHIFY_NAVIGATION.md`;
- feature add/change/remove/fix: `docs/FEATURE_LIFECYCLE.md`;
- bug/issue investigation and repair: `docs/BUG_TRIAGE_AND_FIXING.md`;
- README/About/version/repository presentation: `docs/README_MAINTENANCE.md`;
- production release qualification: `docs/RELEASE_CHECKLIST.md`;
- AI-assisted verification: `$test-and-verify` in `docs/AI_AGENT_WORKFLOW.md`.

## Graphify-guided test selection

Before scanning the test suite broadly, check Graphify freshness and use the graph
to find tests connected to the changed/failing symbol or behavior:

```bash
graphify query "what tests cover <symbol or behavior>?"
graphify path "<production symbol>" "<test symbol>"
graphify explain "<production or test symbol>"
```

Then inspect/run only the relevant current tests first. Graphify chooses the
starting scope; the current test/source files remain authoritative. If Graphify is
stale and available, refresh with `graphify update .`; if it cannot be used, use a
narrow fallback search and record why.

Never load the complete `graphify-out/graph.json` into AI/chat context just to
select tests.

## Progressive verification

Do not start with the broadest/noisiest command when a focused check can identify
the problem faster.

Recommended order:

1. Graphify-map the changed/failing behavior to connected tests;
2. reproduce the reported behavior or run the closest focused test;
3. run the changed module's nearby test file(s);
4. run repository presentation/policy tests when the changed surface affects them;
5. run the full automated suite;
6. compile/check shell/package consistency;
7. rerun the exact user reproduction;
8. perform target-device checks for hardware/session/provider behavior;
9. refresh Graphify after material source/docs relationship changes when available.

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
construction, AI workspace configuration, Codex hook policy, Graphify-first
navigation policy, repository-presentation consistency, and documentation
link/index integrity.

### First-run and release regression coverage

`tests/test_first_run_regression.py` exercises a complete first-run wizard in
local-only mode using temporary configuration paths and mocked hardware/systemd
boundaries. It also exercises provider validation and owner-pairing behavior with
fake provider responses only. No live Bale/Telegram token, real chat ID, camera,
microphone, desktop session, journal, or systemd instance is required.

The first-run regression verifies that:

- setup reaches a complete checkpoint and can be loaded back from disk;
- config and setup-progress files are owner-only (`0600`) and the config
  directory is owner-only (`0700`);
- local mode creates no secrets file;
- mocked camera/audio selections survive persistence;
- provider credentials used in tests are explicit test-only strings and are not
  printed by the setup flow.

`tests/test_service.py` protects systemd user-unit generation, incomplete-setup
refusal, autostart persistence, and uninstall/reload behavior using mocked
subprocess calls. `tests/test_cli.py` smoke-parses every supported CLI
subcommand so command registration regressions fail in CI.

GitHub Actions runs the full suite on Python 3.11, 3.12, and 3.13 for every push
and for pull requests targeting `main`. The final **Release gate** job depends
on the entire supported-Python matrix and fails unless all matrix jobs succeed.
Configure branch protection/rulesets to require **Release gate** plus
**repository-safety** before merging to `main`; repository-admin settings cannot
be guaranteed by workflow files alone.

### Documentation and AI-navigation regression checks

`tests/test_documentation_links.py` verifies local Markdown links/index routing.

`tests/test_graphify_navigation_policy.py` verifies that:

- `docs/GRAPHIFY_NAVIGATION.md` remains the canonical Graphify workflow;
- root/scoped/cross-tool AI instruction files retain Graphify-first routing;
- Codex keeps the `navigator` agent and Graphify-aware specialist roles;
- SessionStart retains Graphify freshness context;
- the Graphify skill/prompt stay registered;
- core human maintenance guides retain the canonical navigation link;
- generated `GRAPH_REPORT.md` continues to record the build commit required for
  freshness checks.

The policy test intentionally does not claim the checked-in graph is fresh. Graph
freshness is an operational comparison between the report's build commit and the
working repository.

### Repository-presentation regression checks

`tests/test_repository_presentation.py` protects the repository landing surface.
It verifies that:

- root `README.md` is the package README referenced by `pyproject.toml`;
- the current package version appears in the root README;
- the repository overview SVG is referenced and present;
- important landing-page sections remain available;
- `.github/repository-profile.json` has a valid GitHub About description/topics
  and references real canonical files;
- `repository_curator`, `$repository-presentation`, and the reusable presentation
  prompt/maintenance guide remain wired;
- generated Graphify HTML/JSON are marked as generated for GitHub Linguist so they
  do not dominate repository language statistics.

Run this test whenever a version, release, root README, package metadata, GitHub
About/profile, major product capability, or repository-presentation workflow
changes:

```bash
.venv/bin/python -m pytest -q tests/test_repository_presentation.py
```

When adding/renaming/removing a documentation or AI-workspace file, update links
and policy references before merging. Do not bypass these checks by replacing useful
local links with plain text.

## Standard completion checks

For normal Python/runtime changes, the applicable completion set is:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q laptop_guard tests
bash -n install.sh run.sh doctor.sh repair-opencv.sh
.venv/bin/python -m pip check
git diff --check
```

For repository presentation/documentation maintenance, run the focused policy set
first:

```bash
.venv/bin/python -m pytest -q tests/test_repository_presentation.py
.venv/bin/python -m pytest -q tests/test_documentation_links.py tests/test_graphify_navigation_policy.py
```

Use focused Graphify-selected subsets first when debugging. A failure in one of
these commands should be investigated rather than hidden or skipped.

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

For a production release, these checks must be recorded through
[RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md), including separate GNOME X11 and
GNOME Wayland results for the v12.0 primary Ubuntu target.


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
2. use Graphify to connect that test/module to likely production ownership and
   dependencies before broad repository searching;
3. determine whether the failure is product code, test/fixture, dependency,
   Python-version compatibility, packaging, repository-presentation policy, or
   environment/flakiness;
4. reproduce locally or with the smallest equivalent test when possible;
5. fix the cause rather than weakening/skipping the check;
6. rerun the failed focused test before the full suite.

For Codex:

```text
Have tester triage the failing CI job using Graphify first, docs/TESTING.md, and
BUG_TRIAGE_AND_FIXING.md. Return graph freshness, connected production/test paths,
the exact failing step/test, classification, root-cause evidence, and smallest next
fix/diagnostic. Do not change unrelated code.
```

## Verification report format

Record what was actually proven:

```text
Graphify freshness / queries used:
Focused tests:
Repository presentation/policy tests:
Full pytest:
Compile/shell/pip/diff checks:
Original reproduction:
GitHub CI:
Repository Safety:
Graph refreshed after relationship changes:
Manual target-device checks:
Manual GitHub About/social-preview settings:
Not tested / still required:
```

Do not state that camera, microphone, lock, provider, Wayland/X11, or systemd
behavior passed when only unit tests ran.
