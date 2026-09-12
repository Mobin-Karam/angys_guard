Refresh this repository's presentation for the current change or release: <change/release/context>

Follow the repository instructions first. Use Graphify before broad source/doc reads, check graph freshness, and identify the smallest set of current source/tests/docs needed to verify the affected user-visible facts.

Use `docs/README_MAINTENANCE.md` as the canonical maintenance contract.

Review and update only what is actually affected among:
- `README.md`;
- `docs/assets/laptop-guard-overview.svg`;
- `.github/repository-profile.json`;
- `docs/README.md`;
- package/version/readme metadata in `pyproject.toml`;
- `CHANGELOG.md`;
- presentation-related agent/skill/prompt indexes.

Requirements:
1. verify current shipped behavior from source/tests/canonical docs;
2. never present roadmap/proposed work as shipped;
3. keep README version/status synchronized with `pyproject.toml`;
4. keep security/privacy/non-goal wording accurate;
5. keep install/command examples copy-pasteable;
6. update the hero visual only if the high-level product flow changed;
7. keep GitHub About description/topics in `.github/repository-profile.json` current;
8. run `tests/test_repository_presentation.py`, documentation-link checks, and Graphify navigation-policy tests;
9. refresh Graphify after material documentation relationship changes when available;
10. report any GitHub About/social-preview changes that still require repository-admin UI/API access.

Return a concise summary of facts verified, presentation surfaces changed, checks run, graph freshness, and remaining manual settings. Do not perform unrelated runtime changes.
