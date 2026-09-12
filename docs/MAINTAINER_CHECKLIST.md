# Maintainer Checklist

Use this as the short operational checklist. Detailed procedures live in:

- `GRAPHIFY_NAVIGATION.md` — graph-first navigation/freshness;
- `FEATURE_LIFECYCLE.md` — feature lifecycle;
- `BUG_TRIAGE_AND_FIXING.md` — bug/issue repair;
- `TESTING.md` — automated/manual validation;
- `ANGYSGUARD_PRODUCT_VISION.md` — product identity/direction;
- `PLATFORM_SUPPORT.md` — current/planned/research OS support;
- `CONTROL_MODES.md` — local/Bale/Telegram/self-hosted/managed modes;
- `README_MAINTENANCE.md` — README/About/package/support presentation synchronization;
- `AI_AGENT_WORKFLOW.md` — agents/skills/task recipes.

## Every pull request

- [ ] Scope is clear and linked to an issue when appropriate.
- [ ] Graphify was used first for discovery/impact mapping, or fallback reason is recorded.
- [ ] Important graph conclusions were confirmed in current source/tests.
- [ ] Feature/bug/architecture/product-roadmap workflow was followed as applicable.
- [ ] No secrets, bot tokens, OS passwords, private keys, or private evidence are included.
- [ ] CI and Repository Safety pass.
- [ ] Security/privacy impact was considered.
- [ ] Setup/config/migration impact was considered.
- [ ] Current, best-effort, planned, research and user-requested support states remain distinct.
- [ ] A new OS/app/provider/control mode is not presented as shipped without implementation/validation.
- [ ] Managed-service/self-hosted changes preserve local/self-hosted as a first-class path unless a separately approved breaking product decision says otherwise.
- [ ] Remote-control changes do not introduce a generic shell or OS-password-through-bot/backend flow.
- [ ] Tests/docs were updated where behavior changed.
- [ ] If release/version/user-visible/platform/control/security/repository structure changed, `README_MAINTENANCE.md`, `$repository-presentation`, and `$product-roadmap-maintenance` were applied where relevant.
- [ ] Target-device/provider/platform validation is listed separately when CI cannot prove it.
- [ ] `FILE_REFERENCE.md` was updated if ownership/layout materially changed.
- [ ] Graphify refresh/follow-up is accounted for after material relationship changes.

## Weekly

- [ ] Review open P0/P1 issues and blockers.
- [ ] Review Dependabot alerts/PRs and failed/flaky Actions runs.
- [ ] Check project tracker/milestones and move the next highest-value issue forward.
- [ ] Confirm no security/credential/pairing issue lacks an owner.
- [ ] Check new bugs have reproduction/evidence or a clear next diagnostic.
- [ ] Check newly added features have tests/docs and did not create duplicate legacy paths.
- [ ] Review new `type:platform-request` issues as demand signals; do not promise support automatically.
- [ ] Check `PLATFORM_SUPPORT.md` still matches actual validated support.
- [ ] Check `CONTROL_MODES.md` matches current provider/onboarding behavior and future managed/self-hosted plans.
- [ ] Compare recent user-visible/product-direction changes with README/About/profile and fix drift.
- [ ] Compare Graphify build commit with current `main`; refresh when material relationships changed.

## Before a release

- [ ] Release milestone/checklist is complete.
- [ ] `$release-readiness` / `release_manager` has no unresolved blocker.
- [ ] `product_planner` / `$product-roadmap-maintenance` reviewed platform/control/support claims when relevant.
- [ ] `repository_curator` / `$repository-presentation` review is complete.
- [ ] Graphify freshness is acceptable or the release explicitly records the limitation.
- [ ] Full automated checks pass on the supported Python range.
- [ ] Documentation/Graphify/repository-presentation policy checks pass.
- [ ] Repository Safety passes on the release commit.
- [ ] Clean-machine installation succeeds on every platform the release claims as Supported.
- [ ] Setup, doctor, provider pairing, camera, microphone, lock, service/autostart and offline behavior are validated as applicable.
- [ ] Any new Supported OS/session/provider has real target-device/manual validation recorded.
- [ ] Windows/Android/managed-service work remains Planned/Research unless its acceptance and validation gates are genuinely complete.
- [ ] No design sends/stores protected-device OS passwords through Bale/Telegram/mobile/managed backend or normal environment variables.
- [ ] Known P0/P1 regressions are resolved or explicitly block release.
- [ ] `CHANGELOG.md` contains shipped behavior only.
- [ ] `pyproject.toml` version matches README status/badge.
- [ ] `PLATFORM_SUPPORT.md`, `CONTROL_MODES.md`, product vision, README and repository profile are mutually consistent.
- [ ] GitHub About/social preview is synchronized where admin access is available; otherwise manual setting is recorded.
- [ ] README install/command examples still match current behavior.
- [ ] Known platform/session/provider limitations are documented.
- [ ] Previously exposed credentials are rotated.
- [ ] Release tag points to the exact tested commit.

## After a release

- [ ] Verify published installation instructions on the supported target(s).
- [ ] Verify README/About/support matrix render correctly for the release.
- [ ] Watch CI/issues for upgrade/platform regressions.
- [ ] Triage new defects with Graphify + bug playbook rather than speculative fixes.
- [ ] Confirm Graphify released baseline/follow-up provenance is clear.
- [ ] Open follow-up issues instead of silently carrying unfinished release/platform/presentation work.
