---
name: repository-presentation
description: Keep Laptop Guard's root README, GitHub About profile metadata, package/release references, docs index, and repository visual synchronized with current shipped behavior. Use after releases, version changes, major features, setup/command/platform/security changes, repository reorganizations, or when asked to improve README/About/docs presentation.
---

# Repository presentation

Treat repository presentation as a maintained product surface.

## Start with Graphify

1. Read root `AGENTS.md` and applicable scoped instructions.
2. Follow `docs/GRAPHIFY_NAVIGATION.md` before broad source/search work.
3. Check graph freshness.
4. Query the smallest relevant product surface, for example:

   ```bash
   graphify query "what user-visible capabilities and commands exist?"
   graphify query "what files define setup, doctor and service behavior?"
   graphify query "what security boundaries constrain owner remote control?"
   ```

5. Confirm all material claims in current source/tests/canonical docs.

## Canonical maintenance guide

Follow `docs/README_MAINTENANCE.md`.

The important presentation surfaces are:

- `README.md`;
- `docs/assets/laptop-guard-overview.svg`;
- `.github/repository-profile.json`;
- `pyproject.toml`;
- `docs/README.md`;
- `CHANGELOG.md`;
- `docs/ROADMAP.md`.

## Rules

- Never describe planned roadmap work as shipped.
- Never invent support claims from an issue title or proposal.
- Keep security/privacy wording aligned with `docs/SECURITY.md` and `AGENTS.md`.
- Preserve the explicit non-goals: no generic remote shell, keylogging, credential collection, hidden/unbounded capture, or arbitrary remote filesystem control.
- Keep commands copy-pasteable and paths accurate.
- Keep the current README version synchronized with `pyproject.toml`.
- Update the repository profile only when discoverability/product identity materially changes.
- Update the overview graphic only when the high-level product flow changes.
- Do not duplicate detailed canonical docs into the root README; summarize and link.

## Release/change workflow

For a release or material user-visible change:

1. identify affected claims with Graphify;
2. confirm source/tests/docs;
3. update the smallest relevant presentation files;
4. update `CHANGELOG.md` for shipped changes;
5. run presentation/link/Graphify policy tests;
6. run broader checks required by `docs/TESTING.md` when part of a product release;
7. refresh Graphify when documentation relationships materially changed and Graphify is available;
8. report any GitHub About/social-preview values that still require repository-admin UI/API access.

## Verification

Run at least:

```bash
.venv/bin/python -m pytest -q tests/test_repository_presentation.py
.venv/bin/python -m pytest -q tests/test_documentation_links.py tests/test_graphify_navigation_policy.py
```

For release work, also use `$release-readiness`.

## Handoff

Return:

```text
Presentation surfaces changed:
Shipped facts verified from:
Version consistency:
GitHub About/profile changes:
Security wording reviewed:
Checks run:
Graphify refresh status:
Manual GitHub settings still required:
```
