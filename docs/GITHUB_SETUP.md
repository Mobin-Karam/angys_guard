# GitHub Setup Guide

This repository includes GitHub-native files for issue forms, pull requests, CI, dependency updates, code ownership, and repository safety checks.

Some protections must still be enabled in the GitHub web interface because repository files cannot turn them on automatically.

## 1. Protect `main`

Open **Settings → Rules → Rulesets** (or Branch protection rules) and create a rule for `main`.

Recommended settings:

- Require a pull request before merge.
- Require status checks before merge.
- Add `CI` and `Repository Safety` as required checks after confirming they pass reliably.
- Require conversation resolution.
- Block force pushes.
- Block deletion of `main`.

For a solo-maintainer project, required external approvals are optional. The important part is that changes still pass through PRs/checks once the workflow is established.

## 2. Enable security features

Open **Settings → Security / Code security and analysis** and enable, where your plan supports them:

- Private vulnerability reporting.
- Dependabot alerts.
- Dependabot security updates.
- Secret scanning.
- Push protection.
- Code scanning.

## 3. Review Actions

Open the **Actions** tab and confirm these workflows are green:

- `CI`
- `Repository Safety`

Do not make a failing check required until its environment assumptions are corrected and it is stable.

## 4. Dependency updates

Dependabot is configured for:

- Python (`pip`)
- GitHub Actions

Review dependency PRs instead of merging them automatically. Laptop Guard interacts with OS/hardware/security capabilities, so dependency updates should pass CI and relevant manual checks.

## 5. Issues and pull requests

Normal bug reports and feature requests should use the repository issue forms.

Security vulnerabilities must follow `SECURITY.md` and should not be posted in a normal issue.

Pull requests should use the repository checklist and include security/privacy impact when relevant.

## 6. Releases

Before creating a release:

1. Confirm roadmap/release issues are complete.
2. Run the full test suite.
3. Confirm `CI` and `Repository Safety` pass.
4. Test install/setup/doctor on a clean supported environment.
5. Update `CHANGELOG.md`.
6. Update the version in `pyproject.toml`.
7. Tag the exact release commit.
8. Publish release notes that call out security, config migration, and platform changes.
