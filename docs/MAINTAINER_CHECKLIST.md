# Maintainer Checklist

Use this as the short operational checklist for repository maintenance. Detailed
procedures live in:

- `FEATURE_LIFECYCLE.md` for add/change/fix/remove feature work;
- `BUG_TRIAGE_AND_FIXING.md` for issue/bug investigation and repair;
- `TESTING.md` for automated/manual validation;
- `AI_AGENT_WORKFLOW.md` for Codex agents/skills and task recipes.

## Every pull request

- [ ] Scope is clear and linked to an issue when appropriate.
- [ ] Task followed the feature-lifecycle or bug-triage workflow as applicable.
- [ ] No secrets or private evidence are included.
- [ ] CI passes, including documentation/AI workspace regression tests.
- [ ] Repository Safety passes.
- [ ] Security/privacy impact was considered.
- [ ] Setup/config migration impact was considered.
- [ ] Feature removal checked stale commands/config/docs/tests/migrations where applicable.
- [ ] User-facing errors remain actionable.
- [ ] Regression tests were added/updated for bug fixes where practical.
- [ ] Tests/docs were updated where behavior changed.
- [ ] Target-device validation is listed separately when CI cannot prove it.
- [ ] `FILE_REFERENCE.md` was updated if file ownership/layout materially changed.

## Weekly

- [ ] Review open P0/P1 issues.
- [ ] Review Dependabot PRs and alerts.
- [ ] Review failed Actions runs and recurring/flaky failures.
- [ ] Check the project tracker and move the next highest-value issue forward.
- [ ] Confirm no credential/security issue is waiting without an owner.
- [ ] Check newly reported bugs have reproduction/evidence or a clear next diagnostic.
- [ ] Check recently added features have docs/tests and no duplicate legacy path was left behind.

## Before a release

- [ ] Release milestone/checklist is complete.
- [ ] `$release-readiness` / release-manager review has no unresolved blocker.
- [ ] Full tests pass on the supported Python range.
- [ ] Documentation link/index checks pass.
- [ ] Repository Safety passes on the release commit.
- [ ] Clean-machine install succeeds.
- [ ] Setup, doctor, provider pairing, camera, microphone, locking, service/autostart, and offline behavior are validated as applicable.
- [ ] Known P0/P1 regressions are resolved or explicitly block the release.
- [ ] `CHANGELOG.md` is updated with shipped behavior only.
- [ ] `pyproject.toml` version is correct.
- [ ] Known platform/session limitations are documented.
- [ ] Any previously exposed credentials have been rotated.
- [ ] Release tag points to the exact tested commit.

## After a release

- [ ] Verify installation instructions against the published release.
- [ ] Watch CI/issues for upgrade regressions.
- [ ] Triage new defects with `BUG_TRIAGE_AND_FIXING.md` instead of applying speculative hotfixes.
- [ ] Open follow-up issues instead of silently carrying unfinished release work.
