## Summary

Describe what changed and why.

## Related work

Closes #

## Type of change

- [ ] Bug fix
- [ ] Feature
- [ ] Security hardening
- [ ] Installation/setup improvement
- [ ] Platform / desktop / mobile
- [ ] Provider / bot / managed service
- [ ] Documentation / repository presentation
- [ ] Refactor/maintenance

## Discovery / scope

- [ ] Graphify was used first for non-trivial repository discovery, or the narrow fallback reason is documented below.
- [ ] The owning source/tests/docs and change boundary were identified before broad edits.

## Validation

- [ ] `python -m pytest -q` passes locally, or the reason it cannot run is documented below.
- [ ] No tokens, chat IDs, OS passwords, private screenshots, recordings, or other secrets are included.
- [ ] Setup/config migration impact was considered.
- [ ] Platform/session behavior was considered where relevant.
- [ ] User-facing errors remain understandable for non-technical users.
- [ ] Security/privacy impact was reviewed where applicable.

## Platform / control-mode impact

If this changes OS support, Bale/Telegram behavior, self-hosted pairing, managed service, desktop/mobile apps, or remote/local authorization:

- [ ] `docs/PLATFORM_SUPPORT.md` reflects the correct state: Supported / Best effort / Planned / Research / Requested.
- [ ] `docs/CONTROL_MODES.md` remains accurate.
- [ ] Planned/research targets are not described as shipped.
- [ ] Local/self-hosted operation remains first-class unless an explicit approved product decision says otherwise.
- [ ] No protected-device OS password is sent/stored through Bale, Telegram, mobile clients, managed backend, or ordinary environment variables.
- [ ] No generic remote shell/PowerShell/Bash execution surface was introduced.
- [ ] Target-device/provider validation still required is listed below.
- [ ] If none apply, this PR does not change platform/control-mode claims.

See `docs/ANGYSGUARD_PRODUCT_VISION.md`, `docs/PLATFORM_SUPPORT.md`, `docs/CONTROL_MODES.md`, and `$product-roadmap-maintenance`.

## Repository presentation

For a release/version bump or material user-visible/platform/control/security/repository change:

- [ ] `README.md` accurately separates current vs future behavior.
- [ ] README version/status matches `pyproject.toml` / release state.
- [ ] `.github/repository-profile.json` is current.
- [ ] documentation navigation/roadmap is current.
- [ ] overview visual was updated only if high-level product direction changed.
- [ ] `tests/test_repository_presentation.py` passes.
- [ ] If none apply, the change does not materially affect repository presentation.

See `docs/README_MAINTENANCE.md` / `$repository-presentation`.

## Manual checks

List setup, camera, microphone, provider, pairing, lock, service, UI, OS/platform, GitHub About/social-preview, or target-device checks performed/still required.

## Risk / rollback

Describe security impact, regressions, migration/support/documentation risks, and rollback.
