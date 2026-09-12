---
name: release-readiness
description: Assess or prepare a Laptop Guard release using Graphify impact/freshness, CI, tests, changelog, roadmap, security status, version metadata, and target-device checks. Use for release planning, tagging preparation, or deciding whether a version is ready.
---

# Release readiness

1. Follow `AGENTS.md` and `docs/GRAPHIFY_NAVIGATION.md`. Check graph freshness and
   use Graphify to summarize changed communities/symbols, public/config/state/storage
   surfaces, connected tests/docs, and architecture/security hotspots.
2. Read `CHANGELOG.md`, `docs/ROADMAP.md`, `docs/TESTING.md`, `SECURITY.md`, and
   relevant open release/milestone issues identified by the release scope.
3. Verify version consistency in `pyproject.toml` and user-facing release docs.
4. Confirm CI and repository-safety workflows are green for the release commit.
5. Run/use `test-and-verify` for applicable local verification.
6. Check P0 security work, credential rotation, known regressions, migrations, and
   material graph staleness are resolved or explicitly block the release.
7. Confirm support matrix/known limitations for Ubuntu, Python, X11/Wayland,
   hardware, and provider integrations are current.
8. Record manual target-device results separately from unit-test results.
9. Prepare changelog/release notes from shipped changes only; do not describe
   roadmap items as released.
10. Refresh Graphify before release when material source/docs relationships changed
    and the tool is available.
11. Do not create/push tags, publish packages, or create a GitHub Release unless the
    user explicitly asks for that action.

Return a checklist grouped as **Ready**, **Blocked**, and **Manual validation**,
plus Graphify freshness/impact summary and the exact next release action.
