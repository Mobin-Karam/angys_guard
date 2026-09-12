# GitHub Setup Guide

This repository includes GitHub-native files for issue forms, pull requests, CI, dependency updates, code ownership, repository safety checks, and repository-presentation metadata.

Some protections and presentation settings must still be enabled/applied through an admin-capable GitHub API token or the GitHub web interface because repository files alone cannot turn them on.

## 1. Synchronize the repository About panel

The canonical About/profile values live in:

```text
.github/repository-profile.json
```

Preview them safely:

```bash
python scripts/sync_repository_profile.py
```

If you have a trusted token with repository **Administration write** permission:

```bash
GH_TOKEN='<admin-capable token>' python scripts/sync_repository_profile.py --apply
```

Do not commit or paste that token into issues, logs, documentation, or chat.

Without an admin-capable API token, open the repository and use the **About** gear icon:

- Description → copy `repository-profile.json:description`;
- Website → use `homepage` or leave blank when it is `null`;
- Topics → copy `repository-profile.json:topics`.

For **Social preview**, use `docs/assets/laptop-guard-overview.svg` as the source design and upload the required raster image through **Settings → General → Social preview** when desired.

The repository presentation synchronization contract is `docs/README_MAINTENANCE.md`.

## 2. Protect `main`

Open **Settings → Rules → Rulesets** (or Branch protection rules) and create a rule for `main`.

Recommended settings:

- Require a pull request before merge.
- Require status checks before merge.
- Add `CI` and `Repository Safety` as required checks after confirming they pass reliably.
- Require conversation resolution.
- Block force pushes.
- Block deletion of `main`.

For a solo-maintainer project, required external approvals are optional. The important part is that changes still pass through PRs/checks once the workflow is established.

## 3. Enable security features

Open **Settings → Security / Code security and analysis** and enable, where your plan supports them:

- Private vulnerability reporting.
- Dependabot alerts.
- Dependabot security updates.
- Secret scanning.
- Push protection.
- Code scanning.

## 4. Review Actions

Open the **Actions** tab and confirm these workflows are green:

- `CI`
- `Repository Safety`

Do not make a failing check required until its environment assumptions are corrected and it is stable.

## 5. Dependency updates

Dependabot is configured for:

- Python (`pip`)
- GitHub Actions

Review dependency PRs instead of merging them automatically. Laptop Guard interacts with OS/hardware/security capabilities, so dependency updates should pass CI and relevant manual checks.

## 6. Issues and pull requests

Normal bug reports and feature requests should use the repository issue forms.

Security vulnerabilities must follow `SECURITY.md` and should not be posted in a normal issue.

Pull requests should use the repository checklist and include security/privacy impact when relevant. Releases and material user-visible/setup/platform/security changes should also account for repository-presentation impact through `docs/README_MAINTENANCE.md`.

## 7. Releases

Before creating a release:

1. Confirm roadmap/release issues are complete.
2. Run the full test suite.
3. Confirm `CI` and `Repository Safety` pass.
4. Test install/setup/doctor on a clean supported environment.
5. Update `CHANGELOG.md` with shipped behavior only.
6. Update the version in `pyproject.toml`.
7. Run `$repository-presentation` / `repository_curator` and confirm the root README version, capabilities, About profile, package metadata, and docs navigation are current.
8. Run `tests/test_repository_presentation.py` and documentation/Graphify policy checks.
9. Apply `.github/repository-profile.json` to GitHub About where admin access is available.
10. Refresh Graphify after material relationship/docs changes when possible.
11. Tag the exact tested release commit.
12. Publish release notes that call out security, config migration, platform changes, and known manual-validation limits.
