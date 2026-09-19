# Recommended GitHub Repository Settings

These settings cannot all be enforced from repository files alone. Configure repository-administration settings in GitHub when the connected tool/token does not expose them.

## Repository About and presentation

Canonical About metadata lives in `.github/repository-profile.json`.

Keep the GitHub About panel synchronized with that file:

- **Description** — use `repository-profile.json:description`.
- **Website** — use `repository-profile.json:homepage`; leave blank when `null`.
- **Topics** — use `repository-profile.json:topics`.
- **Social preview** — use `docs/assets/laptop-guard-overview.svg` as the source design and upload the required raster preview through GitHub Settings when desired.

Preview the canonical values locally:

```bash
python scripts/sync_repository_profile.py
```

An admin-capable local environment can apply description/homepage/topics with:

```bash
GH_TOKEN='<admin-capable token>' python scripts/sync_repository_profile.py --apply
```

Never commit or paste the token. Repository **Administration write** permission is required for the API update.

Presentation/version synchronization rules are in `docs/README_MAINTENANCE.md` and protected by `tests/test_repository_presentation.py`.

## Main branch protection

For `main`, enable a branch ruleset or branch protection rule with:

- Require a pull request before merging.
- Require status checks to pass before merging.
- Require the `Release gate` check from CI and the `repository-safety` check.
  `Release gate` succeeds only when the complete Python 3.11/3.12/3.13 matrix succeeds.
- Require conversation resolution before merging.
- Block force pushes.
- Block branch deletion.
- Prefer squash merge or another consistent merge strategy.

For a solo-maintainer repository, requiring one external approval is optional; requiring PRs and passing checks is still useful.

## Security

Enable where available:

- Private vulnerability reporting.
- Dependabot alerts.
- Dependabot security updates.
- Secret scanning / push protection.
- Code scanning if your GitHub plan supports it.

## Issues and pull requests

- Keep Issues enabled for normal bugs/features.
- Send vulnerability reports through the Security policy instead of normal issues.
- Use the issue forms and pull request template in `.github/`.
- Treat a stale README/About profile as a release/documentation defect when a material user-visible change caused the drift.

## Releases

Before a production release:

- CI and Repository Safety must pass.
- Update `CHANGELOG.md`.
- Confirm `pyproject.toml` version matches the root README/version status.
- Run `$repository-presentation` / `repository_curator` and the presentation policy test.
- Confirm `.github/repository-profile.json` still describes the product and apply the About values where admin access is available.
- Follow `docs/ROADMAP.md` and the release checklist tracked for v12.0.
- Test installation/setup/doctor on a clean supported machine.

## Secrets already committed

Removing a secret from the latest branch does not remove it from Git history. Rotate any credential that was ever committed. History rewriting may reduce accidental discovery, but rotation is still required.
