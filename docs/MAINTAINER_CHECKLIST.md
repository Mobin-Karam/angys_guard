# Maintainer Checklist

Use this as the short operational checklist for repository maintenance. Detailed
procedures live in:

- `GRAPHIFY_NAVIGATION.md` for graph-first repository navigation/freshness;
- `FEATURE_LIFECYCLE.md` for add/change/fix/remove feature work;
- `BUG_TRIAGE_AND_FIXING.md` for issue/bug investigation and repair;
- `TESTING.md` for automated/manual validation;
- `README_MAINTENANCE.md` for root README, GitHub About/profile, package/version,
  documentation navigation, and repository visual synchronization;
- `AI_AGENT_WORKFLOW.md` for Codex agents/skills and task recipes.

## Every pull request

- [ ] Scope is clear and linked to an issue when appropriate.
- [ ] Graphify was used first for repository discovery/impact mapping, or the
      narrow fallback reason is recorded.
- [ ] Important graph relationships were confirmed in current source/tests.
- [ ] Task followed the feature-lifecycle or bug-triage workflow as applicable.
- [ ] No secrets or private evidence are included.
- [ ] CI passes, including documentation/AI/Graphify/presentation-policy regression tests.
- [ ] Repository Safety passes.
- [ ] Security/privacy impact was considered.
- [ ] Setup/config migration impact was considered.
- [ ] Feature removal checked stale commands/config/docs/tests/migrations where applicable.
- [ ] User-facing errors remain actionable.
- [ ] Regression tests were added/updated for bug fixes where practical.
- [ ] Tests/docs were updated where behavior changed.
- [ ] If the change affects a release/version, user-visible feature/command,
      setup/platform requirement, security boundary, or repository structure,
      `README_MAINTENANCE.md` / `$repository-presentation` was applied.
- [ ] `README.md` and `.github/repository-profile.json` do not contain stale shipped-feature claims.
- [ ] Target-device validation is listed separately when CI cannot prove it.
- [ ] `FILE_REFERENCE.md` was updated if file ownership/layout materially changed.
- [ ] Graphify was refreshed after material file/symbol/dependency/doc relationship
      changes when the tool was available; otherwise a follow-up is recorded.

## Weekly

- [ ] Review open P0/P1 issues.
- [ ] Review Dependabot PRs and alerts.
- [ ] Review failed Actions runs and recurring/flaky failures.
- [ ] Check the project tracker and move the next highest-value issue forward.
- [ ] Confirm no credential/security issue is waiting without an owner.
- [ ] Check newly reported bugs have reproduction/evidence or a clear next diagnostic.
- [ ] Check recently added features have docs/tests and no duplicate legacy path was left behind.
- [ ] Compare the Graphify `GRAPH_REPORT.md` build commit with current `main`; refresh
      with `graphify update .` when material repository relationships changed.
- [ ] Spot-check `graphify query`, `graphify explain`, and `graphify path` for a few
      core nodes when a graph refresh landed.
- [ ] Compare recent user-visible changes with the root README and About profile;
      fix drift instead of waiting for the next release.

## Before a release

- [ ] Release milestone/checklist is complete.
- [ ] `$release-readiness` / release-manager review has no unresolved blocker.
- [ ] `repository_curator` / `$repository-presentation` review is complete.
- [ ] Graphify is fresh enough to represent the release's material source/docs
      relationships, or a documented reason explicitly blocks/waives it.
- [ ] Full tests pass on the supported Python range.
- [ ] Documentation link/index, Graphify-navigation, and repository-presentation policy checks pass.
- [ ] Repository Safety passes on the release commit.
- [ ] Clean-machine install succeeds.
- [ ] Setup, doctor, provider pairing, camera, microphone, locking, service/autostart, and offline behavior are validated as applicable.
- [ ] Known P0/P1 regressions are resolved or explicitly block the release.
- [ ] `CHANGELOG.md` is updated with shipped behavior only.
- [ ] `pyproject.toml` version is correct and matches the root README release/status surface.
- [ ] `.github/repository-profile.json` description/topics still match the product.
- [ ] GitHub About/social preview is synchronized from the canonical profile where admin access is available; otherwise the manual setting is recorded.
- [ ] README install/command examples still match current behavior.
- [ ] Planned roadmap work is not described as already shipped.
- [ ] Known platform/session limitations are documented.
- [ ] Any previously exposed credentials have been rotated.
- [ ] Release tag points to the exact tested commit.

## After a release

- [ ] Verify installation instructions against the published release.
- [ ] Verify the repository landing page and About metadata render correctly for the release.
- [ ] Watch CI/issues for upgrade regressions.
- [ ] Triage new defects with Graphify + `BUG_TRIAGE_AND_FIXING.md` instead of
      applying speculative hotfixes.
- [ ] Confirm the checked-in graph still represents the released baseline; if a
      graph refresh intentionally follows the release commit, keep that provenance clear.
- [ ] Open follow-up issues instead of silently carrying unfinished release or presentation work.
