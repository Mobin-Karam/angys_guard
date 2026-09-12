# Contributing to Laptop Guard

Laptop Guard is security-sensitive software. Changes should keep the project
understandable for non-technical users while preserving strict boundaries around
credentials, remote control, capture features, and OS-level actions.

## Graphify-first discovery

Before reading/searching the repository broadly, follow
`docs/GRAPHIFY_NAVIGATION.md`.

Use Graphify to identify the smallest relevant ownership/call/dependency/test/doc
surface:

```bash
graphify query "where is <behavior> implemented?"
graphify explain "<symbol>"
graphify path "<A>" "<B>"
```

Check `graphify-out/GRAPH_REPORT.md` for the build commit first. If stale and
Graphify is available, run `graphify update .`. Do not load the complete
`graphify-out/graph.json` into AI/chat context. After Graphify narrows scope,
confirm important behavior in current source/tests.

If Graphify is unavailable, stale and cannot be refreshed, or insufficient, keep
direct fallback search narrow and note why it was needed.

## Before starting

1. Check `docs/ROADMAP.md` and existing GitHub issues.
2. Prefer an existing issue for non-trivial work.
3. Check Graphify freshness and map the task to owning symbols/files/tests/docs.
4. Classify the task:
   - architecture/cross-module refactor -> `docs/ARCHITECTURE.md`, `docs/architecture/`, relevant ADRs;
   - add/change/remove/fix a feature -> `docs/FEATURE_LIFECYCLE.md`;
   - investigate/fix a bug -> `docs/BUG_TRIAGE_AND_FIXING.md`;
   - feature module template -> `docs/EXTENDING.md`;
   - AI-assisted workflow -> `docs/AI_AGENT_WORKFLOW.md`.
5. Keep one focused change per pull request where practical.
6. Never use real bot/API tokens, chat IDs, private media, or personal logs in code,
   tests, commits, issues, or PRs.

## Local development

Laptop Guard requires Python 3.11 or newer.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m pytest -q
```

For normal installation/testing on Linux, use the repository's `install.sh`,
`run.sh setup`, and `run.sh doctor` flows as applicable.

## Branches

Use descriptive branch names such as:

- `fix/<short-description>`
- `feature/<short-description>`
- `refactor/<short-description>`
- `security/<short-description>`
- `chore/<short-description>`
- `docs/<short-description>`

Do not work directly on `main` for non-trivial changes when a focused branch/PR is
practical.

## Architecture changes

Use Graphify to map current relationships first. Then read `docs/ARCHITECTURE.md`,
`docs/architecture/BOUNDARIES.md`, and `docs/architecture/EVOLUTION_PLAN.md`.

Architecture work should normally:

- preserve behavior unless the issue explicitly changes product behavior;
- extract one cohesive flow/boundary at a time;
- avoid directory/class reshuffling for appearance alone;
- reuse or strengthen existing ports before adding another abstraction;
- keep authorization ahead of privileged side effects;
- identify the authoritative owner for state/persistence;
- state which compatibility path is created, migrated, frozen, or removed;
- include rollback and focused regression verification.

Create/update an ADR when a change materially affects dependency direction,
security boundaries, persistence ownership, extension mechanisms, transport
strategy, concurrency model, or another difficult-to-reverse architectural choice.

A proposed ADR is not permission to merge a runtime change by itself; normal issue,
implementation, testing, and security review still apply.

## Feature changes

Follow `docs/FEATURE_LIFECYCLE.md`. Use Graphify first to identify the owning
abstraction, registration/call paths, config/state/storage, tests, and docs. New bot
commands/callbacks should use the explicit feature system rather than another
dispatcher. Configuration changes need safe defaults and migration behavior.
Feature removal requires a dependency inventory; do not simply delete a module.

For AI-assisted work, the recommended flow is:

```text
navigator (when scope unclear)
        -> architect -> implementer -> tester -> reviewer
                                  \-> security_reviewer when sensitive
```

Small bounded work may use `$safe-implementation` directly. GitHub issue work may
use `$issue-to-pr`.

## Bug fixes

Follow `docs/BUG_TRIAGE_AND_FIXING.md`. Start by using Graphify to connect the
symptom/error/entry point to likely owning code and tests, then reproduce and verify
against current source.

A good bug fix normally follows:

```text
Graphify map -> reproduce -> owner/root cause -> regression test -> smallest fix
-> targeted tests -> applicable full checks -> reviewer/security review
```

Do not "fix" a symptom by bypassing authorization, swallowing errors, retrying
forever, or adding a second parallel implementation path.

If a problem cannot yet be reproduced, improve diagnostics or gather the minimum
evidence needed to distinguish likely causes instead of making speculative broad
changes.

## Pull requests

A PR should explain:

- what user problem it solves;
- issue/acceptance criteria when applicable;
- root cause for bug fixes, design boundary for features, or migration boundary for architecture changes;
- relevant Graphify impact/navigation findings when useful;
- security/privacy impact;
- configuration or migration impact;
- automated tests/checks performed;
- Graphify freshness/refresh status when relationships materially changed;
- manual target-device validation performed or still required;
- rollback considerations for risky changes.

The test suite and required GitHub checks should pass before merge.

## User experience rule

Expected setup, dependency, configuration, permission, provider, and hardware
failures should produce actionable messages rather than raw tracebacks. Advanced
diagnostics may remain available in logs, but normal flows should guide recovery.

## Security-sensitive changes

Extra review is expected for changes involving provider authentication/owner
pairing, remote lock/unlock or stop authorization, local control API, secrets,
process execution, camera/microphone/screen/evidence, systemd/autostart, input
monitoring, or intrusion response.

Use Graphify to trace the changed surface to these trust boundaries, then verify
those paths in current source. Do not weaken an authorization/privacy boundary for
convenience. Use `security_reviewer` / `$security-review` for sensitive final diffs.

## Tests

Use Graphify to identify connected tests first. Add/update tests for behavior
changes. Tests must use fake credentials and temporary paths. Hardware/network
behavior should be mocked where practical so CI does not depend on a real camera,
microphone, provider account, desktop session, or personal device.

Read `docs/TESTING.md`. Use `$test-and-verify` for AI-assisted verification.

## Documentation

Update user-facing docs when behavior, required packages, setup steps, commands,
supported platforms, security expectations, architecture ownership, or maintenance
workflows change.

When adding/removing files or materially changing responsibility, keep
`docs/FILE_REFERENCE.md` current and refresh Graphify when available. Architecture
changes should update canonical architecture/ADR docs rather than duplicating the
target design elsewhere.

## Vulnerabilities

Do not report vulnerabilities through normal issues. Follow `SECURITY.md`.
