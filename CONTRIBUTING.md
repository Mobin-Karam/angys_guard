# Contributing to Laptop Guard

Laptop Guard is security-sensitive software. Changes should keep the project understandable for non-technical users while preserving strict boundaries around credentials, remote control, capture features, and OS-level actions.

## Before starting

1. Check the roadmap and existing issues.
2. Prefer an existing issue for non-trivial work.
3. Keep one focused change per pull request where practical.
4. Never use real bot/API tokens, chat IDs, private media, or personal logs in code, tests, commits, issues, or PRs.

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

## Pull requests

A PR should explain:

- What user problem it solves.
- Security/privacy impact.
- Configuration or migration impact.
- Manual validation performed.
- Rollback considerations for risky changes.

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

## Tests

Add or update tests for behavior changes. Tests must use fake credentials and temporary paths. Hardware/network behavior should be mocked where practical so CI does not depend on a real camera, microphone, Telegram/Bale account, desktop session, or personal device.

## Documentation

Update user-facing documentation when behavior, required packages, setup steps, commands, supported platforms, or security expectations change.

## Vulnerabilities

Do not report vulnerabilities through normal issues. Follow `SECURITY.md`.
