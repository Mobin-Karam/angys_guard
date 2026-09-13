# Graph Report - laptop_guard_v3  (2026-09-13)

## Corpus Check
- 229 files · ~164,958 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1675 nodes · 2635 edges · 181 communities (140 shown, 41 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 84 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e8232d5d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- cli.py
- LaptopGuard
- FeatureManager
- guard.py
- SecurityChatManager
- CameraMonitor
- HttpBotProvider
- BaleApi
- StopPinStore
- Full system audit
- EventStore
- AudioConfig
- RuntimeStateStore
- config.py
- AppConfig
- RuntimeApi
- ScreenCaptureManager
- test_v33_features.py
- HealthMonitor
- runtime_config.py
- models.py
- README.md
- Security and privacy
- AppManager
- launch_warning
- LocalControlAPI
- setup_wizard.py
- USBMonitor
- show_fullscreen
- test_persian_tts.py
- Release and migration history
- Legacy facade coexistence
- doctor.sh
- install.sh
- repair-opencv.sh
- run.sh
- laptop-guard
- Configuration
- Extending Laptop Guard
- File reference
- Laptop Guard 11.1
- Laptop Guard agent guide
- test_config_robustness.py
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
- Feature lifecycle: add, change, fix, and remove features
- AngysGuard brand guide
- Repository presentation and README maintenance
- Contributing to Laptop Guard
- AI agent workflow
- ROADMAP.md
- Architecture boundaries and dependency rules
- Unreleased
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
- AngysGuard brand assets
- Codex project workspace
- Future mode B — AngysGuard managed bot/service
- GitHub Setup Guide
- bootstrap_repository_management.py
- test_graphify_navigation_policy.py
- Repository presentation
- Documentation instructions
- Issue intake and triage
- Recommended GitHub Repository Settings
- Current owner interfaces
- AngysGuard repository rename and GitHub Projects runbook
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
- Test instructions
- Project AI skills
- Laptop Guard AI instructions
- SKILL.md
- SKILL.md
- SKILL.md
- SKILL.md
- SKILL.md
- SKILL.md
- SKILL.md
- security-advisory.md
- design-or-refresh-brand.prompt.md

## God Nodes (most connected - your core abstractions)
1. `LaptopGuard` - 89 edges
2. `AppConfig` - 52 edges
3. `FeatureManager` - 31 edges
4. `load_config()` - 27 edges
5. `SoundDetectionMonitor` - 26 edges
6. `BaleApi` - 25 edges
7. `EventStore` - 24 edges
8. `AngysGuard` - 23 edges
9. `InputMonitor` - 22 edges
10. `AudioConfig` - 22 edges

## Surprising Connections (you probably didn't know these)
- `test_oversized_owner_voice_is_rejected_before_download()` --indirect_call--> `LaptopGuard`  [INFERRED]
  tests/test_sound_detection.py → laptop_guard/guard.py
- `test_invalid_voice_falls_back()` --calls--> `AppConfig`  [INFERRED]
  tests/test_persian_tts.py → laptop_guard/models.py
- `test_tts_defaults()` --calls--> `AppConfig`  [INFERRED]
  tests/test_persian_tts.py → laptop_guard/models.py
- `test_default_warning_sequence_is_five_seconds()` --calls--> `AppConfig`  [INFERRED]
  tests/test_config.py → laptop_guard/models.py
- `test_protected_stop_defaults()` --calls--> `AppConfig`  [INFERRED]
  tests/test_config.py → laptop_guard/models.py

## Import Cycles
- None detected.

## Communities (181 total, 41 thin omitted)

### Community 0 - "cli.py"
Cohesion: 0.12
Nodes (35): camera_label(), build_parser(), cmd_arm(), cmd_autostart(), cmd_config(), cmd_disarm(), cmd_doctor(), cmd_events() (+27 more)

### Community 1 - "LaptopGuard"
Cohesion: 0.07
Nodes (6): notify(), inline_keyboard(), LaptopGuard, main(), Any, Path

### Community 2 - "FeatureManager"
Cohesion: 0.05
Nodes (28): CallbackHandler, CommandHandler, Feature, FeatureHost, Protocol, Narrow host surface available to features., Explicit extension point; features are registered, never auto-imported., FailedLoginEvent (+20 more)

### Community 3 - "guard.py"
Cohesion: 0.05
Nodes (40): Indicator, main(), AudioIntercom, play_audio(), Path, Visible near-live voice intercom.      Bale Bot API transports voice/audio messa, record_audio(), bounded_callback_int() (+32 more)

### Community 4 - "SecurityChatManager"
Cohesion: 0.06
Nodes (30): Direction, DirectionMode, _append(), _atomic_text(), Path, Visible local chat. Only text entered in its reply box is transmitted., # IMPORTANT: send/store logical Unicode, never visual/reversed text., SecurityChatManager (+22 more)

### Community 5 - "CameraMonitor"
Cohesion: 0.09
Nodes (19): CameraMonitor, CameraDevice, _decode_c_string(), discover_cameras(), _linux_capability(), open_camera(), probe_camera(), Path (+11 more)

### Community 6 - "HttpBotProvider"
Cohesion: 0.12
Nodes (10): ABC, BotProvider, ProviderError, Any, Path, RuntimeError, HttpBotProvider, Any (+2 more)

### Community 7 - "BaleApi"
Cohesion: 0.14
Nodes (12): _apply_legacy_env(), _apply_section(), _coerce_like(), ensure_dirs(), _migrate(), Any, Persist non-secret configuration to config.toml.      Bot/API secrets deliberate, One-way compatibility for users launching with exported old variables.      The (+4 more)

### Community 8 - "StopPinStore"
Cohesion: 0.10
Nodes (24): _failed_login_monitor_ok(), main(), _persian_tts_ok(), _psutil_ok(), run_doctor(), _tk_ok(), _video_player_ok(), _warning_video_ok() (+16 more)

### Community 9 - "Full system audit"
Cohesion: 0.13
Nodes (14): Authorization and bot handling, Communications and media, Evidence boundary, Executive assessment, Findings and priorities, Full system audit, Local API and app control, Monitoring and intrusion flow (+6 more)

### Community 10 - "EventStore"
Cohesion: 0.13
Nodes (10): EventLog, Path, EventStore, OutboxItem, Path, test_event_log_roundtrip(), test_guard_events_are_visible_in_shared_sqlite_store(), Path (+2 more)

### Community 11 - "AudioConfig"
Cohesion: 0.07
Nodes (22): AudioRecorder, Path, Local TTS for short owner messages. No cloud service is used., Record a short clip synchronously for the localhost control API., RemoteAudioPlayer, TextToSpeechPlayer, AudioConfig, pcm_rms() (+14 more)

### Community 12 - "RuntimeStateStore"
Cohesion: 0.17
Nodes (9): GuardRuntimeState, Live facade over the shared persisted runtime state.      Assignments are immedi, Path, RuntimeState, RuntimeStateStore, test_guard_state_observes_external_cli_changes(), test_guard_state_persists_assignments(), Path (+1 more)

### Community 13 - "config.py"
Cohesion: 0.24
Nodes (17): BaseException, import_legacy_env_secrets(), Import an already-exported legacy bot token into secrets.json once., _ask_valid_token(), _auth_error(), ensure_runtime_configuration(), _interactive(), _pair_owner_chat() (+9 more)

### Community 14 - "AppConfig"
Cohesion: 0.07
Nodes (30): ApiConfig, AppConfig, AppsConfig, BotConfig, ChatConfig, CommunicationConfig, MonitorConfig, ScreenConfig (+22 more)

### Community 15 - "RuntimeApi"
Cohesion: 0.08
Nodes (16): BaleApi, BaleApiError, Any, Path, RuntimeError, Small dependency-light client for Bale's Telegram-style Bot API., build_runtime_api(), LocalRuntimeApi (+8 more)

### Community 16 - "ScreenCaptureManager"
Cohesion: 0.17
Nodes (7): Path, Backward-compatible facade for older diagnostics/tests., ScreenCapture, ScreenCaptureManager, test_screen_manager_reports_backend_string(), test_parse_gnome_dbus_failure_is_empty(), test_parse_gnome_dbus_path()

### Community 17 - "test_v33_features.py"
Cohesion: 0.08
Nodes (13): SecurityConfig, CameraPrivacyLight, LightStatus, Path, Best-effort control for a *separate* camera indicator exposed via sysfs.      Ma, Safe indicator policy: never force the indicator dark while capturing., Path, Launch and control the visible intrusion countdown surface.      The child proce (+5 more)

### Community 18 - "HealthMonitor"
Cohesion: 0.24
Nodes (6): collect_health(), HealthMonitor, HealthSnapshot, _temperature(), HealthConfig, test_health_snapshot_is_non_throwing()

### Community 19 - "runtime_config.py"
Cohesion: 0.33
Nodes (12): default_api_base(), get_api_token(), get_bot_token(), _read_secrets(), set_api_token(), set_bot_token(), build_provider(), _choose_camera() (+4 more)

### Community 20 - "models.py"
Cohesion: 0.05
Nodes (38): 1. Clone, 2. Install, 3. Configure, 4. Validate, 5. Run, AI-assisted development, AngysGuard, Available today (+30 more)

### Community 21 - "README.md"
Cohesion: 0.17
Nodes (12): Automated suite, CI failure triage, Documentation and AI-navigation regression checks, Environment-specific validation, Graphify-guided test selection, Progressive verification, Regression-test rule for bug fixes, Repository-presentation regression checks (+4 more)

### Community 22 - "Security and privacy"
Cohesion: 0.33
Nodes (6): Capture and privacy, Protected termination, Remote controls, Residual risks, Security and privacy, Trust model

### Community 23 - "AppManager"
Cohesion: 0.32
Nodes (4): AppManager, DesktopApp, Conservative GUI application manager.      It uses .desktop entries rather than, test_app_manager_respects_allowlist()

### Community 24 - "launch_warning"
Cohesion: 0.17
Nodes (5): InputMonitor, Detects input *activity*, never stores typed keys or button values.      auto mo, test_first_pynput_mouse_movement_triggers_immediately(), test_single_nonzero_evdev_relative_event_triggers(), test_input_monitor_has_backend_and_no_key_buffer()

### Community 25 - "LocalControlAPI"
Cohesion: 0.28
Nodes (4): LocalControlAPI, Path, Small authenticated local API.      Default bind is 127.0.0.1. It intentionally, test_local_api_constructs_without_shell_surface()

### Community 26 - "setup_wizard.py"
Cohesion: 0.08
Nodes (25): 1. Owner-controlled by default, 2. No generic remote shell, 3. OS passwords remain local, 4. Self-hosted remains a first-class mode, 5. Managed mode is optional, 6. Platform differences are explicit, 7. Users can influence platform targets, A. Linux today (+17 more)

### Community 28 - "show_fullscreen"
Cohesion: 0.48
Nodes (6): _load_background(), main(), _notify(), Return a PhotoImage-like object fitted to the current screen.      Pillow is opt, show_fullscreen(), Tk

### Community 29 - "test_persian_tts.py"
Cohesion: 0.08
Nodes (24): 10. Platform requests, 11. Backlog, 1. Now, 2. Current product roadmap, 3. AngysGuard product future, 4. Platform expansion, 5. Managed service, 6. Self-hosted bot & providers (+16 more)

### Community 30 - "Release and migration history"
Cohesion: 0.18
Nodes (10): 11, 11.1, 3.2–3.3, 4, 5, 6, 7, 8 (+2 more)

### Community 39 - "Configuration"
Cohesion: 0.40
Nodes (5): Configuration, Configuration sections, Initial setup, Maintenance, Storage

### Community 40 - "Extending Laptop Guard"
Cohesion: 0.25
Nodes (7): Changing or removing a feature, Command feature template, Configuration and diagnostics, Extending Laptop Guard, Host capabilities, Test checklist, Transport and state

### Community 41 - "File reference"
Cohesion: 0.14
Nodes (13): Camera, input, screen, audio, and UI, Codex / AI workspace, Documentation, Entrypoint, configuration, and state, File reference, Generated architecture/navigation data, GitHub repository automation and presentation, Main runtime and feature system (+5 more)

### Community 42 - "Laptop Guard 11.1"
Cohesion: 0.09
Nodes (23): Application layer, Architectural goal, Architecture, Architecture review checklist, Compatibility layers, Composition root, Concurrency model, Current runtime (+15 more)

### Community 43 - "Laptop Guard agent guide"
Cohesion: 0.22
Nodes (3): FakeResponse, FakeSession, test_send_message_serializes_inline_keyboard()

### Community 44 - "test_config_robustness.py"
Cohesion: 0.10
Nodes (21): 10. AI-agent workflows for finding and fixing bugs, 11. Verification after the fix, 12. Bug-fix completion checklist, 1. Start with evidence, not code changes, 2. Map the symptom with Graphify before broad searching, 3. Classify the failure, 4. Reproduce the smallest failing case, 5. Use canonical docs only after navigation is narrowed (+13 more)

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

### Community 74 - "ROADMAP.md"
Cohesion: 0.09
Nodes (22): AngysGuard / Laptop Guard roadmap, AngysGuard self-hosted UX, Architecture evolution track, Cross-platform, Current baseline, Definition of done for every issue, Exit criteria, Hard security exit criteria (+14 more)

### Community 75 - "Architecture boundaries and dependency rules"
Cohesion: 0.13
Nodes (14): Architecture boundaries and dependency rules, Architecture exceptions, Boundary table, Capture boundary, Current architectural seams to preserve, Current exceptions / migration areas, Dependency direction, Feature boundary rules (+6 more)

### Community 76 - "Unreleased"
Cohesion: 0.14
Nodes (13): 11.1.0 — 2026-09-12, AI-assisted engineering, AngysGuard brand system, AngysGuard product/platform planning, Architecture baseline, Audio security and communication, Changelog, Developer and AI navigation (+5 more)

### Community 78 - "Prompt index"
Cohesion: 0.14
Nodes (13): Bugs and incidents, Documentation, brand, presentation and delivery, Feature lifecycle, General-purpose router, How to use, Maintenance rule, Navigate, understand and plan, Product/platform planning (+5 more)

### Community 79 - "ADR 0007: Passwordless remote device pairing and local privilege separation"
Cohesion: 0.15
Nodes (12): Add a generic remote shell and let the user run privilege commands, ADR 0007: Passwordless remote device pairing and local privilege separation, Consequences, Context, Cost, Decision, Positive, Rejected alternatives (+4 more)

### Community 80 - "ADR 0008: Cross-platform capability adapters before OS expansion"
Cohesion: 0.15
Nodes (12): ADR 0008: Cross-platform capability adapters before OS expansion, Capability-first behavior, Claim identical features on every OS, Consequences, Context, Cost, Decision, One runtime full of platform conditionals (+4 more)

### Community 81 - "Architecture evolution plan"
Cohesion: 0.15
Nodes (12): Architecture evolution plan, Ground rules, Phase 0 — Architecture contract (documentation), Phase 1 — Reduce `LaptopGuard` orchestration load, Phase 2 — Consolidate communication/provider adapters, Phase 3 — Consolidate system/warning/media facades, Phase 4 — Reliable delivery and storage lifecycle, Phase 5 — Refine feature/application boundaries (+4 more)

### Community 82 - "AngysGuard platform support and targets"
Cohesion: 0.15
Nodes (13): Android companion app — issue #35, Android protected-device mode — issue #36, AngysGuard platform support and targets, Cross-platform architecture rule, Current Linux requirements, Current operating-system support, Future desktop/mobile targets, Linux desktop app — issue #32 (+5 more)

### Community 83 - "AngysGuard / Laptop Guard AI / Codex instructions"
Cohesion: 0.17
Nodes (12): AngysGuard / Laptop Guard AI / Codex instructions, Available project agents, Available project skills, Command-output hygiene, Completion standard, Graphify-first navigation — mandatory default, Mission, Read only what the task needs (+4 more)

### Community 84 - "Graphify-first repository navigation"
Cohesion: 0.11
Nodes (15): AI agent compatibility note, Laptop Guard agent instructions, 1. Check graph availability and freshness, 2. Query before reading files, 3. Confirm with authoritative files, AI workflow, Graphify-first repository navigation, Human workflow (+7 more)

### Community 85 - "AngysGuard / Laptop Guard documentation"
Cohesion: 0.18
Nodes (11): AngysGuard / Laptop Guard documentation, Architecture decisions relevant to future platforms, Control-mode summary, Current product, Current vs future, Future product, Graphify-first repository discovery, Platform summary (+3 more)

### Community 87 - "Runtime and security flows"
Cohesion: 0.20
Nodes (9): Configuration change while running, Event and owner delivery, Evidence lifecycle, Failure ordering principles, Incoming owner command, Intrusion/input alert, Protected stop, Runtime and security flows (+1 more)

### Community 88 - "pull_request_template.md"
Cohesion: 0.20
Nodes (9): Discovery / scope, Manual checks, Platform / control-mode impact, Related work, Repository presentation, Risk / rollback, Summary, Type of change (+1 more)

### Community 90 - "AngysGuard brand assets"
Cohesion: 0.22
Nodes (8): AngysGuard brand assets, Canonical sources, Handoff, Logo rule, Palette, Product/category rule, Review checklist, Workflow

### Community 91 - "Codex project workspace"
Cohesion: 0.22
Nodes (8): Agent roles, Codex project workspace, Hooks, Layout, Navigation rule, Primary instructions, Product/platform workflow, Trust

### Community 92 - "Future mode B — AngysGuard managed bot/service"
Cohesion: 0.22
Nodes (9): Computer/OS password rule — hard boundary, Future mode B — AngysGuard managed bot/service, Managed service security requirements, Multi-device future, Provider capability parity, Related roadmap, Self-hosted vs managed comparison, Target managed onboarding (+1 more)

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

### Community 100 - "Current owner interfaces"
Cohesion: 0.17
Nodes (11): 1. Local CLI and guided setup — available now, 2. Bale bot — current bot-style owner UI, 3. Telegram-style provider — current provider architecture, release validation required, 4. Local desktop/chat surfaces — available in current runtime where applicable, AngysGuard control modes: local, self-hosted bot, and managed service, Current owner interfaces, Current safety model for bot control, Future mode A — self-hosted Bale/Telegram bot (+3 more)

### Community 101 - "AngysGuard repository rename and GitHub Projects runbook"
Cohesion: 0.29
Nodes (6): AngysGuard repository rename and GitHub Projects runbook, Canonical repository name, GitHub Project v2, Project bootstrap, Rename action, Security

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
Nodes (5): _graph_status(), main(), Path, _run(), CompletedProcess

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
Cohesion: 0.47
Nodes (3): ensure_single_select_field(), set_field(), bootstrap_github_project.sh script

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

### Community 125 - "Test instructions"
Cohesion: 0.50
Nodes (3): Find tests with Graphify first, Test instructions, Test rules

## Knowledge Gaps
- **544 isolated node(s):** `doctor.sh script`, `install.sh script`, `BotConfig`, `CommunicationConfig`, `ScreenConfig` (+539 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LaptopGuard` connect `LaptopGuard` to `cli.py`, `guard.py`, `SecurityChatManager`, `StopPinStore`, `EventStore`, `AudioConfig`, `RuntimeStateStore`, `config.py`, `AppConfig`, `RuntimeApi`, `ScreenCaptureManager`, `launch_warning`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `AppConfig` connect `AppConfig` to `cli.py`, `guard.py`, `BaleApi`, `config.py`, `RuntimeApi`, `test_v33_features.py`, `runtime_config.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `build_provider()` connect `runtime_config.py` to `cli.py`, `config.py`, `HttpBotProvider`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `LaptopGuard` (e.g. with `AudioIntercom` and `BaleApiError`) actually correct?**
  _`LaptopGuard` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `AppConfig` (e.g. with `LocalRuntimeApi` and `RuntimeApi`) actually correct?**
  _`AppConfig` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `FeatureManager` (e.g. with `Feature` and `FeatureHost`) actually correct?**
  _`FeatureManager` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `SoundDetectionMonitor` (e.g. with `LaptopGuard` and `AudioRecorder`) actually correct?**
  _`SoundDetectionMonitor` has 3 INFERRED edges - model-reasoned connections that need verification._