# Changelog

All notable shipped/repository changes should be recorded here. Planned product work belongs in the roadmap and issues, not in a release section as if already available.

The project uses semantic-style versioning where practical:

- **Patch**: fixes and compatible hardening.
- **Minor**: compatible features and UX improvements.
- **Major**: breaking behavior, configuration, or compatibility changes.

## Unreleased

### Provider-scoped bot credentials

- Split remote bot credentials into `telegram_bot_token` and `bale_bot_token` so selecting one provider can never automatically validate or overwrite the other provider's saved credential.
- Added conservative migration for the historical shared `bot_token`: completed setups migrate to their already-known provider, while incomplete/ambiguous setups quarantine it as `legacy_bot_token` instead of guessing.
- Updated setup, runtime startup, Doctor, manual provider tests, runtime Guard reconnects, and owner pairing to request only the selected provider's credential.
- Runtime diagnostic sanitization now redacts every saved Telegram/Bale/legacy bot token in addition to the local API token.
- Added regressions for Bale/Telegram credential coexistence, provider switching, completed legacy migration, pending legacy quarantine, and cross-provider non-reuse.

### Provider credential validation recovery

- Provider validation now distinguishes actual credential rejection from network/proxy/TLS/API-response failures instead of treating every failure as a bad token.
- Guided setup preserves an existing stored bot token when connectivity cannot verify it and pauses the provider section with network/proxy/API-base recovery guidance instead of looping for replacement secrets.
- Newly entered credentials are saved only after successful provider validation; transient connectivity failures do not save the candidate token and do not repeatedly prompt for another one.
- HTTP provider failures use token-safe typed errors so Doctor and manual provider tests can give credential-vs-connectivity guidance without exposing token-bearing request URLs.
- Added offline regressions for Telegram authentication rejection, transport failure, custom API-base 404 behavior, setup non-looping behavior, and secret preservation.

### Release qualification and support policy

- Defined Ubuntu Desktop 24.04 LTS amd64 as the v12.0 primary release-qualification target, with Ubuntu 22.04 and 26.04 remaining best-effort/candidate until separately qualified.
- Limited the v12.0 release-supported Python matrix to the CI-tested Python 3.11, 3.12 and 3.13 range; newer Python versions remain best effort until added to release validation.
- Documented separate GNOME X11 and GNOME Wayland capability limits for input monitoring, screenshots and screen recording instead of treating all Linux desktop sessions as equivalent.
- Added a canonical clean-machine release checklist covering install, resumable setup, Doctor, provider pairing, camera, microphone/audio, input, screen capture, lock/protected stop, service/autostart, offline queue/reconnect, update and rollback.
- Added measurable v12.0 exit criteria plus semantic versioning/changelog/tag rules.
- Added safe bug-report guidance for the token-sanitized runtime diagnostic log while warning that filesystem paths, hostnames, IP addresses and other personal metadata still require manual review/redaction.
- Added regression tests that keep the support matrix, release gates, diagnostics rules and checklist links from silently drifting.

### Production-readiness regression coverage

- Added an offline first-run regression that executes the complete guided setup in local mode with temporary private config/state paths and mocked hardware/systemd boundaries.
- Added mocked provider validation and owner-pairing regressions that require no real Bale/Telegram credential or live network service.
- Expanded service/autostart coverage for safe user-unit generation, incomplete-setup refusal, persisted enable/disable state, and uninstall/reload behavior.
- Added a CLI registration smoke test for every supported subcommand.
- Made CI run on every push plus pull requests to `main` across Python 3.11, 3.12, and 3.13, with a stable `Release gate` job that fails unless the full supported-Python matrix passes.
- Documented `Release gate` and `repository-safety` as the status checks to require in GitHub branch protection/rulesets.

### Guided runtime recovery

- Added a shared runtime-recovery layer that maps expected provider, hardware/backend, and permission failures to short explanations plus concrete test/reconfigure/doctor actions.
- Added configured-capability startup preflight for camera, audio, input monitoring, screen capture, failed-login journal access, and screen-lock backends before Guard startup.
- Provider credential/network failures no longer echo raw HTTP/provider exception text at the CLI or manual bot-test boundary.
- Unexpected runtime/background defects are retained in an owner-only JSONL diagnostic log with stored bot/API credentials and token-bearing bot URLs redacted.
- Camera/input/audio background failures now emit safe recovery guidance while preserving sanitized diagnostics for advanced troubleshooting.
- Added regressions for credential redaction, provider recovery, camera readiness, permission guidance, unexpected-defect logging, and manual provider testing.

### Resumable setup and reconfiguration

- Split guided setup into independently checkpointed identity/profile, provider, owner pairing, camera, audio, security, communication, screen capture, apps/API, monitors, and startup sections.
- Interrupted setup now validates saved checkpoints and resumes at the first incomplete or invalid section instead of replaying the whole wizard.
- Added `./run.sh reconfigure [section]` so one setup area can be changed later without redoing unrelated sections.
- Existing valid bot credentials are validated and reused without printing stored tokens; changing provider invalidates owner pairing, while profile changes invalidate only affected camera/security/monitor sections.
- Reused doctor readiness helpers for section validation and keep setup checkpoint metadata in an owner-only local progress file separate from secrets.

### Guided local operation

- Added a simple interactive main menu for TTY launches with Setup, Start Guard, Arm, Disarm, Status, Test Hardware, Doctor, Autostart, Events and Exit actions.
- The menu shows configured/not-configured, armed/disarmed and provider connected/offline state before each choice, retries invalid input, and returns after normal actions.
- Kept all existing CLI subcommands unchanged for advanced users and scripts; non-interactive no-argument launches continue to start the Guard directly.
- Limited confirmations to security-sensitive choices such as disarming protection, disabling autostart, and the desktop-lock hardware test.
- Added CLI regressions for interactive/non-interactive dispatch, backward-compatible subcommands, status indicators, invalid input, confirmations and return-to-menu behavior.

### Setup, installation, and diagnostics hardening

- Expanded `./run.sh doctor` into grouped required/recommended/optional readiness checks with a concise final READY/NOT READY summary.
- Added actionable recovery steps for required Python/venv, configuration, secret-permission, bot/pairing, camera, microphone, lock, screen-capture, journal, and autostart failures.
- Doctor now makes the exit code depend only on required checks for the configured feature set and deliberately suppresses provider exception text that could contain bot tokens.
- Added focused doctor regressions for blocking vs non-blocking failures, secret permissions, token-safe connectivity errors, and configured-feature recovery actions.
- Made `install.sh` detect Python 3.11+ and matching `venv` support before creating the environment, with exact Ubuntu package recovery guidance.
- Added bounded APT mirror/repository diagnostics and recommended Ubuntu package checks without exposing raw Python tracebacks.
- Made installer reruns idempotent, staged replacement environments safely, restored a previous working `.venv` after failed replacement installs, and preserved fresh failed environments for retry.
- Added explicit PASS/FAILED summaries and only show setup/doctor next steps after `pip check` confirms the environment is usable.
- Added focused offline installer regression tests for fresh install, missing `venv`, reruns, dependency failure, and rollback behavior.

### Audio security and communication

- Added opt-in, armed-mode sound-level detection that discards idle samples and sends one bounded recording to the authorized owner after a configurable trigger.
- Kept owner voice playback one-way unless the owner explicitly starts `/voicechat`, and pause sound detection during playback to prevent echoing that message back.
- Added duration, sensitivity, consecutive-trigger, cooldown, incoming-size and local privacy-notification safeguards. Linux microphone/backend and live Bale delivery still require target-device validation.

### AngysGuard brand system

- Established **owner-controlled endpoint security and device protection platform** as the preferred AngysGuard product category; explicitly avoid an antivirus claim until a real maintained malware-detection engine exists.
- Added the canonical winged-A / halo / shield-lock identity, dark/light wordmarks, monochrome mark, app-icon source and README hero under `docs/assets/brand/`.
- Added explicit SVG icon exports for 16, 20, 24, 32, 48, 64, 96, 128, 180, 192, 256, 512 and 1024 pixel targets plus `scripts/generate_brand_assets.py` for PNG/favicon/social-preview rendering.
- Added `docs/BRAND_GUIDE.md` with palette, usage rules and official GNOME/freedesktop/Windows/Android/GitHub design references.
- Updated the repository overview image to include the AngysGuard logo and product category.
- Added `$brand-assets`, `design-or-refresh-brand.prompt.md`, repository-presentation integration and `tests/test_brand_assets.py` so future brand/release changes remain synchronized.

### AngysGuard product/platform planning

- Introduced **AngysGuard — Angel of System Guard** as the planned public product identity while retaining current `laptop-guard` / `laptop_guard_v3` compatibility identifiers until a safe migration is implemented.
- Added canonical product vision, platform-support matrix, and local/Bale/Telegram/self-hosted/managed control-mode documentation.
- Documented Linux as the current reference platform, Windows and Android companion apps as planned targets, Android protected-device mode as research, and a structured path for users to request other OSes/devices.
- Added the Platform / OS request GitHub issue form and declarative platform/mobile/desktop-app/managed-service labels.
- Added future milestones for v13.0 self-hosted UX/Linux app, v14.0 optional managed control, and long-horizon Windows/Android platform expansion.
- Added roadmap issues #30-#42 for branding, platform support, Linux/Windows/Android apps, self-hosted pairing, managed service, passwordless device authorization, multi-device control, and Bale/Telegram parity.
- Added proposed ADRs for passwordless device pairing/local privilege separation and cross-platform capability adapters.
- Added `product_planner`, `$product-roadmap-maintenance`, and `update-product-roadmap.prompt.md` so future roadmap/support/control-mode changes remain synchronized with issues/milestones/README.
- Established a hard future-design boundary: the protected device's OS password is never sent through Bale, Telegram, mobile clients, or the AngysGuard managed backend and is not treated as a normal environment-variable credential.

### Repository presentation

- Added a full root `README.md` landing page with product overview, capabilities, security boundaries, architecture/flow diagrams, quick start, commands, repository map, testing, docs, roadmap, contributing, and license guidance.
- Added `docs/assets/laptop-guard-overview.svg` as the repository overview visual and updated it for the AngysGuard current/future product direction.
- Added canonical `.github/repository-profile.json` metadata for GitHub About description/topics/social-preview source.
- Updated package metadata so the root README is the package landing document and package description/URLs align with repository presentation.
- Added `.gitattributes` Linguist rules so generated Graphify HTML/JSON do not dominate GitHub language statistics.
- Added `docs/README_MAINTENANCE.md`, `repository_curator`, `$repository-presentation`, reusable presentation prompt, workflow integration, and regression tests to keep README/About/version/docs/platform/control claims synchronized.

### Developer and AI navigation

- Made Graphify the default repository-discovery/navigation layer for humans and AI agents before broad source reads/searches.
- Added canonical Graphify freshness, query/path/explain, source-verification, token/context, and fallback guidance.
- Added a read-only Codex `navigator` role and reusable `graphify-navigation` skill/prompt.
- Updated Codex, Copilot, Claude, Gemini, scoped AGENTS, feature/bug workflows, tests, review/security/release roles, and contribution docs to use Graphify-first discovery.
- Codex SessionStart now reports Graphify freshness and post-edit guidance reminds maintainers to refresh the graph after material relationship changes.
- Added regression tests that protect the cross-tool Graphify navigation policy.

### Planned

See `docs/ROADMAP.md`, `docs/PROJECT_MANAGEMENT.md`, `docs/ANGYSGUARD_PRODUCT_VISION.md`, `docs/PLATFORM_SUPPORT.md`, and `docs/architecture/EVOLUTION_PLAN.md` for v11.2, v11.3, v12.0, v13.0, v14.0, platform-expansion, and architecture work. These entries are planning targets, not current support claims.

## 11.1.0 — 2026-09-12

First formal GitHub release checkpoint for the existing 11.1.0 Linux-first product baseline.

### Repository and project management

- Added GitHub Actions CI for supported Python versions.
- Added repository safety checks to prevent common local secret files and private keys from being committed.
- Added Dependabot configuration for Python and GitHub Actions dependencies.
- Added issue forms, pull request checklist, CODEOWNERS, security policy, and contribution workflow.
- Removed the tracked `.env` file from the current branch and added ignore rules for local secrets/runtime artifacts.
- Added declarative repository-management configuration for labels, milestones, issue metadata, release notes, and the `v11.1.0` GitHub release/tag bootstrap.
- Defined the GitHub Project v2 fields, views, workflow states, and initial issue mapping.

### AI-assisted engineering

- Added authoritative `AGENTS.md` instructions with scoped runtime/test/docs guidance.
- Added project-local Codex roles, reusable skills, safety hooks, and cross-tool AI compatibility instructions.
- Added an evergreen `.github/prompts/` engineering prompt library.
- Added feature-lifecycle, bug-triage, testing, and AI-agent maintenance playbooks.

### Architecture baseline

- Added the canonical modular-monolith / ports-and-adapters architecture guide.
- Added dependency-boundary rules, security/runtime flow diagrams, staged architecture evolution plan, and ADR framework.
- Added architecture backlog issues for intrusion orchestration, provider consolidation, durable delivery, compatibility-facade convergence, retention policy, and dependency-boundary enforcement.

### Security note

The repository no longer expects a tracked project `.env`, but any real credential that may have existed in historical commits must still be rotated before credential-cleanup work is considered complete.
