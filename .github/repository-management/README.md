# Repository management configuration

This directory is the declarative source for Laptop Guard's GitHub issue/release management metadata.

## Managed automatically

`../workflows/repository-management-bootstrap.yml` applies these files on `main` and may also be run manually:

- `labels.json` — canonical repository label taxonomy;
- `milestones.json` — release/architecture milestones;
- `issues.json` — issue-to-label/milestone mapping;
- `releases/v11.1.0.md` — release notes for the stable `v11.1.0` baseline.

The bootstrap is idempotent: existing labels/milestones/release metadata are updated rather than duplicated. Existing unrelated issue labels are preserved.

## Version/release rule

Do not change an already-published release tag to point at a different product state merely to include later work. Future releases should add a new release-notes file and update the bootstrap/release process intentionally.

The current baseline version is declared by `pyproject.toml` as `11.1.0`, therefore the initial GitHub release tag is `v11.1.0`.

## GitHub Project v2

Projects v2 is user/organization scoped rather than repository scoped. The normal repository `GITHUB_TOKEN` has no Projects v2 write permission, so the standard repository bootstrap intentionally does not use elevated Project credentials.

The canonical Project design is documented in `docs/PROJECT_MANAGEMENT.md` and the machine blueprint is `project-v2.json`.

A narrowly scoped manual workflow already exists at `../workflows/project-v2-bootstrap.yml`. It requires the repository secret `ANGYSGUARD_PROJECT_TOKEN` with GitHub Projects access and runs `scripts/bootstrap_github_project.sh`. Do not grant Projects write permission to normal runtime/CI workflows, and never print or commit that token.
