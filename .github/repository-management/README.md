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

Projects v2 is user/organization scoped rather than repository scoped. The normal repository `GITHUB_TOKEN` has no Projects v2 write permission, so the repository bootstrap intentionally does not attempt to create a Project board with elevated credentials.

The canonical Project design is documented in `docs/PROJECT_MANAGEMENT.md`.

To create/manage that board automatically in the future, use a dedicated fine-grained user token or GitHub App with Projects write permission, store it as a repository/organization secret, and add a narrowly scoped manual workflow. Do not grant that permission to the normal runtime/CI workflows.
