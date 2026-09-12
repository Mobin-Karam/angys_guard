# File reference

This catalog describes every retained project file after documentation
consolidation. Generated caches, `.git`, `.venv`, and local `graphify-out`
artifacts are not product source.

## Root and operations

| File | Responsibility |
|---|---|
| `.env`, `.env.example` | Legacy environment compatibility/example; current setup does not require them and secrets must not be committed. |
| `.gitignore` | Excludes local environments, caches, secrets, media, and runtime data from version control. |
| `LICENSE` | Project licensing terms. |
| `pyproject.toml` | Package metadata, runtime/test dependencies, console entry point, discovery, and media package data. |
| `AGENTS.md` | Compact project map, security constraints, and validation rules for AI coding agents. |
| `requirements.txt` | Installer-compatible pinned/ranged runtime dependency list. |
| `install.sh` | Creates `.venv`, upgrades pip, and installs runtime requirements. |
| `run.sh` | Secure launcher with `umask 077`; selects virtual-environment Python. |
| `doctor.sh` | Convenience launcher for dependency/configuration diagnostics. |
| `repair-opencv.sh` | Repairs conflicting OpenCV variants for HOG compatibility. |
| `V11_CHANGED_FILES.txt` | Historical handoff inventory; redundant with version control and a candidate for removal. |
| `new.zip` | Untracked delivery/archive artifact; not used by the runtime and should be removed only after confirming it is not the user's backup. |

## Documentation

| File | Responsibility |
|---|---|
| `docs/README.md` | Current product entry point and documentation index. |
| `docs/CONFIGURATION.md` | Setup, persisted paths, defaults, migration, and service preparation. |
| `docs/SECURITY.md` | Trust model, authorization, protected exit, privacy, and residual risks. |
| `docs/TESTING.md` | Automated and target-device validation instructions/evidence. |
| `docs/HISTORY.md` | Consolidated v3–v11.1 release and migration history. |
| `docs/SYSTEM_AUDIT.md` | Full architecture, current behavior, findings, priorities, and evidence boundary. |
| `docs/FILE_REFERENCE.md` | This complete retained-file catalog. |
| `docs/EXTENDING.md` | Feature registry template, contracts, and focused validation workflow. |

## Runtime package

| File | Responsibility and current status |
|---|---|
| `laptop_guard/__init__.py` | Package version/public package marker. |
| `laptop_guard/__main__.py` | Enables `python -m laptop_guard`; delegates to CLI. |
| `laptop_guard/cli.py` | Parses setup/run/status/profile/events/health/test/service commands. Active. |
| `laptop_guard/models.py` | Dataclass configuration schema and compatibility properties. Active. |
| `laptop_guard/config.py` | User paths, TOML/secrets persistence, legacy env import, and migrations. Active. |
| `laptop_guard/runtime_config.py` | Interactive token validation/repair and owner pairing before startup. Active. |
| `laptop_guard/runtime_api.py` | Main-runtime transport protocol/factory plus token-free local adapter. Active boundary. |
| `laptop_guard/runtime_state.py` | Live facade over shared persisted CLI/guard state. Active boundary. |
| `laptop_guard/features/base.py` | Narrow feature and host protocols. Active extension contract. |
| `laptop_guard/features/manager.py` | Conflict-safe command/callback registry and feature lifecycle. Active extension core. |
| `laptop_guard/features/system_info.py` | First extracted feature for status/system/help commands. Active. |
| `laptop_guard/features/failed_login.py` | Parses and monitors journal authentication failures, deduplicates bursts, and alerts the owner. |
| `laptop_guard/features/__init__.py` | Public feature-system exports. |
| `laptop_guard/setup_wizard.py` | Resumable guided setup, camera/audio discovery, and owner pairing. Active. |
| `laptop_guard/doctor.py` | Reports required and optional runtime/backend readiness. Active. |
| `laptop_guard/guard.py` | Main v11 orchestration: polling, authorization, menus, monitors, evidence, warning/lock, media, chat, TTS, and lifecycle. Active core. |
| `laptop_guard/bale_api.py` | Direct Requests-based Bale Bot API client used by `LaptopGuard`. Active. |
| `laptop_guard/providers/base.py` | Abstract generic bot provider contract. Used by setup/modular path, not main guard transport. |
| `laptop_guard/providers/http_bot.py` | Httpx Telegram-style provider with explicit proxy policy. Secondary/compatibility path. |
| `laptop_guard/providers/__init__.py` | Provider factory for Bale/Telegram-style HTTP providers. Secondary path. |
| `laptop_guard/camera.py` | Threaded motion/person/tamper camera monitor and HOG fallback. Modular component/tests. |
| `laptop_guard/camera_devices.py` | Quiet camera discovery, Linux device metadata, probing, and labels. Active setup/support. |
| `laptop_guard/input_monitor.py` | Evdev activity classification with pynput fallback; discards key identity. Modular component. |
| `laptop_guard/screen_capture.py` | Screenshot and bounded video backends for GNOME, Wayland, and X11. Active. |
| `laptop_guard/audio.py` | General recorder, remote playback, and command-backed TTS playback classes. Compatibility/modular layer. |
| `laptop_guard/audio_intercom.py` | Current fixed-command recording/playback and near-live intercom manager. Active. |
| `laptop_guard/audio_indicator.py` | Local subprocess indicator for visible microphone activity. Support process. |
| `laptop_guard/persian_speech.py` | Lazy async PersianTTS integration, voice normalization, bounded serialized queue, and playback. Active. |
| `laptop_guard/chat_surface.py` | Chat event/transcript persistence and child-window management. Active. |
| `laptop_guard/chat_window.py` | Tk fullscreen bilingual chat/notepad UI and visitor replies. Active child process. |
| `laptop_guard/text_direction.py` | RTL/LTR detection, shaping, bidi rendering, and direction marks. Active. |
| `laptop_guard/warning_sequence.py` | Current MP4 player selection, fullscreen launch, notification fallback, and process-group cleanup. Active. |
| `laptop_guard/warning.py` | Older image/staged warning process manager. Compatibility/tests; not the main v11 warning path. |
| `laptop_guard/warning_screen.py` | Tk image/text warning child UI used by the older warning manager. Compatibility child process. |
| `laptop_guard/assets/warnings/countdown.mp4` | Bundled five-second 1920×1080 intrusion warning. Active packaged asset. |
| `laptop_guard/system_actions.py` | Current lock/unlock/suspend/reboot/shutdown and system snapshot helpers. Active. |
| `laptop_guard/system.py` | Older compact lock/unlock/notification/session helpers used by CLI/modular code. Compatibility layer. |
| `laptop_guard/exit_watchdog.py` | Detached parent-death monitor and one-time safe-exit token consumer. Active security component. |
| `laptop_guard/stop_auth.py` | Scrypt PIN store and bounded hidden terminal input. Active security component. |
| `laptop_guard/events.py` | Fail-safe JSONL log with mirrored writes to the shared SQLite event store. Active. |
| `laptop_guard/storage.py` | Shared SQLite events and durable outbound queue. Event writes are integrated; failed v11 sends do not all use the outbox yet. |
| `laptop_guard/state.py` | Atomic shared JSON runtime-state persistence used by CLI and live guard. Active. |
| `laptop_guard/profiles.py` | Applies Away/Home/Night/Testing configuration presets. Active CLI/setup support. |
| `laptop_guard/health.py` | Psutil health snapshot and change-monitor thread. Modular/CLI support. |
| `laptop_guard/usb_monitor.py` | Pyudev-based USB event watcher. Modular component; not started by current `LaptopGuard`. |
| `laptop_guard/privacy_light.py` | Best-effort camera indicator discovery/follow mode; never suppresses active capture indication. Support component. |
| `laptop_guard/app_manager.py` | Discovers, launches, and normally terminates allowlisted desktop apps. Optional modular component. |
| `laptop_guard/control_api.py` | Optional loopback bearer-authenticated fixed-action HTTP API. Optional modular component. |
| `laptop_guard/service.py` | Installs/removes/inspects the systemd user unit. Active CLI support. |
| `laptop_guard/tests_manual.py` | Hardware/integration checks invoked by `./run.sh test`. Active diagnostic support. |

## Current automated tests

| File | Coverage |
|---|---|
| `tests/test_bale_api.py` | Bale keyboard serialization and download URL. |
| `tests/test_camera_capability.py` | Person detector capability and safe HOG fallback. |
| `tests/test_cli.py` | Correct success/failure exit codes for CLI desktop locking. |
| `tests/test_config.py` | Five-second warning and protected-stop defaults. |
| `tests/test_config_checkpoint.py` | Setup completion persistence. |
| `tests/test_config_v33_migration.py` | Old immediate-lock migration. |
| `tests/test_events.py` | JSONL event log round trip. |
| `tests/test_exit_watchdog.py` | PID liveness helpers. |
| `tests/test_persian_tts.py` | Defaults, voices, async API contract, playback, and persistence. |
| `tests/test_provider_keyboard.py` | Generic provider inline keyboard encoding. |
| `tests/test_state.py` | Runtime state atomic round trip. |
| `tests/test_stop_auth.py` | PIN hashing/verification and one-time safe exit. |
| `tests/test_text_direction.py` | Persian/English/mixed/neutral direction behavior. |
| `tests/test_v33_features.py` | Safe defaults, light status, and warning initial state. |
| `tests/test_v4_config_roundtrip.py` | Configuration section round trip. |
| `tests/test_v4_health.py` | Non-throwing health snapshot. |
| `tests/test_v4_outbox.py` | SQLite events and offline queue. |
| `tests/test_v4_profiles.py` | Away and Testing profile behavior. |
| `tests/test_v5_api.py` | Local API construction and absence of shell surface. |
| `tests/test_v5_apps.py` | Desktop app allowlist. |
| `tests/test_v5_chat.py` | Owner/visitor chat persistence. |
| `tests/test_v5_config.py` | Newer config sections/lists round trip. |
| `tests/test_v5_input_privacy.py` | Input backend and no key buffer. |
| `tests/test_v5_screen.py` | Screen backend reporting. |
| `tests/test_v6_config_migration.py` | Text-editor migration and input evidence defaults. |
| `tests/test_v6_screen_native.py` | GNOME D-Bus screen path parsing. |
| `tests/test_v6_warning.py` | Legacy warning manager stages/notification arguments. |
| `tests/test_v8_security_config.py` | Exit lock, unlock/power opt-in, direction, stop defaults. |
| `tests/test_warning_assets.py` | MP4 existence, dimensions, frame rate, and duration. |
| `tests/test_feature_manager.py` | Feature registration, routing, lifecycle, and conflict rejection. |
| `tests/test_guard_helpers.py` | Safe bounds/defaults for untrusted callback integer payloads. |
| `tests/test_runtime_api.py` | Local no-token runtime and configured proxy propagation. |
| `tests/test_runtime_state.py` | Live state persistence and observation of external CLI changes. |
| `tests/test_service.py` | Service and CLI failure exit-code propagation. |
| `tests/test_autostart.py` | Separate startup/arming defaults and systemd enable command. |
| `tests/test_failed_login.py` | GDM/SSH parsing, filtering, owner alerts, and deduplication. |

Historical uncollected `.legacy.py` copies were removed because the current test
files already cover their configuration migration, setup checkpoint, and chat
round-trip cases.
