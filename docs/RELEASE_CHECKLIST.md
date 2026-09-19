# v12.0 release qualification checklist

This document is the canonical **production-release qualification checklist** for
the current Linux-first AngysGuard / Laptop Guard product.

It complements:

- [Platform support](PLATFORM_SUPPORT.md) — what environments the project claims;
- [Testing](TESTING.md) — automated and target-device verification methods;
- [Security](SECURITY.md) — trust/privacy boundaries;
- [README maintenance](README_MAINTENANCE.md) — release/version/presentation sync.

A release is not production-ready merely because CI is green. Hardware, desktop
session, provider, service and update/rollback checks below require a real target
machine or a clean VM with the required devices/session.

## 1. v12.0 qualification target

The primary v12.0 release-qualification environment is:

| Dimension | v12.0 requirement |
|---|---|
| OS | Ubuntu Desktop **24.04 LTS** |
| Architecture | **amd64 / x86_64** |
| Python | **3.11, 3.12 or 3.13**; CI must pass all three |
| Desktop | GNOME desktop |
| Sessions | GNOME **X11** and GNOME **Wayland**, with the feature limits documented in [Platform support](PLATFORM_SUPPORT.md) |
| Init/service | systemd user session |
| Input | readable evdev devices preferred; session-compatible pynput is fallback |
| Camera | one normal user-accessible V4L2/UVC camera when camera features are claimed |
| Audio | one user-accessible microphone and playback device when audio features are claimed |
| Lock | a working supported desktop lock backend |
| Network | required only for Bale/Telegram-style provider qualification; local mode must remain usable offline |

Ubuntu 22.04 LTS and Ubuntu 26.04 LTS are **not v12.0 release-qualified targets**
until their own clean-machine records pass the same checklist with a supported
Python version. They remain best-effort/candidate environments as documented in
[Platform support](PLATFORM_SUPPORT.md).

The support promise is **configured-feature based**. A session may be supported
with a feature disabled when the current backend does not support that feature.
`./run.sh doctor` is the release-time authority for whether the selected feature
set is ready on the specific machine.

## 2. Qualification record

Create one record per tested OS/session/provider combination. Keep the record in
the release PR, release issue, or other maintainer-controlled release evidence.
Do **not** include credentials, private evidence, chat IDs, usernames, private IPs,
or raw local configuration.

```text
Release candidate/tag:
Commit SHA:
Date:
Tester:
Machine type: physical / VM
OS/version:
Architecture:
Kernel:
Python:
Desktop:
Session: X11 / Wayland
Provider mode: local / Bale / Telegram-style
Camera model (generic description only):
Microphone/backend:
Input backend:
Screen screenshot backend:
Screen video backend:
Lock backend:
systemd user service:
Doctor result:
Checklist result: PASS / BLOCKED
Known limitations / linked issues:
```

A missing required field is a release-blocking documentation gap for that claimed
environment.

## 3. Automated release gates

On the exact release commit:

- [ ] **Repository Safety** passes.
- [ ] **Release gate** passes.
- [ ] Python 3.11 compile + full pytest passes.
- [ ] Python 3.12 compile + full pytest passes.
- [ ] Python 3.13 compile + full pytest passes.
- [ ] No required check is skipped to make the release green.
- [ ] No unresolved P0 release blocker exists.
- [ ] Any unresolved P1 issue is explicitly reviewed and cannot violate a v12.0 exit criterion.

Local verification, when available:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q laptop_guard tests
bash -n install.sh run.sh doctor.sh repair-opencv.sh
.venv/bin/python -m pip check
git diff --check
```

## 4. Clean-machine install

Use a fresh Ubuntu 24.04 LTS Desktop amd64 VM or machine. Do not reuse a developer
home directory.

- [ ] Apply normal OS updates and reboot if required.
- [ ] Clone the release candidate into a fresh directory.
- [ ] Run:

```bash
chmod +x install.sh run.sh doctor.sh
./install.sh
```

- [ ] Installer ends with `Installation summary: PASS`.
- [ ] Installer does not print a Python traceback for an expected dependency failure.
- [ ] `.venv` uses a release-supported Python version.
- [ ] `.venv/bin/python -m pip check` exits zero.
- [ ] Rerunning `./install.sh` succeeds without destroying the working environment.
- [ ] Recommended package warnings are understandable and actionable.
- [ ] No credential is required during installation.

Record: **PASS / BLOCKED + issue link**.

## 5. Guided setup and secure persistence

Run:

```bash
./run.sh setup
```

- [ ] Complete every setup section.
- [ ] Interrupt setup once, rerun it, and verify it resumes from the expected section.
- [ ] Reconfigure one section and verify unrelated sections are not replayed.
- [ ] `~/.config/laptop-guard/config.toml` is mode `0600`.
- [ ] `~/.config/laptop-guard/secrets.json`, when present, is mode `0600`.
- [ ] `~/.config/laptop-guard/setup-progress.json` is mode `0600`.
- [ ] Stored provider tokens are not shown in setup output.
- [ ] Local-only mode can complete without creating a provider token.

Record: **PASS / BLOCKED + issue link**.

## 6. Doctor/readiness

Run:

```bash
./run.sh doctor
```

- [ ] Final result is `READY` for the feature set that the release claims on this environment.
- [ ] Every deliberately induced required failure produces a concrete recovery action.
- [ ] A recommended-only failure does not incorrectly mark the installation not ready.
- [ ] Doctor output contains no token, secret value or raw provider URL containing credentials.

If a session has a documented unsupported optional capability, disable that
capability through `./run.sh reconfigure <section>`, rerun Doctor, and record the
limitation rather than claiming that capability is supported.

## 7. Provider and owner pairing

Use a dedicated release-test bot/account. Never use a personal production token in
screenshots, issues, PR text or copied logs.

For each provider the release claims:

```bash
./run.sh reconfigure provider
./run.sh reconfigure owner
./run.sh test bot
```

- [ ] Valid credential is accepted and stored without echoing it.
- [ ] Invalid/expired credential produces guided recovery without exposing it.
- [ ] Owner pairing ignores stale `/start` updates and binds the intended test account.
- [ ] A message/test reaches only the paired owner.
- [ ] Local-only mode still works with no provider/network.

Record provider-specific results separately. Passing Bale does not prove Telegram
parity and vice versa.

## 8. Camera

Run:

```bash
./run.sh test camera
```

- [ ] Configured camera opens as the normal desktop user.
- [ ] A bounded test capture completes.
- [ ] Disconnect/deny access once and verify guided recovery.
- [ ] Reconnect/re-enable and verify recovery without reinstalling.
- [ ] No capture is silently hidden from the local user where the platform normally exposes privacy indicators.

Record camera model only generically; do not attach captured faces/private media to
the release issue.

## 9. Microphone and audio

Run:

```bash
./run.sh test microphone
```

- [ ] Configured microphone records the bounded test sample.
- [ ] Playback/TTS backend works when that feature is claimed.
- [ ] Denied/missing microphone produces actionable recovery.
- [ ] Sound detection remains opt-in/configured and bounded.
- [ ] No private recording is attached to release evidence.

## 10. Input monitoring

Run:

```bash
./run.sh test input
```

For each claimed session:

- [ ] The selected input backend starts.
- [ ] Keyboard/mouse **activity** is detected without storing key identities.
- [ ] If evdev is used, required device permissions are documented and verified.
- [ ] If evdev is unavailable, pynput fallback is tested only in a session where it actually works.
- [ ] Permission denial produces guided recovery rather than a raw traceback.

Wayland qualification should prefer readable evdev because compositor-global input
hooks are intentionally not bypassed.

## 11. Screenshots and screen recording

Run:

```bash
./run.sh test screen
```

### X11

- [ ] Screenshot succeeds with one supported backend.
- [ ] Screen recording succeeds through the supported X11 path when screen video is claimed.
- [ ] Generated capture is bounded and stored under the normal user data directory.

### Wayland

- [ ] Screenshot result is recorded with the actual backend.
- [ ] Screen recording is only marked supported when the compositor works with the current `wf-recorder` path.
- [ ] On GNOME Wayland or another compositor where the current recorder is unavailable, screen video is documented as unavailable and the feature is disabled for a READY configuration.
- [ ] The product does not bypass compositor/privacy controls.

Do not generalize a wlroots/`wf-recorder` success to every Wayland compositor.

## 12. Lock and protected stop

Run:

```bash
./run.sh test lock
```

Use a disposable session because the test intentionally locks the desktop.

- [ ] Normal lock succeeds.
- [ ] Intrusion warning/countdown reaches the configured lock action independently of provider/capture latency.
- [ ] Correct local stop PIN plus owner confirmation permits the protected clean stop when configured.
- [ ] Wrong PIN, denial or timeout fails closed according to configuration.
- [ ] Abrupt-process/watchdog behavior requests the expected lock.
- [ ] No OS password is transmitted through a provider or stored in ordinary environment variables.

## 13. Service and autostart

Run:

```bash
./run.sh service install
./run.sh service status
./run.sh autostart status
```

Then log out and back in.

- [ ] User service starts in the graphical session.
- [ ] Service uses the same saved configuration without interactive prompts.
- [ ] Required display/audio/session environment is available.
- [ ] `./run.sh autostart off` disables startup.
- [ ] `./run.sh autostart on` re-enables startup.
- [ ] `./run.sh service uninstall` removes the unit and reloads the user manager.
- [ ] Reinstall succeeds after uninstall.

A unit-test pass does not replace this login-session check.

## 14. Offline queue and reconnect

The automated regression `tests/test_v4_outbox.py` must pass.

For provider-enabled qualification, use a dedicated release-test account and a
controlled network/provider outage:

- [ ] Queue one non-sensitive test notification while delivery is unavailable.
- [ ] Verify it remains pending rather than being silently lost.
- [ ] Restore connectivity.
- [ ] Verify delivery succeeds and the pending count returns to zero.
- [ ] Verify retries remain bounded.
- [ ] Do not use captured private evidence for this test.

Record only counts/result and generic test text, never the provider token or owner
chat ID.

## 15. Update and rollback

Perform this on a disposable release-test account/VM, not on the maintainer's
primary installation.

### Update

- [ ] Install the previous supported release/tag and complete setup.
- [ ] Record non-secret settings and expected state.
- [ ] Switch the code checkout to the release candidate.
- [ ] Run `./install.sh`.
- [ ] Run `./run.sh doctor`.
- [ ] Confirm configuration, pairing metadata and non-secret state remain usable.
- [ ] Confirm no migration writes credentials into `config.toml`.

### Rollback

- [ ] Switch the code checkout back to the previous known-good tag.
- [ ] Rerun `./install.sh`.
- [ ] Run `./run.sh doctor`.
- [ ] Confirm the previous release can read the retained configuration/state, **or**
      document and test a specific backup/restore migration before release.
- [ ] Confirm a failed environment replacement restores the previous working
      `.venv` as covered by installer regression tests.

If a configuration migration is intentionally one-way, v12.0 cannot claim simple
rollback. The release notes must state the limitation and provide a tested backup
and restore path.

## 16. Sanitized diagnostics for bug reports

Normal user-facing recovery should start with:

```bash
./run.sh doctor
```

Unexpected defects may be recorded in:

```text
~/.local/share/laptop-guard/logs/runtime-diagnostics.jsonl
```

(or the equivalent `XDG_DATA_HOME` path).

That file is written owner-only and the runtime redacts known bot/API tokens and
token-bearing bot URLs. **It is still not guaranteed to be free of personal
metadata** such as local filesystem paths, usernames, hostnames, IP addresses, or
device names.

Safe bug-report procedure:

1. Reproduce the problem once if it is safe to do so.
2. Run `./run.sh doctor` and copy only the relevant output.
3. Locate the diagnostic file locally; do not upload the whole data directory.
4. Copy only the smallest relevant diagnostic record.
5. Manually remove usernames/home paths, hostnames, private/public IPs, device
   names, chat IDs, and any other identifying data before posting.
6. Re-check that the text contains no token, API key, PIN, password, private key,
   cookie, Authorization header, or provider URL with embedded credentials.
7. Describe captured-media behavior in words. Do **not** attach private
   camera/screen/audio evidence unless the reporter explicitly intends to share
   that specific non-sensitive test artifact.
8. Never attach or paste `secrets.json`, `stop-pin.json`, raw event databases,
   private evidence directories, or OS passwords.

Security vulnerabilities should follow the repository security-reporting process,
not a public bug issue.

## 17. Versioning and changelog rules

The project uses semantic-style versions:

- **Patch** — compatible bug fixes, hardening and documentation corrections.
- **Minor** — backward-compatible features or user-experience improvements.
- **Major** — intentionally breaking behavior/configuration/support contracts.

Release mechanics:

- [ ] `pyproject.toml` is the package-version source of truth.
- [ ] Root README current-release text matches `pyproject.toml`.
- [ ] Move shipped entries from `Unreleased` into `X.Y.Z — YYYY-MM-DD`.
- [ ] Create a fresh `Unreleased` section for subsequent work.
- [ ] Keep planned roadmap work out of released changelog sections.
- [ ] Call out security-relevant behavior changes without exposing exploit details
      that should remain private.
- [ ] Document config migrations, support-matrix changes and rollback limitations.
- [ ] Create tag `vX.Y.Z` at the exact commit that passed qualification.
- [ ] Release notes link known limitations and target-device qualification results.

## 18. Measurable v12.0 exit criteria

v12.0 is release-ready only when **all** of the following are true:

- [ ] Issues #2, #3, #6, #7 and #8 are closed by merged changes.
- [ ] `Release gate` and `repository-safety` pass on the release commit.
- [ ] No unresolved P0 release blocker exists.
- [ ] Ubuntu 24.04 LTS amd64 has a clean-machine qualification record.
- [ ] GNOME X11 and GNOME Wayland each have a recorded qualification result.
- [ ] Every feature advertised as supported on those sessions passes its relevant
      target-device check; unsupported session-specific features are explicitly
      disabled/documented.
- [ ] Local-only operation is validated without a provider.
- [ ] Every provider claimed by the release has its own pairing/connectivity record.
- [ ] Camera, microphone, input, lock and service/autostart checks pass where claimed.
- [ ] Offline queue/reconnect behavior is validated.
- [ ] Update from the previous release is validated.
- [ ] Rollback is validated or an explicit tested backup/restore limitation is
      documented in release notes.
- [ ] Platform support, README, changelog, package version and repository profile
      are mutually consistent.
- [ ] Sanitized diagnostic/reporting instructions are published and verified.
- [ ] Any remaining known limitation has a linked issue and does not contradict a
      Supported claim.

If any required item is **BLOCKED**, the v12.0 production release is blocked.
