---
name: repository-presentation
description: Keep AngysGuard's root README, GitHub About/profile metadata, brand assets, package/release references, docs index, and repository visuals synchronized with current shipped behavior. Use after releases, version changes, major features, setup/command/platform/security changes, brand updates, repository reorganizations, or when asked to improve README/About/docs presentation.
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

## Canonical presentation sources

Follow `docs/README_MAINTENANCE.md` and `docs/BRAND_GUIDE.md`.

The important presentation surfaces are:

- `README.md`;
- `docs/assets/laptop-guard-overview.svg` (legacy README path, now carrying the AngysGuard hero);
- `docs/assets/brand/`;
- `.github/repository-profile.json`;
- `pyproject.toml`;
- `docs/README.md`;
- `CHANGELOG.md`;
- `docs/ROADMAP.md`.

Use `$brand-assets` for logo/icon/wordmark/color/social-preview changes.

## Rules

- Never describe planned roadmap work as shipped.
- Never invent support claims from an issue title or proposal.
- Use **owner-controlled endpoint security and device protection platform** as the primary AngysGuard category unless canonical product docs change it.
- Do not market AngysGuard as antivirus unless a validated malware-detection engine actually ships.
- Keep security/privacy wording aligned with `docs/SECURITY.md` and `AGENTS.md`.
- Preserve explicit non-goals: no generic remote shell, keylogging, credential collection, hidden/unbounded capture, or arbitrary remote filesystem control.
- Keep commands copy-pasteable and paths accurate.
- Keep the current README version synchronized with `pyproject.toml`.
- Update repository profile metadata only when discoverability/product identity materially changes.
- Update brand/overview graphics only when the identity or high-level product flow changes.
- Do not duplicate detailed canonical docs into the root README; summarize and link.

## Release/change workflow

For a release or material user-visible change:

1. identify affected claims with Graphify;
2. confirm source/tests/docs;
3. update the smallest relevant presentation files;
4. update `CHANGELOG.md` for shipped changes;
5. run presentation/link/Graphify/brand policy tests;
6. run broader checks required by `docs/TESTING.md` when part of a product release;
7. refresh Graphify when documentation relationships materially changed and Graphify is available;
8. report any GitHub About/social-preview values that still require repository-admin UI/API access.

## Verification

Run at least:

```bash
.venv/bin/python -m pytest -q tests/test_repository_presentation.py tests/test_brand_assets.py
.venv/bin/python -m pytest -q tests/test_documentation_links.py tests/test_graphify_navigation_policy.py
```

For release work, also use `$release-readiness`.

## Handoff

Return:

```text
Presentation surfaces changed:
Shipped facts verified from:
Version consistency:
Brand assets/category checked:
GitHub About/profile changes:
Security wording reviewed:
Checks run:
Graphify refresh status:
Manual GitHub settings still required:
```
