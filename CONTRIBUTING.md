# Contributing to Laptop Guard

Laptop Guard is security-sensitive software. Changes should keep the project understandable for non-technical users while preserving strict boundaries around credentials, remote control, capture features, and OS-level actions.

## Before starting

1. Check `docs/ROADMAP.md` and existing GitHub issues.
2. Prefer an existing issue for non-trivial work.
3. Classify the task:
   - add/change/remove/fix a feature -> `docs/FEATURE_LIFECYCLE.md`;
   - investigate/fix a bug -> `docs/BUG_TRIAGE_AND_FIXING.md`;
   - feature module template -> `docs/EXTENDING.md`;
   - AI-assisted workflow -> `docs/AI_AGENT_WORKFLOW.md`.
4. Keep one focused change per pull request where practical.
5. Never use real bot/API tokens, chat IDs, private media, or personal logs in code, tests, commits, issues, or PRs.

## Local development

Laptop Guard requires Python 3.11 or newer.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
python -m pytest -q
```

For normal installation/testing on Linux, use the repository's `install.sh`, `run.sh setup`, and `run.sh doctor` flows as applicable.

## Branches

Use descriptive branch names such as:

- `fix/<short-description>`
- `feature/<short-description>`
- `security/<short-description>`
- `chore/<short-description>`
- `docs/<short-description>`

Do not work directly on `main` for non-trivial changes when a focused branch/PR is practical.

## Feature changes

Follow `docs/FEATURE_LIFECYCLE.md`.

Before editing, identify the owning abstraction and trace existing behavior. New bot commands/callbacks should use the explicit feature system rather than adding another dispatcher. Configuration changes need safe defaults and migration behavior. Feature removal requires a dependency inventory; do not simply delete the implementation module.

For AI-assisted work, the recommended flow is:

```text
architect -> implementer -> tester -> reviewer
                         \-> security_reviewer when sensitive
```

Small bounded work may use `$safe-implementation` directly. GitHub issue work may use `$issue-to-pr`.

## Bug fixes

Follow `docs/BUG_TRIAGE_AND_FIXING.md`.

A good bug fix normally follows:

```text
reproduce -> identify owner/root cause -> regression test -> smallest fix
-> targeted tests -> applicable full checks -> reviewer/security review
```

Do not "fix" a symptom by bypassing authorization, swallowing errors, retrying forever, or adding a second parallel implementation path.

If a problem cannot yet be reproduced, improve diagnostics or gather the minimum evidence needed to distinguish likely causes instead of making speculative broad changes.

## Pull requests

A PR should explain:

- what user problem it solves;
- issue/acceptance criteria when applicable;
- root cause for bug fixes, or design boundary for feature changes;
- security/privacy impact;
- configuration or migration impact;
- automated tests/checks performed;
- manual target-device validation performed or still required;
- rollback considerations for risky changes.

The test suite and required GitHub checks should pass before merge.

## User experience rule

Expected setup, dependency, configuration, permission, provider, and hardware failures should produce actionable messages rather than raw tracebacks. Advanced diagnostics may remain available in logs, but normal flows should guide the user toward recovery.

## Security-sensitive changes

Extra review is expected for changes involving:

- provider authentication and owner pairing;
- remote lock/unlock or stop authorization;
- the local control API;
- secret/config storage;
- arbitrary process/command execution boundaries;
- camera, microphone, screen capture, or stored evidence;
- systemd/autostart and OS session locking;
- input monitoring and intrusion response.

Do not weaken an authorization or privacy boundary merely to make a feature easier to use.

Use the repo-local `security_reviewer` / `$security-review` workflow for sensitive final diffs.

## Tests

Add or update tests for behavior changes. Tests must use fake credentials and temporary paths. Hardware/network behavior should be mocked where practical so CI does not depend on a real camera, microphone, Telegram/Bale account, desktop session, or personal device.

Read `docs/TESTING.md`. Use `$test-and-verify` for AI-assisted verification.

## Documentation

Update user-facing documentation when behavior, required packages, setup steps, commands, supported platforms, security expectations, architecture ownership, or maintenance workflows change.

When adding/removing files or materially changing responsibility, keep `docs/FILE_REFERENCE.md` current.

## Vulnerabilities

Do not report vulnerabilities through normal issues. Follow `SECURITY.md`.
