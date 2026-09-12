---
name: release-readiness
description: Assess or prepare an AngysGuard / Laptop Guard release using Graphify impact/freshness, CI, tests, changelog, roadmap, security status, platform/control-mode support, version metadata, repository presentation, and target-device checks.
---

# Release readiness

1. Follow `AGENTS.md` and `docs/GRAPHIFY_NAVIGATION.md`; use Graphify to map changed product/config/state/storage/provider/platform surfaces and connected tests/docs.
2. Read the release-relevant subset of `CHANGELOG.md`, `docs/ROADMAP.md`, `docs/TESTING.md`, `SECURITY.md`, `docs/README_MAINTENANCE.md`, `docs/PLATFORM_SUPPORT.md`, `docs/CONTROL_MODES.md`, `docs/ANGYSGUARD_PRODUCT_VISION.md`, and milestone issues.
3. Verify version consistency in `pyproject.toml`, `README.md`, changelog/release docs.
4. Use `$product-roadmap-maintenance` / `product_planner` if the release changes an OS/app/provider/control mode/support state. Keep current, best-effort, planned, research and requested states distinct.
5. Use `$repository-presentation` / `repository_curator` to verify root README, repository profile, package metadata, docs navigation and visual against **shipped** behavior.
6. Confirm CI and Repository Safety are green on the release commit.
7. Use `$test-and-verify`, including repository-presentation/documentation policy tests for release docs.
8. Check P0 security work, credential rotation, regressions, migrations and material Graphify staleness.
9. Confirm supported platform/session/provider matrix is current. A platform must not move to Supported without implementation plus target-device validation.
10. Confirm remote-control/onboarding design does not send/store protected-device OS passwords through Bale, Telegram, mobile apps, managed backend, or normal environment variables. Self-hosted/local remains first-class and no generic remote shell exists.
11. Record real device/session/provider validation separately from unit CI. Linux CI does not prove Windows/Android behavior.
12. Prepare changelog/release notes from shipped changes only.
13. Refresh Graphify after material source/docs relationships changed when available.
14. Report any GitHub About/social-preview/admin settings still pending.
15. Do not tag/publish/create a GitHub Release unless explicitly requested.

Return **Ready**, **Blocked**, and **Manual validation** plus Graphify freshness, platform/control-mode support status, repository-presentation status, and exact next release action.
