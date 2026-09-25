# Graph Report - angys_guard  (2026-09-25)

## Corpus Check
- 307 files · ~209,063 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2643 nodes · 4839 edges · 247 communities (138 shown, 54 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 184 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a4055016`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ScreenCaptureManager
- ._handle_callback
- FeatureManager
- PersianSpeechManager
- ChatWindow
- camera_devices.py
- HttpBotProvider
- RuntimeStateStore
- models.py
- Full system audit
- EventStore
- SoundDetectionMonitor
- v12.0 release qualification checklist
- docs/README.md
- AppConfig
- RuntimeApi
- InputMonitor
- test_v33_features.py
- HealthMonitor
- config.py
- AngysGuard
- get_bot_token
- Security and privacy
- AppManager
- test_runtime_recovery.py
- .start
- AngysGuard product vision
- USBMonitor
- show_fullscreen
- Views
- Release and migration history
- Legacy facade coexistence
- doctor.sh
- install.sh
- repair-opencv.sh
- run.sh
- BotProvider
- laptop-guard
- Configuration
- Extending Laptop Guard
- File reference
- Architecture
- test_first_run_regression.py
- Bug triage and fixing playbook
- launch_warning
- Security-preserving extension rules
- Guided setup and owner pairing
- Secure configuration defaults
- User-scoped storage
- Explicit feature system
- Narrow FeatureHost capabilities
- FeatureManager contract
- Feature test checklist
- Runtime transport and state boundaries
- Automated test catalog
- Runtime package catalog
- Laptop Guard modularization evolution
- Owner-controlled Linux security agent
- Capture privacy
- Owner authorization boundary
- Remote control constraints
- Residual security risks
- Evidence retention and quota gap
- Shared runtime persistence
- HTTP transport duplication
- Automated validation suite
- Target-device validation
- FeatureHost
- Feature lifecycle: add, change, fix, and remove features
- AngysGuard brand guide
- Repository presentation and README maintenance
- Contributing to Laptop Guard
- AI agent workflow
- write_runtime_diagnostic
- Architecture boundaries and dependency rules
- Unreleased
- features/__init__.py
- Prompt index
- ADR 0007: Passwordless remote device pairing and local privilege separation
- ADR 0008: Cross-platform capability adapters before OS expansion
- Architecture evolution plan
- AngysGuard platform support and targets
- AngysGuard / Laptop Guard AI / Codex instructions
- Graphify-first repository navigation
- AngysGuard / Laptop Guard documentation
- test_repository_presentation.py
- Runtime and security flows
- pull_request_template.md
- setup_wizard.py
- AngysGuard brand assets
- Codex project workspace
- tests_manual.py
- GitHub Setup Guide
- bootstrap_repository_management.py
- test_graphify_navigation_policy.py
- Repository presentation
- Documentation instructions
- Issue intake and triage
- Recommended GitHub Repository Settings
- CONTROL_MODES.md
- AngysGuard repository rename and GitHub Projects runbook
- doctor.py
- Laptop Guard v11.1.0
- Runtime code instructions
- Security Policy
- test_codex_hooks.py
- _graph_status
- ADR 0001 — Explicit feature registration
- ADR 0002 — Runtime owner-transport port
- ADR 0003 — Shared persisted runtime control state
- ADR 0004 — Layered modular monolith with ports/adapters
- ADR 0005 — Durable owner delivery for important notifications
- ADR 0006 — Consolidate compatibility facades before adding new paths
- Maintainer Checklist
- bootstrap_github_project.sh
- test_ai_workspace_config.py
- test_documentation_links.py
- Architecture Decision Records (ADRs)
- Repository management configuration
- sync_repository_profile.py
- pre_tool_use_policy.py
- app/main.py
- Test instructions
- Project AI skills
- Laptop Guard AI instructions
- CameraController
- graphify-navigation/SKILL.md
- issue-to-pr/SKILL.md
- product-roadmap-maintenance/SKILL.md
- release-readiness/SKILL.md
- safe-implementation/SKILL.md
- security-review/SKILL.md
- test-and-verify/SKILL.md
- security-advisory.md
- design-or-refresh-brand.prompt.md
- generate_brand_assets.py
- parse_failed_login
- check_tracked_secrets.py
- test_repository_secret_safety.py
- test_installer.py
- cli.py
- test_cli.py
- lib.rs
- CommandServer
- test_project_delivery_policy.py
- IdentityService
- SystemInfoFeature
- Bale and Telegram provider behavior
- DeviceProtocol
- persian_speech.py
- tauri.conf.json
- CameraMonitor
- runtime_config.py
- setup_is_complete
- main.ts
- ProviderConnectionError
- http_bot.py
- ProviderError
- test_remote_power_confirmations.py
- LaptopGuard
- RoutedCommand
- compilerOptions
- laptop_guard/service.py
- default.json
- PairingService
- configure_telegram_webhook.py
- angysguard-desktop
- test_wake_on_lan.py
- FailedLoginFeature
- WakeOnLanGateway
- DeviceCommandAgent
- AngysGuard Platform v2 Architecture Foundation
- Future mode B — AngysGuard managed bot/service
- guard.py
- Feature
- Planned managed onboarding protocol
- Models
- Platform capability contract
- Testing and validation
- build_linux_desktop_runtime.py
- runtime_recovery.py
- angys_platform/__init__.py
- DemoFeature
- test_root_entrypoint.py
- test_linux_desktop_runtime_build.py
- app/__init__.py
- CameraPrivacyLight
- onboarding_window.py
- Work board
- camera.py
- SecurityConfig
- .__init__

## God Nodes (most connected - your core abstractions)
1. `AppConfig` - 114 edges
2. `LaptopGuard` - 97 edges
3. `HttpBotProvider` - 56 edges
4. `load_config()` - 42 edges
5. `IdentityService` - 38 edges
6. `write_runtime_diagnostic()` - 35 edges
7. `collect_checks()` - 28 edges
8. `FeatureManager` - 28 edges
9. `GatewayRouter` - 27 edges
10. `save_config()` - 27 edges

## Surprising Connections (you probably didn't know these)
- `test_oversized_owner_voice_is_rejected_before_download()` --uses--> `LaptopGuard`  [INFERRED]
  tests/test_sound_detection.py → laptop_guard/guard.py
- `test_invalid_voice_falls_back()` --calls--> `AppConfig`  [INFERRED]
  tests/test_persian_tts.py → laptop_guard/models.py
- `test_tts_defaults()` --calls--> `AppConfig`  [INFERRED]
  tests/test_persian_tts.py → laptop_guard/models.py
- `test_keyboard_encoding()` --uses--> `HttpBotProvider`  [INFERRED]
  tests/test_provider_keyboard.py → laptop_guard/providers/http_bot.py
- `test_menu_status_shows_setup_arm_and_provider_state()` --calls--> `_menu_status()`  [EXTRACTED]
  tests/test_cli.py → laptop_guard/cli.py

## Import Cycles
- None detected.

## Communities (247 total, 54 thin omitted)

### Community 0 - "ScreenCaptureManager"
Cohesion: 0.19
Nodes (7): Path, Backward-compatible facade for older diagnostics/tests., ScreenCapture, ScreenCaptureManager, test_screen_manager_reports_backend_string(), test_parse_gnome_dbus_failure_is_empty(), test_parse_gnome_dbus_path()

### Community 1 - "._handle_callback"
Cohesion: 0.12
Nodes (7): inline_keyboard(), worker(), worker(), worker(), menu(), Any, Create one short-lived, action-bound power confirmation. Callback payloads are…

### Community 2 - "FeatureManager"
Cohesion: 0.18
Nodes (9): CallbackHandler, CommandHandler, FeatureConflictError, FeatureManager, ValueError, Owns deterministic command/callback routes and feature lifecycle., test_duplicate_command_is_rejected(), test_failed_feature_install_rolls_back_partial_routes() (+1 more)

### Community 3 - "PersianSpeechManager"
Cohesion: 0.11
Nodes (13): normalize_voice(), package_available(), PersianSpeechManager, synthesize(), Serialized Persian text-to-speech playback for owner messages. The third-party…, _SpeechJob, SpeechResult, test_invalid_voice_falls_back() (+5 more)

### Community 4 - "ChatWindow"
Cohesion: 0.06
Nodes (31): Direction, DirectionMode, _append(), _atomic_text(), Path, Visible local chat. Only text entered in its reply box is transmitted., # IMPORTANT: send/store logical Unicode, never visual/reversed text., SecurityChatManager (+23 more)

### Community 5 - "camera_devices.py"
Cohesion: 0.18
Nodes (18): CameraDevice, close_camera(), _decode_c_string(), discover_cameras(), _linux_capability(), open_camera(), probe_camera(), Path (+10 more)

### Community 6 - "HttpBotProvider"
Cohesion: 0.17
Nodes (7): HttpBotProvider, Any, Path, Encode the legacy tuple keyboard surface as Bot API JSON., Single active HTTP adapter for Bale and Telegram Bot APIs. ProviderProfile…, Compatibility alias for the pre-RuntimeApi provider surface., Timeout

### Community 7 - "RuntimeStateStore"
Cohesion: 0.15
Nodes (9): GuardRuntimeState, Live facade over the shared persisted runtime state. Assignments are…, Path, RuntimeState, RuntimeStateStore, test_guard_state_observes_external_cli_changes(), test_guard_state_persists_assignments(), Path (+1 more)

### Community 8 - "models.py"
Cohesion: 0.14
Nodes (13): ApiConfig, AppsConfig, ChatConfig, CommunicationConfig, MonitorConfig, ScreenConfig, StartupConfig, TTSConfig (+5 more)

### Community 9 - "Full system audit"
Cohesion: 0.07
Nodes (24): Bot webhooks, Linux desktop local-protection flow, Managed test deployment — `api.mahakaram.ir`, Operator release gate, Runflare Python PaaS, Server setup, What is deployed, Data the pilot handles (+16 more)

### Community 10 - "EventStore"
Cohesion: 0.13
Nodes (10): EventLog, Path, EventStore, OutboxItem, Path, test_event_log_roundtrip(), test_guard_events_are_visible_in_shared_sqlite_store(), Path (+2 more)

### Community 11 - "SoundDetectionMonitor"
Cohesion: 0.06
Nodes (23): AudioRecorder, Path, Local TTS for short owner messages. No cloud service is used., Record a short clip synchronously for the localhost control API., RemoteAudioPlayer, worker(), TextToSpeechPlayer, AudioConfig (+15 more)

### Community 12 - "v12.0 release qualification checklist"
Cohesion: 0.09
Nodes (23): 10. Input monitoring, 11. Screenshots and screen recording, 12. Lock and protected stop, 13. Service and autostart, 14. Offline queue and reconnect, 15. Update and rollback, 16. Sanitized diagnostics for bug reports, 17. Versioning and changelog rules (+15 more)

### Community 13 - "docs/README.md"
Cohesion: 0.09
Nodes (17): Platform client protocol boundary, AngysGuard / Laptop Guard roadmap, Architecture evolution track, Current baseline, Definition of done for every issue, Exit criteria, Hard security exit criteria, Measurable exit criteria (+9 more)

### Community 14 - "AppConfig"
Cohesion: 0.11
Nodes (25): check_bot_connectivity_detailed(), Return token-safe connectivity status plus a stable failure category., AppConfig, _check_provider_token(), _ensure_provider_token(), test_enabling_for_next_login_does_not_start_immediately(), test_startup_and_arming_are_separate_defaults(), test_chat_defaults_to_two_minutes_and_allows_visitor_reply() (+17 more)

### Community 15 - "RuntimeApi"
Cohesion: 0.12
Nodes (11): build_runtime_api(), LocalRuntimeApi, Any, Path, Protocol, Transport contract consumed by the guard runtime., No-network runtime adapter for local-only installations., RuntimeApi (+3 more)

### Community 16 - "InputMonitor"
Cohesion: 0.17
Nodes (5): InputMonitor, Detects input *activity*, never stores typed keys or button values. auto mode…, test_first_pynput_mouse_movement_triggers_immediately(), test_single_nonzero_evdev_relative_event_triggers(), test_input_monitor_has_backend_and_no_key_buffer()

### Community 17 - "test_v33_features.py"
Cohesion: 0.14
Nodes (9): Path, Launch and control the visible intrusion countdown surface. The child process…, WarningScreenManager, test_privacy_light_status_is_non_throwing(), test_v33_safe_defaults(), test_warning_manager_initially_not_visible(), FakeProc, test_warning_manager_passes_image_stages_and_notifications() (+1 more)

### Community 18 - "HealthMonitor"
Cohesion: 0.23
Nodes (6): collect_health(), HealthMonitor, HealthSnapshot, _temperature(), HealthConfig, test_health_snapshot_is_non_throwing()

### Community 19 - "config.py"
Cohesion: 0.10
Nodes (28): _apply_legacy_env(), _apply_section(), _atomic_write_private(), _coerce_like(), ensure_dirs(), load_config(), _migrate(), Any (+20 more)

### Community 20 - "AngysGuard"
Cohesion: 0.05
Nodes (38): 1. Clone, 2. Install, 3. Configure, 4. Validate, 5. Run, AI-assisted development, AngysGuard, Available today (+30 more)

### Community 21 - "get_bot_token"
Cohesion: 0.22
Nodes (20): _bot_token_key(), get_bot_token(), import_legacy_env_secrets(), Return only the credential scoped to the selected remote provider., Store one provider credential without touching another provider's token., Import the historical BALE_BOT_TOKEN into Bale's scoped secret slot., set_bot_token(), parametrize (+12 more)

### Community 22 - "Security and privacy"
Cohesion: 0.33
Nodes (6): Capture and privacy, Protected termination, Remote controls, Residual risks, Security and privacy, Trust model

### Community 23 - "AppManager"
Cohesion: 0.32
Nodes (4): AppManager, DesktopApp, Conservative GUI application manager. It uses .desktop entries rather than…, test_app_manager_respects_allowlist()

### Community 24 - "test_runtime_recovery.py"
Cohesion: 0.15
Nodes (14): cmd_run(), main(), configuration_recovery(), guidance_for_exception(), is_provider_auth_error(), BaseException, _minimal_runtime_config(), test_camera_preflight_returns_direct_recovery_actions() (+6 more)

### Community 25 - ".start"
Cohesion: 0.20
Nodes (10): LocalControlAPI, _auth(), _binary(), _body_json(), do_GET(), do_POST(), _json(), Path (+2 more)

### Community 26 - "AngysGuard product vision"
Cohesion: 0.08
Nodes (25): 1. Owner-controlled by default, 2. No generic remote shell, 3. OS passwords remain local, 4. Self-hosted remains a first-class mode, 5. Managed mode is optional, 6. Platform differences are explicit, 7. Users can influence platform targets, A. Linux today (+17 more)

### Community 28 - "show_fullscreen"
Cohesion: 0.39
Nodes (7): _load_background(), main(), _notify(), Return a PhotoImage-like object fitted to the current screen. Pillow is…, show_fullscreen(), tick(), Tk

### Community 29 - "Views"
Cohesion: 0.08
Nodes (25): 10. Platform requests, 11. Backlog, 1. Now, 2. Current product roadmap, 3. AngysGuard product future, 4. Platform expansion, 5. Managed service, 6. Self-hosted bot & providers (+17 more)

### Community 30 - "Release and migration history"
Cohesion: 0.18
Nodes (10): 11, 11.1, 3.2–3.3, 4, 5, 6, 7, 8 (+2 more)

### Community 33 - "install.sh"
Cohesion: 0.23
Nodes (23): apt_package_installed(), check_recommended_system_packages(), check_venv_support(), classify_apt_log(), cleanup(), create_or_reuse_venv(), detect_python(), diagnose_apt_health() (+15 more)

### Community 37 - "BotProvider"
Cohesion: 0.22
Nodes (4): BotProvider, Any, Path, Owner-transport port implemented by Bale/Telegram adapters.

### Community 39 - "Configuration"
Cohesion: 0.40
Nodes (5): Configuration, Configuration sections, Initial setup, Maintenance, Storage

### Community 40 - "Extending Laptop Guard"
Cohesion: 0.25
Nodes (7): Changing or removing a feature, Command feature template, Configuration and diagnostics, Extending Laptop Guard, Host capabilities, Test checklist, Transport and state

### Community 41 - "File reference"
Cohesion: 0.14
Nodes (13): Camera, input, screen, audio, and UI, Codex / AI workspace, Documentation, Entrypoint, configuration, and state, File reference, Generated architecture/navigation data, GitHub repository automation and presentation, Main runtime and feature system (+5 more)

### Community 42 - "Architecture"
Cohesion: 0.09
Nodes (23): Application layer, Architectural goal, Architecture, Architecture review checklist, Compatibility layers, Composition root, Concurrency model, Current runtime (+15 more)

### Community 43 - "test_first_run_regression.py"
Cohesion: 0.13
Nodes (11): load_setup_progress(), Return completed setup section ids without exposing configuration secrets., _configure_provider(), Path, _QuietConsole, _redirect_config_paths(), test_first_run_local_setup_completes_with_private_persistence(), prompt_ask() (+3 more)

### Community 44 - "Bug triage and fixing playbook"
Cohesion: 0.10
Nodes (21): 10. AI-agent workflows for finding and fixing bugs, 11. Verification after the fix, 12. Bug-fix completion checklist, 1. Start with evidence, not code changes, 2. Map the symptom with Graphify before broad searching, 3. Classify the failure, 4. Reproduce the smallest failing case, 5. Use canonical docs only after navigation is narrowed (+13 more)

### Community 45 - "launch_warning"
Cohesion: 0.24
Nodes (12): countdown_lock(), _build_player_command(), dismiss_warning(), launch_warning(), main(), _notification_fallback(), _notify(), play_warning_video() (+4 more)

### Community 69 - "Feature lifecycle: add, change, fix, and remove features"
Cohesion: 0.10
Nodes (20): 1. Map the existing feature neighborhood with Graphify, 2. Decide what kind of feature this is, 3. Adding a feature, 4. Changing an existing feature, 5. Fixing a feature, 6. Removing a feature safely, 7. AI-agent workflow, 8. Completion checklist (+12 more)

### Community 70 - "AngysGuard brand guide"
Cohesion: 0.11
Nodes (16): AngysGuard brand assets, Primary files, Size exports, AngysGuard brand guide, Asset folder, Avoid, Brand idea, Brand maintenance (+8 more)

### Community 71 - "Repository presentation and README maintenance"
Cohesion: 0.11
Nodes (18): 1. Establish the current shipped baseline, 2. Update the smallest affected set, 3. Keep GitHub About synchronized, 4. Verify consistency, 5. Refresh Graphify when available, Brand workflow, Canonical presentation/product surfaces, Goals (+10 more)

### Community 72 - "Contributing to Laptop Guard"
Cohesion: 0.12
Nodes (15): Architecture changes, Before starting, Branches, Bug fixes, Contributing to Laptop Guard, Documentation, Feature changes, Graphify-first discovery (+7 more)

### Community 73 - "AI agent workflow"
Cohesion: 0.12
Nodes (16): Agent handoff format, AI agent workflow, Bug workflow, Custom Codex agents, Feature workflow, First step for every repository-knowledge task: Graphify, GitHub Copilot and other agents, Hooks (+8 more)

### Community 74 - "write_runtime_diagnostic"
Cohesion: 0.14
Nodes (7): worker(), worker(), worker(), Path, Keep one camera worker alive and open the device only while enabled., Append a sanitized diagnostic record without exposing stored credentials., write_runtime_diagnostic()

### Community 75 - "Architecture boundaries and dependency rules"
Cohesion: 0.13
Nodes (14): Architecture boundaries and dependency rules, Architecture exceptions, Boundary table, Capture boundary, Current architectural seams to preserve, Current exceptions / migration areas, Dependency direction, Feature boundary rules (+6 more)

### Community 76 - "Unreleased"
Cohesion: 0.07
Nodes (29): 11.1.0 — 2026-09-12, AI-assisted engineering, AngysGuard brand system, AngysGuard product/platform planning, Architecture baseline, Audio security and communication, Bale / Telegram transport parity, Changelog (+21 more)

### Community 78 - "Prompt index"
Cohesion: 0.14
Nodes (13): Bugs and incidents, Documentation, brand, presentation and delivery, Feature lifecycle, General-purpose router, How to use, Maintenance rule, Navigate, understand and plan, Product/platform planning (+5 more)

### Community 79 - "ADR 0007: Passwordless remote device pairing and local privilege separation"
Cohesion: 0.13
Nodes (15): Add a generic remote shell and let the user run privilege commands, ADR 0007: Passwordless remote device pairing and local privilege separation, Consequences, Context, Cost, Credential model and lifecycle, Decision, High-risk action policy (+7 more)

### Community 80 - "ADR 0008: Cross-platform capability adapters before OS expansion"
Cohesion: 0.15
Nodes (12): ADR 0008: Cross-platform capability adapters before OS expansion, Capability-first behavior, Claim identical features on every OS, Consequences, Context, Cost, Decision, One runtime full of platform conditionals (+4 more)

### Community 81 - "Architecture evolution plan"
Cohesion: 0.15
Nodes (12): Architecture evolution plan, Ground rules, Phase 0 — Architecture contract (documentation), Phase 1 — Reduce `LaptopGuard` orchestration load, Phase 2 — Consolidate communication/provider adapters, Phase 3 — Consolidate system/warning/media facades, Phase 4 — Reliable delivery and storage lifecycle, Phase 5 — Refine feature/application boundaries (+4 more)

### Community 82 - "AngysGuard platform support and targets"
Cohesion: 0.15
Nodes (13): Android companion app — issue #35, Android protected-device mode — issue #36, AngysGuard platform support and targets, Cross-platform architecture rule, Current Linux requirements, Current operating-system support, Future desktop/mobile targets, GNOME X11 and Wayland support (+5 more)

### Community 83 - "AngysGuard / Laptop Guard AI / Codex instructions"
Cohesion: 0.11
Nodes (15): AI agent compatibility note, AngysGuard / Laptop Guard AI / Codex instructions, Available project agents, Available project skills, Command-output hygiene, Completion standard, Graphify-first navigation — mandatory default, Mission (+7 more)

### Community 84 - "Graphify-first repository navigation"
Cohesion: 0.17
Nodes (12): 1. Check graph availability and freshness, 2. Query before reading files, 3. Confirm with authoritative files, AI workflow, Graphify-first repository navigation, Human workflow, Maintenance rule, Security and privacy (+4 more)

### Community 85 - "AngysGuard / Laptop Guard documentation"
Cohesion: 0.18
Nodes (11): AngysGuard / Laptop Guard documentation, Architecture decisions relevant to future platforms, Control-mode summary, Current product, Current vs future, Future product, Graphify-first repository discovery, Platform summary (+3 more)

### Community 87 - "Runtime and security flows"
Cohesion: 0.20
Nodes (9): Configuration change while running, Event and owner delivery, Evidence lifecycle, Failure ordering principles, Incoming owner command, Intrusion/input alert, Protected stop, Runtime and security flows (+1 more)

### Community 88 - "pull_request_template.md"
Cohesion: 0.20
Nodes (9): Discovery / scope, Manual checks, Platform / control-mode impact, Related work, Repository presentation, Risk / rollback, Summary, Type of change (+1 more)

### Community 89 - "setup_wizard.py"
Cohesion: 0.13
Nodes (33): migrate_legacy_bot_token(), Assign one unambiguous old token only when the caller trusts the provider., _checkpoint(), _choose_camera(), _choose_section(), _configure_apps_api(), _configure_audio(), _configure_camera() (+25 more)

### Community 90 - "AngysGuard brand assets"
Cohesion: 0.22
Nodes (8): AngysGuard brand assets, Canonical sources, Handoff, Logo rule, Palette, Product/category rule, Review checklist, Workflow

### Community 91 - "Codex project workspace"
Cohesion: 0.22
Nodes (8): Agent roles, Codex project workspace, Hooks, Layout, Navigation rule, Primary instructions, Product/platform workflow, Trust

### Community 92 - "tests_manual.py"
Cohesion: 0.21
Nodes (15): camera_label(), cmd_test(), print_recovery(), Console, Path, RecoveryGuidance, lock_screen(), run_first() (+7 more)

### Community 93 - "GitHub Setup Guide"
Cohesion: 0.22
Nodes (8): 1. Synchronize the repository About panel, 2. Protect `main`, 3. Enable security features, 4. Review Actions, 5. Dependency updates, 6. Issues and pull requests, 7. Releases, GitHub Setup Guide

### Community 94 - "bootstrap_repository_management.py"
Cohesion: 0.58
Nodes (8): ensure_issue_metadata(), ensure_labels(), ensure_milestones(), ensure_release(), fail(), load_json(), main(), request()

### Community 95 - "test_graphify_navigation_policy.py"
Cohesion: 0.42
Nodes (8): test_authoritative_and_scoped_agent_instructions_are_graphify_first(), test_canonical_graphify_navigation_guide_exists_and_documents_commands(), test_checked_in_graph_report_records_build_commit(), test_codex_has_graphify_navigator_and_session_freshness_context(), test_every_codex_specialist_mentions_graphify_navigation(), test_graphify_skill_and_prompt_are_registered(), test_human_maintenance_guides_start_from_graph_navigation(), _text()

### Community 96 - "Repository presentation"
Cohesion: 0.25
Nodes (7): Canonical presentation sources, Handoff, Release/change workflow, Repository presentation, Rules, Start with Graphify, Verification

### Community 97 - "Documentation instructions"
Cohesion: 0.25
Nodes (7): Canonical architecture documents, Canonical maintenance documents, Canonical navigation document, Canonical product/platform documents, Documentation instructions, Documentation rules, Navigate documentation with Graphify first

### Community 98 - "Issue intake and triage"
Cohesion: 0.25
Nodes (7): Choose the right form, Duplicate and related issues, Issue intake and triage, Maintaining the forms, Priority guidance, Security reporting, Triage workflow

### Community 99 - "Recommended GitHub Repository Settings"
Cohesion: 0.25
Nodes (7): Issues and pull requests, Main branch protection, Recommended GitHub Repository Settings, Releases, Repository About and presentation, Secrets already committed, Security

### Community 100 - "CONTROL_MODES.md"
Cohesion: 0.17
Nodes (11): 1. Guided local menu, CLI and setup — available now, 2. Bale bot — current bot-style owner UI, 3. Telegram-style provider — current provider architecture, release validation required, 4. Local desktop/chat surfaces — available in current runtime where applicable, AngysGuard control modes: local, self-hosted bot, and managed service, Current owner interfaces, Current safety model for bot control, Future mode A — self-hosted Bale/Telegram bot (+3 more)

### Community 101 - "AngysGuard repository rename and GitHub Projects runbook"
Cohesion: 0.29
Nodes (6): AngysGuard repository rename and GitHub Projects runbook, Canonical repository name, GitHub Project v2, Project bootstrap, Rename action, Security

### Community 102 - "doctor.py"
Cohesion: 0.06
Nodes (53): Category, _audio_player_ok(), _autostart_ok(), _bot_connectivity(), _camera_ok(), _check(), check_bot_connectivity(), collect_checks() (+45 more)

### Community 103 - "Laptop Guard v11.1.0"
Cohesion: 0.29
Nodes (6): Known follow-up work, Laptop Guard v11.1.0, Product baseline, Repository and engineering baseline, Security note, Validation baseline

### Community 104 - "Runtime code instructions"
Cohesion: 0.29
Nodes (6): Design rules, Error handling, Navigate before reading broadly, Runtime code instructions, Security-sensitive areas, Testing expectations

### Community 105 - "Security Policy"
Cohesion: 0.29
Nodes (6): Reporting a vulnerability, Scope priorities, Secrets and evidence, Security Policy, Supported code, What to include

### Community 107 - "test_codex_hooks.py"
Cohesion: 0.52
Nodes (6): run_hook(), test_post_edit_escalates_sensitive_runtime_change(), test_pre_tool_hook_allows_safe_git_status(), test_pre_tool_hook_blocks_destructive_git(), test_pre_tool_hook_blocks_patch_to_env(), test_session_start_adds_project_context()

### Community 108 - "_graph_status"
Cohesion: 0.60
Nodes (5): _graph_status(), main(), CompletedProcess, Path, _run()

### Community 109 - "ADR 0001 — Explicit feature registration"
Cohesion: 0.33
Nodes (5): ADR 0001 — Explicit feature registration, Consequences, Context, Decision, Security/privacy

### Community 110 - "ADR 0002 — Runtime owner-transport port"
Cohesion: 0.33
Nodes (5): ADR 0002 — Runtime owner-transport port, Consequences, Context, Decision, Security/privacy

### Community 111 - "ADR 0003 — Shared persisted runtime control state"
Cohesion: 0.33
Nodes (5): ADR 0003 — Shared persisted runtime control state, Consequences, Context, Decision, Security/privacy

### Community 112 - "ADR 0004 — Layered modular monolith with ports/adapters"
Cohesion: 0.33
Nodes (5): ADR 0004 — Layered modular monolith with ports/adapters, Consequences, Context, Decision, Migration

### Community 113 - "ADR 0005 — Durable owner delivery for important notifications"
Cohesion: 0.33
Nodes (5): ADR 0005 — Durable owner delivery for important notifications, Consequences, Context, Decision, Security/privacy

### Community 114 - "ADR 0006 — Consolidate compatibility facades before adding new paths"
Cohesion: 0.33
Nodes (5): ADR 0006 — Consolidate compatibility facades before adding new paths, Consequences, Context, Decision, Security/privacy

### Community 115 - "Maintainer Checklist"
Cohesion: 0.33
Nodes (5): After a release, Before a release, Every pull request, Maintainer Checklist, Weekly

### Community 116 - "bootstrap_github_project.sh"
Cohesion: 0.50
Nodes (7): ensure_single_select_field(), map_area(), map_track(), set_field(), set_status_if_available(), bootstrap_github_project.sh script, status_option_available()

### Community 117 - "test_ai_workspace_config.py"
Cohesion: 0.40
Nodes (3): load_toml(), Path, test_codex_config_references_existing_custom_agents()

### Community 118 - "test_documentation_links.py"
Cohesion: 0.53
Nodes (4): _local_target(), _markdown_files(), Path, test_local_markdown_links_point_to_existing_paths()

### Community 120 - "Architecture Decision Records (ADRs)"
Cohesion: 0.40
Nodes (4): Architecture Decision Records (ADRs), Index, Rules, Status values

### Community 121 - "Repository management configuration"
Cohesion: 0.40
Nodes (4): GitHub Project v2, Managed automatically, Repository management configuration, Version/release rule

### Community 122 - "sync_repository_profile.py"
Cohesion: 0.70
Nodes (4): infer_repository(), load_profile(), main(), request()

### Community 123 - "pre_tool_use_policy.py"
Cohesion: 0.83
Nodes (3): deny(), main(), protected_patch_target()

### Community 124 - "app/main.py"
Cohesion: 0.06
Nodes (83): BaseModel, Depends, FastAPI, get, Header, Runflare-compatible root ASGI entrypoint for the managed test service. Runflare…, middleware, post (+75 more)

### Community 125 - "Test instructions"
Cohesion: 0.50
Nodes (3): Find tests with Graphify first, Test instructions, Test rules

### Community 128 - "CameraController"
Cohesion: 0.15
Nodes (8): CameraController, Thread-safe camera ON/OFF controller. This controller owns one cv2.VideoCapture…, Return True when this controller currently owns an open camera., Return the underlying VideoCapture object., Open the camera. Returns: True -> camera is ON False -> camera could not be…, Close and release the camera., Toggle camera state. Returns the new state: True = ON False = OFF, Read one frame. Returns: (False, None) when the camera is OFF.

### Community 186 - "parse_failed_login"
Cohesion: 0.29
Nodes (8): FailedLoginEvent, parse_failed_login(), Any, FakeHost, test_ignores_non_authentication_logs(), test_notifies_owner_and_deduplicates_burst(), test_parses_gdm_authentication_failure_without_password_content(), test_parses_remote_ssh_failure_address()

### Community 187 - "check_tracked_secrets.py"
Cohesion: 0.60
Nodes (4): is_blocked_path(), main(), Reject tracked local-secret filenames without reading their contents., tracked_paths()

### Community 188 - "test_repository_secret_safety.py"
Cohesion: 0.38
Nodes (5): _load_checker(), Path, test_checker_command_rejects_blocked_tracked_file(), test_current_git_index_contains_no_blocked_secret_paths(), test_secret_filename_policy()

### Community 189 - "test_installer.py"
Cohesion: 0.55
Nodes (11): _prepare_install_tree(), CompletedProcess, Path, _run(), test_failed_replacement_restores_previous_venv(), test_fresh_supported_install_ends_with_setup_and_doctor(), test_installer_is_safe_to_run_twice_with_existing_matching_venv(), test_missing_venv_reports_exact_ubuntu_package_and_mirror_help() (+3 more)

### Community 190 - "cli.py"
Cohesion: 0.19
Nodes (24): _autostart_menu(), build_parser(), cmd_arm(), cmd_autostart(), cmd_config(), cmd_desktop_status(), cmd_disarm(), cmd_doctor() (+16 more)

### Community 191 - "test_cli.py"
Cohesion: 0.14
Nodes (14): cmd_lock(), _interactive_terminal(), main(), PyInstaller entry point for the bundled Linux Laptop Guard runtime., test_all_cli_subcommands_parse_to_callable_handlers(), test_explicit_cli_subcommand_remains_backward_compatible(), test_interactive_no_argument_launch_uses_menu(), test_lock_command_reports_failure() (+6 more)

### Community 192 - "lib.rs"
Cohesion: 0.11
Nodes (52): AppHandle, Arc, Client, AgentState, apply_command(), BUNDLED_RUNTIME_DIRECTORY, BUNDLED_RUNTIME_NAME, BUNDLED_RUNTIME_VERSION (+44 more)

### Community 193 - "CommandServer"
Cohesion: 0.10
Nodes (24): CommandHandoff, Server-side signer; transport and local execution remain separate., ProviderUpdateAdapter, Parse only a narrow provider update shape into an authorized route., CommandServer, Path, ValueError, Durable server outbox; HTTP/provider adapters call this application layer. (+16 more)

### Community 194 - "test_project_delivery_policy.py"
Cohesion: 0.33
Nodes (6): _json(), Path, test_blueprint_groups_match_repository_milestones(), test_every_managed_delivery_issue_is_grouped_once(), test_project_blueprint_uses_live_and_target_repository_names(), test_project_bootstrap_syncs_only_stable_status_states()

### Community 195 - "IdentityService"
Cohesion: 0.11
Nodes (17): GatewayRouter, Server-side account/device router with no bot-token or OS-control access., IdentityService, Path, Return the active account that owns a device, if any., SQLite-backed account and device identity service. This is the first server-…, Persist a provider account link after the pairing flow authorizes it., Return the linked account for one provider identity, if present. (+9 more)

### Community 197 - "Bale and Telegram provider behavior"
Cohesion: 0.29
Nodes (7): Active transport architecture, Bale and Telegram provider behavior, Capability confidence, File downloads, Provider differences AngysGuard implements, Retry and timeout policy, Shared documented contract

### Community 198 - "DeviceProtocol"
Cohesion: 0.17
Nodes (12): CommandEnvelope, DeviceProtocol, ProtocolDenied, ValueError, Small, dependency-free signed envelope verifier for enrolled devices., Raised when an incoming managed command fails closed., Verifies finite signed requests before handing them to local policy., Device-verifiable fixed-action command protocol primitives. (+4 more)

### Community 200 - "persian_speech.py"
Cohesion: 0.13
Nodes (10): Indicator, main(), AudioIntercom, worker(), notify(), play_audio(), Path, Visible near-live voice intercom. Bale Bot API transports voice/audio messages… (+2 more)

### Community 201 - "tauri.conf.json"
Cohesion: 0.08
Nodes (23): app, security, windows, build, beforeBuildCommand, beforeDevCommand, devUrl, frontendDist (+15 more)

### Community 202 - "CameraMonitor"
Cohesion: 0.20
Nodes (3): CameraMonitor, Path, Refresh runtime structures after a profile/settings change.

### Community 205 - "runtime_config.py"
Cohesion: 0.21
Nodes (18): default_api_base(), build_provider(), _ask_valid_token(), _auth_error(), ensure_runtime_configuration(), _interactive(), _pair_owner_chat(), _provider() (+10 more)

### Community 206 - "setup_is_complete"
Cohesion: 0.19
Nodes (15): cmd_desktop_setup(), Configure the safe managed desktop profile without terminal prompts., setup_is_complete(), configure_managed_local_profile(), desktop_onboarding_status(), DesktopOnboardingError, DesktopOnboardingStatus, ValueError (+7 more)

### Community 207 - "main.ts"
Cohesion: 0.07
Nodes (40): dependencies, @tauri-apps/api, @tauri-apps/plugin-autostart, @tauri-apps/plugin-opener, devDependencies, @tauri-apps/cli, typescript, vite (+32 more)

### Community 208 - "ProviderConnectionError"
Cohesion: 0.14
Nodes (17): ProviderAuthError, ProviderConnectionError, ProviderResponseError, The remote provider rejected the configured credential., The provider could not be reached because of network/proxy/TLS transport., The provider returned an unexpected HTTP/API response., test_bot_connectivity_distinguishes_network_failure_from_bad_token(), get_me() (+9 more)

### Community 209 - "http_bot.py"
Cohesion: 0.16
Nodes (14): get_provider_profile(), ProviderProfile, Documented transport differences for a Telegram-style provider., CaptureClient, parametrize, Path, test_bale_reply_uses_reply_to_message_id(), test_get_updates_has_bounded_long_poll_contract() (+6 more)

### Community 210 - "ProviderError"
Cohesion: 0.16
Nodes (10): ABC, BaleApi, Compatibility facade over the consolidated Bale provider adapter. New code must…, ProviderError, RuntimeError, Base class for token-safe provider failures., CaptureClient, test_bale_api_is_compatibility_facade_over_active_adapter() (+2 more)

### Community 211 - "test_remote_power_confirmations.py"
Cohesion: 0.25
Nodes (9): BotConfig, callback(), confirmation_token(), FakeApi, make_guard(), test_disabled_power_command_does_not_offer_executable_confirmation(), test_expired_power_confirmation_is_rejected(), test_power_confirmation_is_action_bound_single_use_and_runs_requested_action() (+1 more)

### Community 212 - "LaptopGuard"
Cohesion: 0.10
Nodes (6): LaptopGuard, Consume a valid pending confirmation, failing closed otherwise., True when camera use is enabled at runtime., Allow the camera worker to open/reopen the webcam., Disable camera use and wait briefly for VideoCapture to be released., Toggle the camera and return the new enabled state.

### Community 213 - "RoutedCommand"
Cohesion: 0.14
Nodes (11): Turn an authorized gateway route into a device-verifiable envelope., Server-only fixed-action provider gateway boundary., GatewayDenied, ValueError, Authorize fixed provider commands before a future device-delivery adapter., Raised when a provider message is not authorized for a fixed action., An authorized command; this value deliberately has no execution behavior., Store a completed pairing link; pairing proof belongs to the caller. (+3 more)

### Community 214 - "compilerOptions"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, lib, module, moduleDetection, moduleResolution, noEmit (+5 more)

### Community 215 - "laptop_guard/service.py"
Cohesion: 0.16
Nodes (23): cmd_service(), install_service(), logs_service(), Return the fixed local runtime command for the systemd user service. Tauri sets…, Enable/disable startup at graphical user login. Laptop Guard needs the user's…, Start the already-installed user service without changing autostart., Stop the user service without deleting the owner's configuration., _service_exec_start() (+15 more)

### Community 216 - "default.json"
Cohesion: 0.33
Nodes (5): description, identifier, permissions, $schema, windows

### Community 217 - "PairingService"
Cohesion: 0.17
Nodes (9): Platform account and device identity boundary., PairingDenied, PairingService, Path, ValueError, Single-use, short-lived device pairing codes for provider account linking., Raised when a pairing code cannot safely be consumed., test_pairing_code_expires() (+1 more)

### Community 218 - "configure_telegram_webhook.py"
Cohesion: 0.67
Nodes (3): main(), Register the managed-test Telegram webhook without printing its token. Run this…, required()

### Community 220 - "test_wake_on_lan.py"
Cohesion: 0.17
Nodes (8): FakeProvider, FakeSocket, _route(), test_official_bot_dispatches_only_configured_wake_action(), factory(), test_wol_rejects_arbitrary_targets_and_revoked_or_wrong_owner_requests(), test_wol_sends_magic_packet_only_to_enrolled_owner_target(), factory()

### Community 222 - "WakeOnLanGateway"
Cohesion: 0.24
Nodes (8): Path, ValueError, Fixed, owner-authorized Wake-on-LAN dispatch for the always-on gateway., Raised when a wake request or enrolled network target is unsafe., Dispatch magic packets only to explicit, owner-bound enrolled targets., WakeDenied, WakeOnLanGateway, WakeTarget

### Community 223 - "DeviceCommandAgent"
Cohesion: 0.20
Nodes (6): CommandTransport, DeviceCommandAgent, Protocol, Verify signed commands and dispatch only the finite local action set., Device-side loop; local handlers own policy/confirmation and OS effects., Enrolled-device command consumer boundary.

### Community 224 - "AngysGuard Platform v2 Architecture Foundation"
Cohesion: 0.11
Nodes (16): Implemented routing boundary, Not yet shipped, Platform gateway boundary, Wake-on-LAN power-on slice, AngysGuard Platform v2 Architecture Foundation, Configuration Engine, Core platform boundaries, Data ownership (+8 more)

### Community 225 - "Future mode B — AngysGuard managed bot/service"
Cohesion: 0.17
Nodes (12): Computer/OS password rule — hard boundary, Future mode B — AngysGuard managed bot/service, Limited managed-test implementation, Managed service security requirements, Multi-device future, Planned power-on boundary, Provider capability parity, Related roadmap (+4 more)

### Community 226 - "guard.py"
Cohesion: 0.24
Nodes (14): bounded_callback_int(), Parse an integer callback suffix without letting malformed input crash polling., _format_duration(), _human_bytes(), lock_screen(), poweroff_system(), Best-effort owner-requested session unlock. Windows intentionally returns…, reboot_system() (+6 more)

### Community 227 - "Feature"
Cohesion: 0.29
Nodes (3): Feature, Protocol, Explicit extension point; features are registered, never auto-imported.

### Community 228 - "Planned managed onboarding protocol"
Cohesion: 0.20
Nodes (8): Command confidentiality/integrity options evaluated, Device credential and command protocol, Enrollment protocol, Minimum managed data and retention policy, Planned managed onboarding protocol, Privacy and implementation gates, Revocation and recovery, Trust boundaries

### Community 229 - "Models"
Cohesion: 0.25
Nodes (7): Current storage, Flow, Models, Platform Identity Service, sessions, users, users_devices

### Community 230 - "Platform capability contract"
Cohesion: 0.33
Nodes (5): Application-owned ports, Initial platform matrix, Migration order, Platform capability contract, Validation gates

### Community 231 - "Testing and validation"
Cohesion: 0.17
Nodes (12): Automated suite, CI failure triage, Documentation and AI-navigation regression checks, Environment-specific validation, Graphify-guided test selection, Progressive verification, Regression-test rule for bug fixes, Repository-presentation regression checks (+4 more)

### Community 233 - "runtime_recovery.py"
Cohesion: 0.23
Nodes (12): get_api_token(), get_bot_tokens(), get_legacy_bot_token(), _legacy_bot_tokens_from(), _normalize_legacy_bot_token_key(), Rename one old shared bot_token into an explicitly ambiguous legacy slot., Return one unambiguous pre-provider-scoping token without assigning it., Return all provider/legacy bot secrets for redaction only. (+4 more)

### Community 241 - "CameraPrivacyLight"
Cohesion: 0.26
Nodes (5): CameraPrivacyLight, LightStatus, Path, Best-effort control for a *separate* camera indicator exposed via sysfs. Many…, Safe indicator policy: never force the indicator dark while capturing.

### Community 242 - "onboarding_window.py"
Cohesion: 0.31
Nodes (7): cmd_onboarding(), onboarding_steps(), RTL Persian native onboarding guide for non-technical owners., Show a local informational screen; setup still owns all secret entry., show_onboarding(), test_onboarding_command_selects_provider_without_opening_window(), test_persian_onboarding_steps_explain_id_and_one_time_pairing()

### Community 243 - "Work board"
Cohesion: 0.29
Nodes (7): AngysGuard self-hosted UX, Cross-platform, Managed control, Next, Now, Production release, Work board

### Community 244 - "camera.py"
Cohesion: 0.52
Nodes (4): person_detection_capability(), CameraConfig, test_missing_hog_falls_back_without_crashing(), test_person_detector_capability_returns_tuple()

## Knowledge Gaps
- **687 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+682 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1196 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **54 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AppConfig` connect `AppConfig` to `PersianSpeechManager`, `doctor.py`, `models.py`, `runtime_recovery.py`, `write_runtime_diagnostic`, `test_first_run_regression.py`, `runtime_config.py`, `setup_is_complete`, `RuntimeApi`, `ProviderConnectionError`, `test_v33_features.py`, `config.py`, `test_remote_power_confirmations.py`, `get_bot_token`, `laptop_guard/service.py`, `test_runtime_recovery.py`, `setup_wizard.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `LaptopGuard` connect `LaptopGuard` to `ScreenCaptureManager`, `._handle_callback`, `guard.py`, `PersianSpeechManager`, `ChatWindow`, `doctor.py`, `RuntimeStateStore`, `persian_speech.py`, `EventStore`, `write_runtime_diagnostic`, `SoundDetectionMonitor`, `launch_warning`, `runtime_config.py`, `RuntimeApi`, `InputMonitor`, `test_remote_power_confirmations.py`, `test_runtime_recovery.py`, `cli.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Why does `HttpBotProvider` connect `HttpBotProvider` to `BotProvider`, `runtime_config.py`, `RuntimeApi`, `ProviderConnectionError`, `http_bot.py`, `ProviderError`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 48 inferred relationships involving `AppConfig` (e.g. with `_apply_legacy_env()` and `_migrate()`) actually correct?**
  _`AppConfig` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `LaptopGuard` (e.g. with `AudioIntercom` and `SecurityChatManager`) actually correct?**
  _`LaptopGuard` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `HttpBotProvider` (e.g. with `ProviderAuthError` and `ProviderConnectionError`) actually correct?**
  _`HttpBotProvider` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _687 weakly-connected nodes found - possible documentation gaps or missing edges._