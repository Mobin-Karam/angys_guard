# File reference

This is the curated repository ownership map. For live callers, dependencies,
connections, tests, and change impact, use **Graphify first** as defined in
`docs/GRAPHIFY_NAVIGATION.md`, then use this file for human-maintained ownership
context. Current source remains authoritative when a note or generated graph
disagrees.

Generated caches, `.git`, `.venv`, local runtime data, and local
`graphify-out/` artifacts are not product runtime source.

## Root and operations

| File | Responsibility |
|---|---|
| `README.md` | Primary GitHub/package landing page: product purpose, capabilities, security boundaries, architecture, quick start, operations, testing, docs, roadmap, contribution and maintenance routing. |
| `.gitattributes` | GitHub Linguist/generated-asset rules; keeps Graphify-generated HTML/JSON from dominating language statistics. |
| `.gitignore` | Excludes local environments, caches, credentials/secrets, media, logs, and runtime artifacts. |
| `LICENSE` | MIT project licensing terms. |
| `pyproject.toml` | Package metadata, version, root README source, Python requirement, runtime/test dependencies, console entry point, package discovery, media package data, keywords and project URLs. |
| `requirements.txt` | Installer-compatible runtime dependency list. |
| `install.sh` | Creates the virtual environment and installs dependencies. |
| `run.sh` | Secure launcher; selects virtual-environment Python and delegates to the package CLI. |
| `doctor.sh` | Convenience launcher for dependency/configuration readiness checks. |
| `repair-opencv.sh` | Repairs conflicting OpenCV variants for person/HOG compatibility. |
| `AGENTS.md` | Authoritative repository-wide AI/Codex instructions, Graphify-first navigation, architecture/security guardrails, repository-presentation triggers, task routing, and validation rules. |
| `AGENT.md` | Compatibility pointer; `AGENTS.md` remains authoritative. |
| `CLAUDE.md` | Claude-oriented compatibility entry that defers to `AGENTS.md` and Graphify navigation policy. |
| `GEMINI.md` | Gemini-oriented compatibility entry that defers to `AGENTS.md` and Graphify navigation policy. |
| `CONTRIBUTING.md` | Human contribution workflow including Graphify-first discovery, architecture, feature/bug work, repository presentation, PR/testing/docs and vulnerability handling. |
| `SECURITY.md` | Repository vulnerability-reporting policy. |
| `CHANGELOG.md` | Shipped/released changes; do not use for planned roadmap work. |

A project `.env` is not required by the current runtime and must not be committed.
Runtime secrets belong in protected user configuration storage described in
`docs/CONFIGURATION.md`.

## GitHub repository automation and presentation

| Path | Responsibility |
|---|---|
| `.github/workflows/ci.yml` | Python CI matrix, installation, compile checks, and pytest. |
| `.github/workflows/repository-safety.yml` | Rejects tracked secret files/private-key material and protects repository hygiene. |
| `.github/workflows/repository-management-bootstrap.yml` | Applies declarative labels, milestones, issue metadata, and release baseline configuration. |
| `.github/repository-management/` | Declarative label/milestone/issue/release management configuration. |
| `.github/repository-profile.json` | Canonical GitHub About description, topics, social-preview source and presentation metadata. |
| `.github/dependabot.yml` | Dependency update configuration. |
| `.github/CODEOWNERS` | Review ownership for repository/security-sensitive areas. |
| `.github/pull_request_template.md` | PR scope/testing/security/configuration/presentation/manual-validation checklist. |
| `.github/ISSUE_TEMPLATE/` | Structured bug, feature, documentation, help, and security-report routing forms. |
| `.github/copilot-instructions.md` | GitHub Copilot repository instructions; enforces Graphify-first discovery and repository-presentation triggers while deferring policy to `AGENTS.md`. |
| `.github/instructions/` | Path-scoped Copilot rules for runtime/tests, including Graphify-first discovery. |
| `.github/prompts/` | Evergreen reusable engineering prompt library. |
| `.github/prompts/graphify-navigation.prompt.md` | Standalone Graphify-first repository-navigation/impact-mapping prompt. |
| `.github/prompts/refresh-repository-presentation.prompt.md` | Standalone README/About/version/docs/visual synchronization prompt. |
| `.github/REPOSITORY_SETTINGS.md` | Settings/branch-protection/security features that must be configured in GitHub UI. |

## Codex / AI workspace

| Path | Responsibility |
|---|---|
| `.codex/config.toml` | Project-local Codex configuration and custom subagent registry, including `navigator` and `repository_curator`. |
| `.codex/agents/navigator.toml` | Read-only Graphify-first repository navigator for owners, callers, dependencies, tests/docs, and impact mapping. |
| `.codex/agents/architect.toml` | Read-only Graphify-backed architecture/dependency/change planner. |
| `.codex/agents/implementer.toml` | Focused implementation role consuming a graph/source-confirmed scope. |
| `.codex/agents/reviewer.toml` | Read-only correctness/regression reviewer using graph-backed blast-radius discovery. |
| `.codex/agents/security_reviewer.toml` | Read-only trust-boundary/security/privacy reviewer using graph paths plus source confirmation. |
| `.codex/agents/tester.toml` | Graphify-guided test selection, reproduction, CI-failure triage, and verification role. |
| `.codex/agents/release_manager.toml` | Release-readiness role accounting for graph freshness/impact, repository presentation, and release checks. |
| `.codex/agents/repository_curator.toml` | Focused maintainer for root README, GitHub About/profile metadata, package/version references, docs navigation, and repository visual. |
| `.codex/hooks.json` | Session/pre-tool/post-tool Codex hook configuration. |
| `.codex/hooks/session_start.py` | Injects project/security context plus Graphify freshness/build status at session start. |
| `.codex/hooks/pre_tool_use_policy.py` | Blocks destructive Git/repository actions and protected-secret-file access. |
| `.codex/hooks/post_edit_review.py` | Adds verification/security-review, Graphify-refresh, and repository-presentation reminders after relevant runtime edits. |
| `.codex/README.md` | AI workspace layout, trust, roles, Graphify navigation, presentation maintenance, and hook explanation. |
| `.agents/skills/graphify-navigation/SKILL.md` | Reusable Graphify-first ownership/dependency/test/doc/change-impact workflow. |
| `.agents/skills/issue-to-pr/SKILL.md` | GitHub issue to bounded Graphify-mapped branch/PR workflow with presentation-impact accounting. |
| `.agents/skills/safe-implementation/SKILL.md` | Security-preserving product implementation workflow with graph-backed scope discovery and presentation-impact trigger. |
| `.agents/skills/security-review/SKILL.md` | Trust-boundary review workflow using Graphify paths plus source verification. |
| `.agents/skills/test-and-verify/SKILL.md` | Progressive Graphify-guided automated/manual verification workflow. |
| `.agents/skills/release-readiness/SKILL.md` | Release readiness/blocker workflow including graph freshness and repository-presentation readiness. |
| `.agents/skills/repository-presentation/SKILL.md` | README/About/package/version/docs/visual synchronization workflow verified against shipped behavior. |
| `.agents/README.md` | Project skill index and Graphify-first/repository-presentation skill baseline. |

## Documentation

| File | Responsibility |
|---|---|
| `docs/README.md` | Detailed task-oriented documentation index; links back to the root product/repository landing page and routes discovery through Graphify first. |
| `docs/GRAPHIFY_NAVIGATION.md` | Canonical graph-first discovery, freshness, query/path/explain, source verification, token/context discipline, fallback, and refresh rules for humans and AI. |
| `docs/README_MAINTENANCE.md` | Canonical root README, GitHub About/profile, package/version, docs-navigation, visual, release-trigger and presentation-verification contract. |
| `docs/assets/laptop-guard-overview.svg` | High-level repository landing-page visual showing detect → verify/evidence → respond → owner-control flow and security boundaries. |
| `docs/ARCHITECTURE.md` | Canonical architecture contract: current seams, target modular-monolith/ports-adapters structure, layer responsibilities, state/persistence/concurrency/error/security rules, and architecture review checklist. |
| `docs/architecture/BOUNDARIES.md` | Dependency/import direction and cross-layer boundary rules. |
| `docs/architecture/FLOWS.md` | Startup, owner-command, intrusion, protected-stop, delivery, evidence, and configuration flow diagrams. |
| `docs/architecture/EVOLUTION_PLAN.md` | Staged behavior-preserving architecture migration plan and phase exit criteria. |
| `docs/adr/README.md` | ADR status/process/index. |
| `docs/adr/0001-explicit-feature-registration.md` | Accepted decision: explicit feature registration; no filesystem plugin discovery. |
| `docs/adr/0002-runtime-api-port.md` | Accepted decision: runtime owner transport goes through `RuntimeApi`. |
| `docs/adr/0003-shared-runtime-state.md` | Accepted decision: shared persisted runtime control state. |
| `docs/adr/0004-layered-modular-monolith.md` | Proposed decision: incremental modular-monolith architecture with inward dependencies. |
| `docs/adr/0005-durable-owner-delivery.md` | Proposed decision: durable outbox-backed delivery for important owner notifications. |
| `docs/adr/0006-compatibility-facade-consolidation.md` | Proposed decision: converge duplicate/compatibility facades rather than adding new paths. |
| `docs/FEATURE_LIFECYCLE.md` | Canonical Graphify-first add/change/fix/remove-feature process, migration/removal checklist, and AI recipes. |
| `docs/BUG_TRIAGE_AND_FIXING.md` | Canonical Graphify-first symptom-to-root-cause bug/issue investigation and repair playbook. |
| `docs/AI_AGENT_WORKFLOW.md` | Graphify-first Codex agents/skills/hooks, repository curator/presentation flow, and task-specific handoff recipes. |
| `docs/EXTENDING.md` | Focused feature-module template and extension contracts. |
| `docs/SYSTEM_AUDIT.md` | Current architecture evidence, control/data flows, current behavior, risks/findings, and evidence boundary. It is evidence, not the target architecture contract. |
| `docs/CONFIGURATION.md` | Setup, persisted paths, defaults, secret handling, migration, and service preparation. |
| `docs/SECURITY.md` | Product trust model, authorization, protected exit, privacy, and residual risks. |
| `docs/TESTING.md` | Graphify-guided test selection, automated checks, Graphify/presentation/documentation policy regressions, and target-device/manual validation requirements. |
| `docs/ROADMAP.md` | Planned milestones/issues and execution order. |
| `docs/PROJECT_MANAGEMENT.md` | GitHub Project v2 field/view/workflow specification and repository-management conventions. |
| `docs/MAINTAINER_CHECKLIST.md` | Repository/release checklist including Graphify freshness and README/About/profile maintenance. |
| `docs/GITHUB_SETUP.md` | GitHub settings and repository setup guidance. |
| `docs/HISTORY.md` | Consolidated release/migration history. |
| `docs/FILE_REFERENCE.md` | This curated ownership/navigation map; live relationships should be discovered with Graphify first. |
| `docs/AGENTS.md` | Documentation-specific AI instructions and canonical-doc ownership rules. |

## Runtime package

### Entrypoint, configuration, and state

| File | Responsibility and status |
|---|---|
| `laptop_guard/__init__.py` | Package version/public package marker. |
| `laptop_guard/__main__.py` | Enables `python -m laptop_guard`; delegates to CLI. |
| `laptop_guard/cli.py` | Guided interactive main menu plus setup/reconfigure/run/doctor/arm/disarm/status/config/profile/events/health/test/service/autostart commands; explicit subcommands remain scriptable. |
| `laptop_guard/models.py` | Dataclass configuration schema and compatibility properties. |
| `laptop_guard/config.py` | TOML/secrets/setup-progress persistence, user paths, legacy import/migration, safe config handling. |
| `laptop_guard/runtime_config.py` | Runtime validation/repair, token-safe provider validation, and owner pairing before startup. |
| `laptop_guard/state.py` | Atomic shared JSON runtime-state persistence. |
| `laptop_guard/runtime_state.py` | Live facade over shared persisted CLI/guard state. |
| `laptop_guard/storage.py` | Shared SQLite events and durable outbound queue. |
| `laptop_guard/events.py` | Fail-safe event logging mirrored into shared storage. |
| `laptop_guard/profiles.py` | Away/Home/Night/Testing configuration presets. |

### Main runtime and feature system

| File | Responsibility and status |
|---|---|
| `laptop_guard/guard.py` | Main orchestration: polling, authorization, features/menus, monitors, evidence, warning/lock, media, chat, TTS, lifecycle, with guided monitor/provider failure boundaries. Current architecture hotspot; target evolution is documented in `docs/ARCHITECTURE.md`. |
| `laptop_guard/runtime_recovery.py` | Shared guided-recovery classification, configured-capability startup preflight, secret sanitization, and private runtime diagnostic logging. |
| `laptop_guard/runtime_api.py` | Runtime owner-communication protocol/factory and local no-token adapter. Accepted transport port. |
| `laptop_guard/features/base.py` | Narrow feature/host protocols. |
| `laptop_guard/features/manager.py` | Conflict-safe command/callback registry plus deterministic feature lifecycle. Accepted extension mechanism. |
| `laptop_guard/features/system_info.py` | Extracted status/system/help feature. |
| `laptop_guard/features/failed_login.py` | Journal auth-failure parsing, filtering, dedupe, event/owner alert behavior. |
| `laptop_guard/sound_detection.py` | Optional armed-mode volume monitor and bounded recording adapter. |
| `laptop_guard/features/__init__.py` | Public feature-system exports. |
| `laptop_guard/AGENTS.md` | Runtime-specific Graphify-first AI/security/architecture instructions. |

### Provider and local control surfaces

| File | Responsibility and status |
|---|---|
| `laptop_guard/bale_api.py` | Bale Bot API client used by current guard behavior. |
| `laptop_guard/providers/base.py` | Generic bot provider contract. |
| `laptop_guard/providers/http_bot.py` | Httpx Telegram-style provider with explicit proxy policy. |
| `laptop_guard/providers/__init__.py` | Provider factory. |
| `laptop_guard/control_api.py` | Optional loopback bearer-authenticated fixed-action HTTP API. |
| `laptop_guard/app_manager.py` | Safe allowlisted desktop application discovery/launch/termination. |

### Camera, input, screen, audio, and UI

| File | Responsibility and status |
|---|---|
| `laptop_guard/camera.py` | Motion/person/tamper camera monitoring and HOG fallback. |
| `laptop_guard/camera_devices.py` | Camera discovery/probing/device metadata. |
| `laptop_guard/input_monitor.py` | Evdev activity classification with pynput fallback; does not retain key identity. |
| `laptop_guard/screen_capture.py` | Screenshot and bounded screen-recording backends for supported Linux sessions. |
| `laptop_guard/audio.py` | General recording/playback/TTS support layer; compatibility/consolidation candidate. |
| `laptop_guard/audio_intercom.py` | Current command-backed recording/playback and intercom manager. |
| `laptop_guard/audio_indicator.py` | Local visible microphone-activity indicator process. |
| `laptop_guard/persian_speech.py` | Lazy Persian TTS integration, bounded queue, playback. |
| `laptop_guard/chat_surface.py` | Chat event/transcript persistence and UI process management. |
| `laptop_guard/chat_window.py` | Tk fullscreen bilingual chat/notepad UI and visitor replies. |
| `laptop_guard/text_direction.py` | RTL/LTR detection/rendering helpers. |

### Warning, OS actions, monitoring, and service

| File | Responsibility and status |
|---|---|
| `laptop_guard/warning_sequence.py` | Current fullscreen warning media/player selection and cleanup; active warning path. |
| `laptop_guard/warning.py` | Older warning process manager retained for compatibility/tests; new behavior should not extend it. |
| `laptop_guard/warning_screen.py` | UI used by older warning manager. |
| `laptop_guard/assets/warnings/countdown.mp4` | Packaged five-second warning media. |
| `laptop_guard/system_actions.py` | Current lock/unlock/suspend/reboot/shutdown and system snapshot helpers; active system-action path. |
| `laptop_guard/system.py` | Compact compatibility lock/unlock/notification/session helpers used by modular/CLI code; consolidation candidate. |
| `laptop_guard/exit_watchdog.py` | Detached parent-death monitor and safe-exit token behavior. |
| `laptop_guard/stop_auth.py` | Protected stop PIN hashing/verification and bounded terminal input. |
| `laptop_guard/health.py` | System health snapshot/change monitoring. |
| `laptop_guard/usb_monitor.py` | USB event watcher. |
| `laptop_guard/privacy_light.py` | Best-effort camera indicator discovery/follow behavior; never suppresses active capture indication. |
| `laptop_guard/service.py` | systemd user-service/autostart management. |
| `laptop_guard/setup_wizard.py` | Section-checkpointed guided setup/reconfiguration, validation-aware resume, device discovery, and owner pairing. |
| `laptop_guard/doctor.py` | Required/optional dependency/configuration/backend readiness diagnostics. |
| `laptop_guard/tests_manual.py` | Hardware/integration checks exposed through `./run.sh test`, with guided failure recovery and sanitized diagnostics. |

## Tests

Tests live under `tests/` and inherit `tests/AGENTS.md`.

The suite includes coverage for configuration/defaults/migrations, setup
checkpoints, providers/Bale serialization, feature registration/conflicts,
runtime API/state, service/autostart, event/outbox persistence, failed-login
monitoring, camera capability fallback, input privacy, screen parsing/capture,
warning behavior/assets, Persian TTS, text direction, stop authorization, app
allowlisting, local control API, chat persistence, AI workspace configuration,
Codex hook policy, Graphify-navigation policy, repository-presentation consistency,
and documentation link/navigation.

`tests/test_repository_presentation.py` protects root README/package version
consistency, required landing sections, About-profile metadata, curator/skill/prompt
wiring, overview visual presence, and generated Graphify Linguist rules.

Use Graphify first to locate tests connected to the affected runtime symbol/behavior;
`docs/BUG_TRIAGE_AND_FIXING.md` and `docs/TESTING.md` explain the workflow.

## Generated architecture/navigation data

Graphify outputs live under `graphify-out/` and are developer/agent navigation
artifacts, not executable product code.

- `graphify-out/GRAPH_REPORT.md` — high-level graph summary, hubs/communities, and
  recorded build commit used for freshness checks.
- `graphify-out/graph.html` — interactive human visualization.
- `graphify-out/graph.json` — machine-readable graph queried through Graphify;
  do not load it wholesale into AI/chat context for normal investigation.

Use `graphify query`, `graphify explain`, and `graphify path` to discover live
relationships, then confirm important conclusions in current source/tests. Refresh
with `graphify update .` after material relationship changes when Graphify is
available. Never manually edit generated graph data merely to make it appear fresh.
