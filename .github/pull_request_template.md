## Summary

Describe what changed and why.

## Related work

Closes #

## Type of change

- [ ] Bug fix
- [ ] Feature
- [ ] Security hardening
- [ ] Installation/setup improvement
- [ ] Documentation / repository presentation
- [ ] Refactor/maintenance

## Discovery / scope

- [ ] Graphify was used first for non-trivial repository discovery, or the narrow fallback reason is documented below.
- [ ] The owning source/tests/docs and change boundary were identified before broad edits.

## Validation

- [ ] `python -m pytest -q` passes locally, or the reason it cannot run is documented below.
- [ ] No tokens, chat IDs, private screenshots, recordings, or other secrets are included.
- [ ] Setup/config migration impact was considered.
- [ ] Linux/Wayland/X11 behavior was considered where relevant.
- [ ] User-facing errors remain understandable for non-technical users.
- [ ] Security/privacy impact was reviewed where applicable.

## Repository presentation

For a release/version bump or a material change to user-visible features, commands,
setup/platform requirements, security boundaries, or repository structure:

- [ ] `README.md` still describes current shipped behavior accurately.
- [ ] README version/status matches `pyproject.toml` / release state.
- [ ] `.github/repository-profile.json` About description/topics are still correct.
- [ ] `docs/README.md` and other canonical navigation docs are current.
- [ ] The overview visual was updated only if the high-level product flow changed.
- [ ] `tests/test_repository_presentation.py` passes.
- [ ] If none apply, the change does not materially affect repository presentation.

See `docs/README_MAINTENANCE.md` / `$repository-presentation`.

## Manual checks

List any setup, camera, microphone, provider, lock, service, autostart, UI, GitHub
About/social-preview, or target-device checks performed or still required.

## Risk / rollback

Describe security impact, possible regressions, stale-documentation risk where
relevant, and how to roll back if necessary.
