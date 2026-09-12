# Graph Report - laptop_guard_v3  (2026-09-12)

## Corpus Check
- 102 files · ~34,629 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 900 nodes · 1843 edges · 67 communities (37 shown, 30 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 80 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `11f38aa7`
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

## God Nodes (most connected - your core abstractions)
1. `LaptopGuard` - 86 edges
2. `AppConfig` - 52 edges
3. `FeatureManager` - 31 edges
4. `load_config()` - 27 edges
5. `BaleApi` - 25 edges
6. `EventStore` - 24 edges
7. `InputMonitor` - 22 edges
8. `HttpBotProvider` - 21 edges
9. `RuntimeApi` - 21 edges
10. `run_setup()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `test_invalid_voice_falls_back()` --calls--> `AppConfig`  [INFERRED]
  tests/test_persian_tts.py → laptop_guard/models.py
- `test_tts_defaults()` --calls--> `AppConfig`  [INFERRED]
  tests/test_persian_tts.py → laptop_guard/models.py
- `test_default_warning_sequence_is_five_seconds()` --calls--> `AppConfig`  [INFERRED]
  tests/test_config.py → laptop_guard/models.py
- `test_protected_stop_defaults()` --calls--> `AppConfig`  [INFERRED]
  tests/test_config.py → laptop_guard/models.py
- `test_v33_safe_defaults()` --calls--> `AppConfig`  [EXTRACTED]
  tests/test_v33_features.py → laptop_guard/models.py

## Import Cycles
- None detected.

## Communities (67 total, 30 thin omitted)

### Community 0 - "cli.py"
Cohesion: 0.09
Nodes (43): build_parser(), cmd_arm(), cmd_autostart(), cmd_config(), cmd_disarm(), cmd_doctor(), cmd_events(), cmd_health() (+35 more)

### Community 1 - "LaptopGuard"
Cohesion: 0.07
Nodes (6): notify(), inline_keyboard(), LaptopGuard, main(), Any, Path

### Community 2 - "FeatureManager"
Cohesion: 0.05
Nodes (28): CallbackHandler, CommandHandler, Feature, FeatureHost, Protocol, Narrow host surface available to features., Explicit extension point; features are registered, never auto-imported., FailedLoginEvent (+20 more)

### Community 3 - "guard.py"
Cohesion: 0.09
Nodes (13): Indicator, main(), AudioIntercom, play_audio(), Path, Visible near-live voice intercom.      Bale Bot API transports voice/audio messa, record_audio(), normalize_voice() (+5 more)

### Community 4 - "SecurityChatManager"
Cohesion: 0.07
Nodes (27): Direction, DirectionMode, _append(), _atomic_text(), Path, Visible local chat. Only text entered in its reply box is transmitted., # IMPORTANT: send/store logical Unicode, never visual/reversed text., SecurityChatManager (+19 more)

### Community 5 - "CameraMonitor"
Cohesion: 0.09
Nodes (20): CameraMonitor, camera_label(), CameraDevice, _decode_c_string(), discover_cameras(), _linux_capability(), open_camera(), probe_camera() (+12 more)

### Community 6 - "HttpBotProvider"
Cohesion: 0.12
Nodes (10): ABC, BotProvider, ProviderError, Any, Path, RuntimeError, HttpBotProvider, Any (+2 more)

### Community 7 - "BaleApi"
Cohesion: 0.13
Nodes (9): BaleApi, BaleApiError, Any, Path, RuntimeError, Small dependency-light client for Bale's Telegram-style Bot API., FakeResponse, FakeSession (+1 more)

### Community 8 - "StopPinStore"
Cohesion: 0.07
Nodes (41): _authorized_safe_exit(), main(), _pid_alive(), Lock when the guard disappears unless it completed owner-authorized exit.      T, watch(), bounded_callback_int(), Parse an integer callback suffix without letting malformed input crash polling., PinCheck (+33 more)

### Community 9 - "Full system audit"
Cohesion: 0.14
Nodes (14): Authorization and bot handling, Communications and media, Evidence boundary, Executive assessment, Findings and priorities, Full system audit, Local API and app control, Monitoring and intrusion flow (+6 more)

### Community 10 - "EventStore"
Cohesion: 0.13
Nodes (10): EventLog, Path, EventStore, OutboxItem, Path, test_event_log_roundtrip(), test_guard_events_are_visible_in_shared_sqlite_store(), Path (+2 more)

### Community 11 - "AudioConfig"
Cohesion: 0.12
Nodes (8): AudioRecorder, Path, Local TTS for short owner messages. No cloud service is used., Record a short clip synchronously for the localhost control API., RemoteAudioPlayer, TextToSpeechPlayer, AudioConfig, desktop_notify()

### Community 12 - "RuntimeStateStore"
Cohesion: 0.17
Nodes (9): GuardRuntimeState, Live facade over the shared persisted runtime state.      Assignments are immedi, Path, RuntimeState, RuntimeStateStore, test_guard_state_observes_external_cli_changes(), test_guard_state_persists_assignments(), Path (+1 more)

### Community 13 - "config.py"
Cohesion: 0.14
Nodes (12): _apply_legacy_env(), _apply_section(), _coerce_like(), ensure_dirs(), _migrate(), Any, Persist non-secret configuration to config.toml.      Bot/API secrets deliberate, One-way compatibility for users launching with exported old variables.      The (+4 more)

### Community 14 - "AppConfig"
Cohesion: 0.15
Nodes (14): AppConfig, test_enabling_for_next_login_does_not_start_immediately(), test_startup_and_arming_are_separate_defaults(), test_chat_defaults_to_two_minutes_and_allows_visitor_reply(), test_default_warning_sequence_is_five_seconds(), test_protected_stop_defaults(), Path, test_v4_config_sections_roundtrip() (+6 more)

### Community 15 - "RuntimeApi"
Cohesion: 0.13
Nodes (10): build_runtime_api(), LocalRuntimeApi, Any, Path, Protocol, Transport contract consumed by the guard runtime.      Feature code depends on t, No-network runtime adapter for local-only installations., RuntimeApi (+2 more)

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
Cohesion: 0.24
Nodes (17): BaseException, import_legacy_env_secrets(), Import an already-exported legacy bot token into secrets.json once., _ask_valid_token(), _auth_error(), ensure_runtime_configuration(), _interactive(), _pair_owner_chat() (+9 more)

### Community 20 - "models.py"
Cohesion: 0.13
Nodes (11): ApiConfig, AppsConfig, BotConfig, ChatConfig, CommunicationConfig, MonitorConfig, ScreenConfig, StartupConfig (+3 more)

### Community 21 - "README.md"
Cohesion: 0.29
Nodes (3): Automated suite, Target-device checks, Testing and validation

### Community 22 - "Security and privacy"
Cohesion: 0.29
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
Cohesion: 0.35
Nodes (11): default_api_base(), get_api_token(), _read_secrets(), set_api_token(), set_bot_token(), build_provider(), _choose_camera(), detect_audio_sources() (+3 more)

### Community 28 - "show_fullscreen"
Cohesion: 0.48
Nodes (6): _load_background(), main(), _notify(), Return a PhotoImage-like object fitted to the current screen.      Pillow is opt, show_fullscreen(), Tk

### Community 30 - "Release and migration history"
Cohesion: 0.20
Nodes (10): 11, 11.1, 3.2–3.3, 4, 5, 6, 7, 8 (+2 more)

### Community 39 - "Configuration"
Cohesion: 0.33
Nodes (5): Configuration, Configuration sections, Initial setup, Maintenance, Storage

### Community 40 - "Extending Laptop Guard"
Cohesion: 0.33
Nodes (5): Command feature template, Extending Laptop Guard, Host capabilities, Test checklist, Transport and state

### Community 41 - "File reference"
Cohesion: 0.33
Nodes (5): Current automated tests, Documentation, File reference, Root and operations, Runtime package

### Community 42 - "Laptop Guard 11.1"
Cohesion: 0.40
Nodes (5): Common commands, Documentation, Install and run, Laptop Guard 11.1, Main behavior

### Community 43 - "Laptop Guard agent guide"
Cohesion: 0.50
Nodes (3): Laptop Guard agent guide, Rules, Runtime path

### Community 44 - "test_config_robustness.py"
Cohesion: 0.43
Nodes (5): apply_profile(), Apply safe, reversible-ish defaults for a named operating profile.      Profiles, ProfileName, test_away_profile_uses_visible_countdown_lock(), test_testing_profile_reduces_noise()

## Knowledge Gaps
- **78 isolated node(s):** `doctor.sh script`, `install.sh script`, `BotConfig`, `CommunicationConfig`, `ScreenConfig` (+73 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LaptopGuard` connect `LaptopGuard` to `cli.py`, `guard.py`, `SecurityChatManager`, `BaleApi`, `StopPinStore`, `EventStore`, `RuntimeStateStore`, `RuntimeApi`, `ScreenCaptureManager`, `runtime_config.py`, `launch_warning`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Why does `AppConfig` connect `AppConfig` to `cli.py`, `guard.py`, `test_config_robustness.py`, `config.py`, `RuntimeApi`, `test_v33_features.py`, `runtime_config.py`, `models.py`, `setup_wizard.py`, `test_persian_tts.py`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `FeatureManager` connect `FeatureManager` to `StopPinStore`, `guard.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `LaptopGuard` (e.g. with `AudioIntercom` and `BaleApiError`) actually correct?**
  _`LaptopGuard` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `AppConfig` (e.g. with `LocalRuntimeApi` and `RuntimeApi`) actually correct?**
  _`AppConfig` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `FeatureManager` (e.g. with `Feature` and `FeatureHost`) actually correct?**
  _`FeatureManager` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `BaleApi` (e.g. with `LocalRuntimeApi` and `RuntimeApi`) actually correct?**
  _`BaleApi` has 2 INFERRED edges - model-reasoned connections that need verification._