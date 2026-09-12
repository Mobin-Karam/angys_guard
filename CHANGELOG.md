# Changelog

All notable changes to Laptop Guard should be recorded here from this point forward.

The project uses semantic-style versioning where practical:

- **Patch**: fixes and compatible hardening.
- **Minor**: compatible features and UX improvements.
- **Major**: breaking behavior, configuration, or compatibility changes.

## Unreleased

### Repository and project management

- Added GitHub Actions CI for supported Python versions.
- Added repository safety checks to prevent common local secret files and private keys from being committed.
- Added Dependabot configuration for Python and GitHub Actions dependencies.
- Added issue forms, pull request checklist, CODEOWNERS, security policy, and contributing guide.
- Removed the tracked `.env` file from the current branch and added ignore rules for local secrets/runtime artifacts.

### Planned

See `docs/ROADMAP.md` and the GitHub project-tracking issue for the v11.2, v11.3, and v12.0 work.

## 11.1.0

This is the current version declared by `pyproject.toml` when this changelog was introduced. Historical release details have not been reconstructed here; add older entries only from verified tags, releases, or commit history.
