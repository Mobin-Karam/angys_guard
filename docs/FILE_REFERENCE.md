# File reference

This is the repository ownership map: use it to find the module, documentation,
test area, or AI workflow that owns a behavior. Current source remains
authoritative when an old note or generated graph disagrees.

Generated caches, `.git`, `.venv`, local runtime data, and local
`graphify-out/` artifacts are not product source.

## Root and operations

| File | Responsibility |
|---|---|
| `.gitignore` | Excludes local environments, caches, credentials/secrets, media, logs, and runtime artifacts. |
| `LICENSE` | Project licensing terms. |
| `pyproject.toml` | Package metadata, Python requirement, runtime/test dependencies, console entry point, package discovery, and media package data. |
| `requirements.txt` | Installer-compatible runtime dependency list. |
| `install.sh` | Creates the virtual environment and installs dependencies. |
| `run.sh` | Secure launcher; selects virtual-environment Python and delegates to the package CLI. |
| `doctor.sh` | Convenience launcher for dependency/configuration readiness checks. |
| `repair-opencv.sh` | Repairs conflicting OpenCV variants for person/HOG compatibility. |
| `AGENTS.md` | Authoritative repository-wide AI/Codex instructions, architecture guardrails, task routing, and validation rules. |
| `AGENT.md` | Compatibility pointer; `AGENTS.md` remains authoritative. |
| `CLAUDE.md` | Claude-oriented compatibility entry that defers to `AGENTS.md`. |
| `GEMINI.md` | Gemini-oriented compatibility entry that defers to `AGENTS.md`. |
| `CONTRIBUTING.md` | Human contribution, branch, feature/bug, PR, testing, documentation, and vulnerability workflow. |
| `SECURITY.md` | Repository vulnerability-reporting policy. |
| `CHANGELOG.md` | Shipped/released changes; do not use for planned roadmap work. |

A project `.env` is not required by the current runtime and must not be committed.
Runtime secrets belong in protected user configuration storage described in
`docs/CONFIGURATION.md`.

## GitHub repository automation

| Path | Responsibility |
|---|---|
| `.github/workflows/ci.yml` | Python CI matrix, installation, compile checks, and pytest. |
| `.github/workflows/repository-safety.yml` | Rejects tracked secret files/private-key material and protects repository hygiene. |
| `.github/dependabot.yml` | Dependency update configuration. |
| `.github/CODEOWNERS` | Review ownership for repository/security-sensitive areas. |
| `.github/pull_request_template.md` | PR testing/security/configuration/manual-validation checklist. |
| `.github/ISSUE_TEMPLATE/` | Structured bug, feature, documentation, help, and security-report routing forms. |
| `.github/copilot-instructions.md` | GitHub Copilot repository instructions; defers to `AGENTS.md`. |
| `.github/instructions/` | Path-scoped Copilot rules for runtime/tests. |
| `.github/REPOSITORY_SETTINGS.md` | Settings/branch-protection/security features that must be configured in GitHub UI. |

## Codex / AI workspace

| Path | Responsibility |
|---|---|
| `.codex/config.toml` | Project-local Codex configuration and custom subagent registry. |
| `.codex/agents/architect.toml` | Read-only architecture/dependency/change planner. |
| `.codex/agents/implementer.toml` | Focused implementation role. |
| `.codex/agents/reviewer.toml` | Read-only correctness/regression reviewer. |
| `.codex/agents/security_reviewer.toml` | Read-only trust-boundary/security/privacy reviewer. |
| `.codex/agents/tester.toml` | Test selection, reproduction, CI failure triage, and verification role. |
| `.codex/agents/release_manager.toml` | Release-readiness role. |
| `.codex/hooks.json` | Session/pre-tool/post-tool Codex hook configuration. |
| `.codex/hooks/session_start.py` | Injects short project/security context at session start. |
| `.codex/hooks/pre_tool_use_policy.py` | Blocks destructive Git/repository actions and protected-secret-file access. |
| `.codex/hooks/post_edit_review.py` | Adds verification/security-review reminders after relevant edits. |
| `.codex/README.md` | AI workspace layout, trust, roles, and hook explanation. |
| `.agents/skills/issue-to-pr/SKILL.md` | GitHub issue to bounded branch/PR workflow. |
| `.agents/skills/safe-implementation/SKILL.md` | Security-preserving product implementation workflow. |
| `.agents/skills/security-review/SKILL.md` | Trust-boundary review workflow. |
| `.agents/skills/test-and-verify/SKILL.md` | Progressive automated/manual verification workflow. |
| `.agents/skills/release-readiness/SKILL.md` | Release readiness and blocker workflow. |
| `.agents/README.md` | Project skill index and maintenance rules. |

## Documentation

| File | Responsibility |
|---|---|
| `docs/README.md` | Product entry point and task-oriented documentation index. |
| `docs/FEATURE_LIFECYCLE.md` | Canonical add/change/fix/remove-feature process, migration/removal checklist, and AI recipes. |
| `docs/BUG_TRIAGE_AND_FIXING.md` | Canonical symptom-to-root-cause bug/issue investigation and repair playbook. |
| `docs/AI_AGENT_WORKFLOW.md` | Codex agents/skills/hooks and task-specific AI handoff recipes. |
| `docs/EXTENDING.md` | Focused feature-module template and extension contracts. |
| `docs/SYSTEM_AUDIT.md` | Architecture, control/data flows, current behavior, risks/findings, and evidence boundary. |
| `docs/CONFIGURATION.md` | Setup, persisted paths, defaults, secret handling, migration, and service preparation. |
| `docs/SECURITY.md` | Product trust model, authorization, protected exit, privacy, and residual risks. |
| `docs/TESTING.md` | Automated checks and target-device/manual validation requirements. |
| `docs/ROADMAP.md` | Planned milestones/issues and execution order. |
| `docs/MAINTAINER_CHECKLIST.md` | Repository/release maintenance checklist. |
| `docs/GITHUB_SETUP.md` | GitHub settings and repository setup guidance. |
| `docs/HISTORY.md` | Consolidated release/migration history. |
| `docs/FILE_REFERENCE.md` | This ownership/navigation map. |
| `docs/AGENTS.md` | Documentation-specific AI instructions and canonical-doc ownership rules. |

## Runtime package

### Entrypoint, configuration, and state

| File | Responsibility and status |
|---|---|
| `laptop_guard/__init__.py` | Package version/public package marker. |
| `laptop_guard/__main__.py` | Enables `python -m laptop_guard`; delegates to CLI. |
| `laptop_guard/cli.py` | Setup/run/doctor/arm/disarm/status/config/profile/events/health/test/service/autostart commands. |
| `laptop_guard/models.py` | Dataclass configuration schema and compatibility properties. |
| `laptop_guard/config.py` | TOML/secrets persistence, user paths, legacy import/migration, safe config handling. |
| `laptop_guard/runtime_config.py` | Runtime validation/repair, provider token validation, and owner pairing before startup. |
| `laptop_guard/state.py` | Atomic shared JSON runtime-state persistence. |
| `laptop_guard/runtime_state.py` | Live facade over shared persisted CLI/guard state. |
| `laptop_guard/storage.py` | Shared SQLite events and durable outbound queue. |
| `laptop_guard/events.py` | Fail-safe event logging mirrored into shared storage. |
| `laptop_guard/profiles.py` | Away/Home/Night/Testing configuration presets. |

### Main runtime and feature system

| File | Responsibility and status |
|---|---|
| `laptop_guard/guard.py` | Main orchestration: polling, authorization, features/menus, monitors, evidence, warning/lock, media, chat, TTS, lifecycle. |
| `laptop_guard/runtime_api.py` | Runtime owner-communication protocol/factory and local no-token adapter. |
| `laptop_guard/features/base.py` | Narrow feature/host protocols. |
| `laptop_guard/features/manager.py` | Conflict-safe command/callback registry plus deterministic feature lifecycle. |
| `laptop_guard/features/system_info.py` | Extracted status/system/help feature. |
| `laptop_guard/features/failed_login.py` | Journal auth-failure parsing, filtering, dedupe, event/owner alert behavior. |
| `laptop_guard/features/sound_detection.py` | Sound-triggered detection/recording feature. |
| `laptop_guard/features/__init__.py` | Public feature-system exports. |
| `laptop_guard/AGENTS.md` | Runtime-specific AI/security/architecture instructions. |

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
| `laptop_guard/audio.py` | General recording/playback/TTS support layer. |
| `laptop_guard/audio_intercom.py` | Current command-backed recording/playback and intercom manager. |
| `laptop_guard/audio_indicator.py` | Local visible microphone-activity indicator process. |
| `laptop_guard/persian_speech.py` | Lazy Persian TTS integration, bounded queue, playback. |
| `laptop_guard/chat_surface.py` | Chat event/transcript persistence and UI process management. |
| `laptop_guard/chat_window.py` | Tk fullscreen bilingual chat/notepad UI and visitor replies. |
| `laptop_guard/text_direction.py` | RTL/LTR detection/rendering helpers. |

### Warning, OS actions, monitoring, and service

| File | Responsibility and status |
|---|---|
| `laptop_guard/warning_sequence.py` | Current fullscreen warning media/player selection and cleanup. |
| `laptop_guard/warning.py` | Older warning process manager retained for compatibility/tests. |
| `laptop_guard/warning_screen.py` | UI used by older warning manager. |
| `laptop_guard/assets/warnings/countdown.mp4` | Packaged five-second warning media. |
| `laptop_guard/system_actions.py` | Current lock/unlock/suspend/reboot/shutdown and system snapshot helpers. |
| `laptop_guard/system.py` | Compact compatibility lock/unlock/notification/session helpers used by modular/CLI code. |
| `laptop_guard/exit_watchdog.py` | Detached parent-death monitor and safe-exit token behavior. |
| `laptop_guard/stop_auth.py` | Protected stop PIN hashing/verification and bounded terminal input. |
| `laptop_guard/health.py` | System health snapshot/change monitoring. |
| `laptop_guard/usb_monitor.py` | USB event watcher. |
| `laptop_guard/privacy_light.py` | Best-effort camera indicator discovery/follow behavior; never suppresses active capture indication. |
| `laptop_guard/service.py` | systemd user-service/autostart management. |
| `laptop_guard/setup_wizard.py` | Guided/resumable configuration, device discovery, and owner pairing. |
| `laptop_guard/doctor.py` | Required/optional dependency/configuration/backend readiness diagnostics. |
| `laptop_guard/tests_manual.py` | Hardware/integration checks exposed through `./run.sh test`. |

## Tests

Tests live under `tests/` and inherit `tests/AGENTS.md`.

The suite includes coverage for configuration/defaults/migrations, setup
checkpoints, providers and Bale serialization, feature registration/conflicts,
runtime API/state, service/autostart, event/outbox persistence, failed-login
monitoring, camera capability fallback, input privacy, screen parsing/capture,
warning behavior/assets, Persian TTS, text direction, stop authorization, app
allowlisting, local control API, chat persistence, AI workspace configuration,
and Codex hook policy.

Use test names and the owning runtime module together when triaging a failure;
`docs/BUG_TRIAGE_AND_FIXING.md` explains the workflow.

## Generated architecture/navigation data

`graphify-out/graph.json`, when present and current, may be used by humans/agents
to narrow cross-file navigation. It is not authoritative over current source and
should not be treated as executable product code.
