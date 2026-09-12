---
name: release-readiness
description: Assess or prepare a Laptop Guard release using CI, tests, changelog, roadmap, security status, version metadata, and target-device checks. Use for release planning, tagging preparation, or deciding whether a version is ready.
---

# Release readiness

1. Read `CHANGELOG.md`, `docs/ROADMAP.md`, `docs/TESTING.md`, `SECURITY.md`, and
   relevant open release/milestone issues.
2. Verify version consistency in `pyproject.toml` and user-facing release docs.
3. Confirm CI and repository-safety workflows are green for the release commit.
4. Run/use `test-and-verify` for the applicable local verification.
5. Check that P0 security work, credential rotation, known regressions, and required
   migrations are resolved or explicitly block the release.
6. Confirm the support matrix/known limitations for Ubuntu, Python, X11/Wayland,
   hardware, and provider integrations are current.
7. Record manual target-device results separately from unit-test results.
8. Prepare changelog/release notes from shipped changes only; do not describe
   roadmap items as released.
9. Do not create/push tags, publish packages, or create a GitHub Release unless the
   user explicitly asks for that action.

Return a checklist grouped as **Ready**, **Blocked**, and **Manual validation**,
then give the exact next action required for release.
