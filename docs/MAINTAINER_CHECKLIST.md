# Maintainer Checklist

Use this as the short operational checklist for repository maintenance.

## Every pull request

- [ ] Scope is clear and linked to an issue when appropriate.
- [ ] No secrets or private evidence are included.
- [ ] CI passes.
- [ ] Repository Safety passes.
- [ ] Security/privacy impact was considered.
- [ ] Setup/config migration impact was considered.
- [ ] User-facing errors remain actionable.
- [ ] Tests/docs were updated where behavior changed.

## Weekly

- [ ] Review open P0/P1 issues.
- [ ] Review Dependabot PRs and alerts.
- [ ] Review failed Actions runs.
- [ ] Check the project tracker and move the next highest-value issue forward.
- [ ] Confirm no credential/security issue is waiting without an owner.

## Before a release

- [ ] Release milestone/checklist is complete.
- [ ] Full tests pass on the supported Python range.
- [ ] Clean-machine install succeeds.
- [ ] Setup, doctor, provider pairing, camera, microphone, locking, service/autostart, and offline behavior are validated as applicable.
- [ ] `CHANGELOG.md` is updated.
- [ ] `pyproject.toml` version is correct.
- [ ] Known limitations are documented.
- [ ] Any previously exposed credentials have been rotated.
- [ ] Release tag points to the exact tested commit.

## After a release

- [ ] Verify installation instructions against the published release.
- [ ] Watch CI/issues for upgrade regressions.
- [ ] Open follow-up issues instead of silently carrying unfinished release work.
