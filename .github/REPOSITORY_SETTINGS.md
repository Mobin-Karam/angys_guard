# Recommended GitHub Repository Settings

These settings cannot be enforced from repository files alone. Configure them in GitHub repository settings.

## Main branch protection

For `main`, enable a branch ruleset or branch protection rule with:

- Require a pull request before merging.
- Require status checks to pass before merging.
- Require the `CI` and `Repository Safety` checks once they are stable.
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

## Releases

Before a production release:

- CI and Repository Safety must pass.
- Update `CHANGELOG.md`.
- Confirm `pyproject.toml` version.
- Follow `docs/ROADMAP.md` and the release checklist tracked for v12.0.
- Test installation/setup/doctor on a clean supported machine.

## Secrets already committed

Removing a secret from the latest branch does not remove it from Git history. Rotate any credential that was ever committed. History rewriting may reduce accidental discovery, but rotation is still required.
