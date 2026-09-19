from __future__ import annotations

import importlib.util
import os
import platform
import shutil
import stat
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from . import config as config_module
from .models import AppConfig
from .stop_auth import StopPinStore

Category = Literal["required", "recommended", "optional"]


@dataclass(frozen=True, slots=True)
class DoctorCheck:
    name: str
    category: Category
    ok: bool
    detail: str
    action: str = ""


def _check(
    name: str,
    category: Category,
    ok: bool,
    detail: str,
    action: str = "",
) -> DoctorCheck:
    return DoctorCheck(name, category, bool(ok), detail, action if not ok else "")


def _python_version_ok() -> tuple[bool, str]:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return sys.version_info >= (3, 11), f"Python {version}"


def _venv_health_ok() -> tuple[bool, str]:
    active = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    module_available = importlib.util.find_spec("venv") is not None
    if active and module_available:
        return True, "Virtual environment is active and Python venv support is available."
    if not module_available:
        return False, "Python venv support is missing."
    return False, "Laptop Guard is not running from its virtual environment."


def _python_dependencies_ok() -> tuple[bool, str]:
    modules = {
        "requests": "requests",
        "httpx": "httpx",
        "cv2": "opencv-python",
        "pynput": "pynput",
        "rich": "rich",
        "psutil": "psutil",
        "pyudev": "pyudev",
        "evdev": "evdev",
        "PIL": "Pillow",
    }
    missing = [package for module, package in modules.items() if importlib.util.find_spec(module) is None]
    if missing:
        return False, "Missing Python packages: " + ", ".join(sorted(missing))
    return True, "Core Python packages are installed."


def _config_integrity() -> tuple[bool, str]:
    path = config_module.CONFIG_PATH
    if not path.exists():
        return False, "Configuration has not been created yet."
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return False, "Configuration file cannot be read safely."
    if not isinstance(raw, dict):
        return False, "Configuration file is not valid."
    return True, "Configuration file is readable and valid."


def _secret_permissions_ok() -> tuple[bool, str]:
    path = config_module.SECRETS_PATH
    if not path.exists():
        return True, "No secrets file exists yet."
    try:
        mode = stat.S_IMODE(path.stat().st_mode)
    except OSError:
        return False, "Secrets file permissions could not be inspected."
    if mode != 0o600:
        return False, f"Secrets file permissions are {mode:04o}; expected 0600."
    return True, "Secrets file is private to the current user (0600)."


def check_bot_connectivity_detailed(
    cfg: AppConfig,
    token: str,
) -> tuple[bool, str, str]:
    """Return token-safe connectivity status plus a stable failure category."""
    if cfg.bot.provider == "local":
        return True, "Local mode does not require a bot connection.", "ok"
    if not token:
        return False, "No bot token is stored.", "missing"

    bot = None
    provider_label = cfg.bot.provider.title()
    try:
        from . import providers
        from .providers.base import (
            ProviderAuthError,
            ProviderConnectionError,
            ProviderError,
            ProviderResponseError,
        )

        bot = providers.build_provider(
            cfg.bot.provider,
            token,
            cfg.bot.api_base,
            cfg.bot.proxy,
        )
        if bot is None:
            return False, "Configured bot provider is not supported.", "unsupported"
        bot.get_me()
        return True, f"{provider_label} bot connection is working.", "ok"
    except ProviderAuthError:
        return False, f"{provider_label} rejected the bot credential.", "auth"
    except ProviderConnectionError:
        return (
            False,
            f"Could not reach the {provider_label} bot service. "
            "The credential was not proven invalid. Check internet/proxy settings and the API base.",
            "network",
        )
    except ProviderResponseError:
        return (
            False,
            f"{provider_label} returned an unexpected API response. "
            "The credential was not proven invalid. Check the API base and provider availability.",
            "response",
        )
    except ProviderError:
        return (
            False,
            f"{provider_label} could not validate the bot credential safely. "
            "The credential was not proven invalid.",
            "response",
        )
    except Exception:
        # Unknown failures must never be treated as proof that a secret is bad.
        # Exception text may contain request URLs that embed the bot token.
        return (
            False,
            f"{provider_label} validation could not complete safely. "
            "The credential was not proven invalid.",
            "response",
        )
    finally:
        client = getattr(bot, "client", None)
        close = getattr(client, "close", None)
        if callable(close):
            try:
                close()
            except Exception:
                pass


def _bot_connectivity(cfg: AppConfig, token: str) -> tuple[bool, str]:
    ok, detail, _kind = check_bot_connectivity_detailed(cfg, token)
    return ok, detail


def _camera_ok(index: int) -> tuple[bool, str]:
    try:
        from .camera_devices import probe_camera

        ok, resolution = probe_camera(index)
    except Exception:
        return False, f"Camera {index} could not be checked."
    if not ok:
        return False, f"Camera {index} is not usable."
    if resolution:
        return True, f"Camera {index} is usable at {resolution[0]}x{resolution[1]}."
    return True, f"Camera {index} is usable."


def _run_quiet(command: list[str], *, timeout: int = 5, capture: bool = False):
    try:
        return subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=capture,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError):
        return None


def _microphone_ok(cfg: AppConfig) -> tuple[bool, str]:
    if not shutil.which("ffmpeg"):
        return False, "ffmpeg is missing, so microphone recording is unavailable."

    backend = str(cfg.audio.backend or "auto").lower()
    source = str(cfg.audio.input or "default").strip()

    if backend in {"auto", "pulse"} and shutil.which("pactl"):
        result = _run_quiet(["pactl", "list", "short", "sources"], capture=True)
        if result and result.returncode == 0:
            sources = []
            for line in (result.stdout or "").splitlines():
                parts = line.split("\t")
                if len(parts) >= 2 and ".monitor" not in parts[1]:
                    sources.append(parts[1])
            if source in {"", "default"} and sources:
                return True, "A microphone source is available through PulseAudio/PipeWire."
            if source in sources:
                return True, "The configured microphone source is available."
            return False, "The configured microphone source is not currently available."
        if backend == "pulse":
            return False, "PulseAudio/PipeWire microphone discovery is unavailable."

    if backend in {"auto", "alsa"} and shutil.which("arecord"):
        result = _run_quiet(["arecord", "-l"], capture=True)
        if result and result.returncode == 0:
            return True, "An ALSA microphone/capture device is available."
        return False, "No usable ALSA microphone/capture device was found."

    return False, "No supported microphone discovery tool is installed."


def _lock_backend_ok() -> tuple[bool, str]:
    if platform.system() != "Linux":
        return False, "The current release requires a supported Linux lock backend."
    if shutil.which("loginctl") or shutil.which("xdg-screensaver"):
        return True, "A Linux screen-lock backend is available."
    return False, "No supported Linux screen-lock backend was found."


def _warning_video_ok() -> tuple[bool, str]:
    try:
        from .warning_sequence import VIDEO_PATH

        ok = VIDEO_PATH.exists() and VIDEO_PATH.stat().st_size > 0
    except Exception:
        ok = False
    return (True, "Warning countdown video is present.") if ok else (False, "Warning countdown video is missing.")


def _video_player_ok() -> tuple[bool, str]:
    if shutil.which("ffplay") or shutil.which("mpv") or shutil.which("cvlc") or shutil.which("vlc"):
        return True, "A fullscreen video player is available."
    return False, "No supported fullscreen video player was found."


def _screenshot_backend_ok() -> tuple[bool, str]:
    if platform.system() != "Linux":
        return False, "Screen capture is supported only on the current Linux target."
    if shutil.which("gnome-screenshot") or shutil.which("grim") or shutil.which("spectacle"):
        return True, "A screenshot backend is available."
    if os.environ.get("DISPLAY") and shutil.which("import"):
        return True, "ImageMagick screenshot backend is available."
    return False, "No supported screenshot backend was found for this desktop session."


def _screen_video_backend_ok() -> tuple[bool, str]:
    if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wf-recorder"):
        return True, "Wayland screen recording is available through wf-recorder."
    if os.environ.get("DISPLAY") and shutil.which("ffmpeg"):
        return True, "X11 screen recording is available through ffmpeg."
    return False, "No supported screen-recording backend was found for this desktop session."


def _failed_login_monitor_ok() -> tuple[bool, str]:
    if platform.system() != "Linux" or not shutil.which("journalctl"):
        return False, "systemd journal access is unavailable."
    result = _run_quiet(["journalctl", "--lines=1", "--output=json", "--no-pager"])
    if result and result.returncode == 0:
        return True, "System journal authentication events are readable."
    return False, "System journal authentication events are not readable by this user."


def _autostart_ok() -> tuple[bool, str]:
    if not shutil.which("systemctl"):
        return False, "systemctl is unavailable."
    try:
        from .service import SERVICE_PATH

        if not SERVICE_PATH.exists():
            return False, "Laptop Guard user service has not been installed."
    except Exception:
        return False, "Laptop Guard user service could not be inspected."
    result = _run_quiet(["systemctl", "--user", "is-enabled", "laptop-guard.service"])
    if result and result.returncode == 0:
        return True, "Laptop Guard autostart is enabled."
    return False, "Laptop Guard autostart is not enabled."


def _service_active_ok() -> tuple[bool, str]:
    if not shutil.which("systemctl"):
        return False, "systemctl is unavailable."
    result = _run_quiet(["systemctl", "--user", "is-active", "laptop-guard.service"])
    if result and result.returncode == 0:
        return True, "Laptop Guard user service is running."
    return False, "Laptop Guard user service is not currently running."


def _tk_ok() -> tuple[bool, str]:
    try:
        import tkinter  # noqa: F401

        return True, "Tkinter local chat UI is available."
    except Exception:
        return False, "Tkinter local chat UI is unavailable."


def _persian_tts_ok() -> tuple[bool, str]:
    ok = importlib.util.find_spec("py_persian_tts") is not None
    return (True, "Persian TTS package is installed.") if ok else (False, "Persian TTS package is missing.")


def _audio_player_ok() -> tuple[bool, str]:
    if shutil.which("ffplay") or shutil.which("paplay") or shutil.which("pw-play") or shutil.which("aplay"):
        return True, "An audio playback backend is available."
    return False, "No supported audio playback backend was found."


def _lock_required(cfg: AppConfig) -> bool:
    return bool(
        cfg.security.lock_on_guard_exit
        or cfg.security.lock_after_countdown
        or cfg.security.input_action in {"lock", "warning_lock"}
    )


def collect_checks() -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []

    linux = platform.system() == "Linux"
    checks.append(_check(
        "Supported operating system",
        "required",
        linux,
        "Linux detected." if linux else "This release is supported on Linux/Ubuntu-oriented desktops.",
        "Use a supported Linux/Ubuntu-oriented system for the current release.",
    ))

    ok, detail = _python_version_ok()
    checks.append(_check(
        "Python version",
        "required",
        ok,
        detail,
        "Install Python 3.11 or newer, then run: ./install.sh",
    ))

    ok, detail = _venv_health_ok()
    checks.append(_check(
        "Python virtual environment",
        "required",
        ok,
        detail,
        "Run: ./install.sh",
    ))

    ok, detail = _python_dependencies_ok()
    checks.append(_check(
        "Python dependencies",
        "required",
        ok,
        detail,
        "Run: ./install.sh",
    ))

    config_ok, detail = _config_integrity()
    checks.append(_check(
        "Configuration integrity",
        "required",
        config_ok,
        detail,
        "Run: ./run.sh setup",
    ))

    secret_ok, secret_detail = _secret_permissions_ok()
    secret_path = str(config_module.SECRETS_PATH)
    checks.append(_check(
        "Secret-file permissions",
        "required",
        secret_ok,
        secret_detail,
        f"Run: chmod 600 {secret_path} && ./run.sh doctor",
    ))

    if not config_ok:
        checks.append(_check(
            "Configured feature checks",
            "optional",
            True,
            "Skipped until configuration is repaired.",
        ))
        return checks

    cfg = config_module.load_config()
    setup_ok = bool(cfg.setup_complete)
    checks.append(_check(
        "Guided setup",
        "required",
        setup_ok,
        "Guided setup is complete." if setup_ok else "Guided setup is incomplete.",
        "Run: ./run.sh setup",
    ))

    if not setup_ok:
        return checks

    remote_provider = cfg.bot.provider != "local"
    token = config_module.get_bot_token(cfg.bot.provider) if remote_provider else ""
    checks.append(_check(
        "Bot token",
        "required" if remote_provider else "optional",
        (not remote_provider) or bool(token),
        "Stored bot credential is present." if token else ("Not needed in local mode." if not remote_provider else "Bot token is missing."),
        "Run: ./run.sh setup",
    ))

    bot_ok, bot_detail = _bot_connectivity(cfg, token)
    checks.append(_check(
        "Bot connectivity",
        "required" if remote_provider else "optional",
        bot_ok,
        bot_detail,
        "Check internet/proxy settings, then run: ./run.sh setup",
    ))

    owner_ok = (not remote_provider) or isinstance(cfg.bot.chat_id, int)
    checks.append(_check(
        "Owner pairing",
        "required" if remote_provider else "optional",
        owner_ok,
        "Owner chat is paired." if owner_ok and remote_provider else ("Not needed in local mode." if not remote_provider else "Owner chat is not paired."),
        "Run: ./run.sh setup",
    ))

    if cfg.camera.enabled:
        ok, detail = _camera_ok(cfg.camera.index)
        checks.append(_check(
            "Camera",
            "required",
            ok,
            detail,
            "Run: ./run.sh test camera; if it fails, reconnect/allow the camera and rerun ./run.sh setup",
        ))
    else:
        checks.append(_check("Camera", "optional", True, "Camera is disabled by configuration."))

    mic_required = bool(cfg.audio.sound_detection_enabled)
    ok, detail = _microphone_ok(cfg)
    checks.append(_check(
        "Microphone recording",
        "required" if mic_required else "recommended",
        ok,
        detail,
        "Run: ./run.sh test microphone. On Ubuntu, install audio tools with: sudo apt install ffmpeg pulseaudio-utils alsa-utils",
    ))

    if _lock_required(cfg):
        ok, detail = _lock_backend_ok()
        checks.append(_check(
            "Screen-lock backend",
            "required",
            ok,
            detail,
            "Run: ./run.sh test lock. On Ubuntu, install the fallback backend with: sudo apt install xdg-utils",
        ))
    else:
        checks.append(_check("Screen-lock backend", "optional", True, "Automatic locking is disabled by configuration."))

    if cfg.security.warning_video:
        ok, detail = _warning_video_ok()
        checks.append(_check(
            "Warning video asset",
            "required",
            ok,
            detail,
            "Restore the packaged warning media, then rerun: ./install.sh",
        ))
        ok, detail = _video_player_ok()
        checks.append(_check(
            "Warning video player",
            "required",
            ok,
            detail,
            "On Ubuntu run: sudo apt install ffmpeg",
        ))
    else:
        checks.append(_check("Warning video", "optional", True, "Warning video is disabled by configuration."))

    screenshot_required = bool(cfg.screen.screenshots_enabled or cfg.security.input_screen_snapshot)
    if screenshot_required:
        ok, detail = _screenshot_backend_ok()
        checks.append(_check(
            "Screenshot backend",
            "required",
            ok,
            detail,
            "On Ubuntu GNOME run: sudo apt install gnome-screenshot; then rerun ./run.sh doctor",
        ))
    else:
        checks.append(_check("Screenshot backend", "optional", True, "Screenshot features are disabled by configuration."))

    video_required = bool(cfg.screen.screen_video_enabled or cfg.security.input_screen_video_seconds > 0)
    if video_required:
        ok, detail = _screen_video_backend_ok()
        checks.append(_check(
            "Screen-recording backend",
            "required",
            ok,
            detail,
            "For X11 install ffmpeg; for compatible Wayland compositors install wf-recorder, or disable screen recording in ./run.sh setup",
        ))
    else:
        checks.append(_check("Screen-recording backend", "optional", True, "Screen recording is disabled by configuration."))

    if cfg.monitors.failed_login_events:
        ok, detail = _failed_login_monitor_ok()
        checks.append(_check(
            "Failed-login journal access",
            "required",
            ok,
            detail,
            "Run: journalctl --lines=1 --no-pager. If access is denied, grant this user journal access or disable failed-login monitoring in ./run.sh setup",
        ))
    else:
        checks.append(_check("Failed-login journal access", "optional", True, "Failed-login monitoring is disabled by configuration."))

    if cfg.startup.enabled:
        ok, detail = _autostart_ok()
        checks.append(_check(
            "Autostart service",
            "required",
            ok,
            detail,
            "Run: ./run.sh autostart on",
        ))
        active, active_detail = _service_active_ok()
        checks.append(_check(
            "Service currently running",
            "recommended",
            active,
            active_detail,
            "Run: systemctl --user start laptop-guard.service",
        ))
    else:
        checks.append(_check("Autostart service", "optional", True, "Autostart is disabled by configuration."))

    if cfg.tts.enabled:
        ok, detail = _persian_tts_ok()
        checks.append(_check(
            "Persian TTS package",
            "required",
            ok,
            detail,
            "Run: .venv/bin/pip install py-persian-tts==3.0.2",
        ))
        ok, detail = _audio_player_ok()
        checks.append(_check(
            "Audio playback backend",
            "required",
            ok,
            detail,
            "On Ubuntu run: sudo apt install ffmpeg",
        ))
    else:
        checks.append(_check("Persian TTS", "optional", True, "Text-to-speech is disabled by configuration."))

    ok, detail = _tk_ok()
    checks.append(_check(
        "Tkinter local chat UI",
        "recommended",
        ok,
        detail,
        "On Ubuntu run: sudo apt install python3-tk",
    ))

    if cfg.security.stop_auth_enabled:
        pin_ok = StopPinStore().configured
        checks.append(_check(
            "Protected-stop PIN",
            "recommended",
            pin_ok,
            "Protected-stop PIN is configured." if pin_ok else "Protected stop is enabled but no PIN has been configured yet.",
            "After the authorized owner connection is running, set the Stop PIN with /stoppin.",
        ))

    return checks


def check_bot_connectivity(cfg: AppConfig, token: str) -> tuple[bool, str]:
    """Backward-compatible token-safe provider validation for setup and doctor."""
    return _bot_connectivity(cfg, token)


def validate_setup_section(cfg: AppConfig, section: str) -> tuple[bool, str]:
    """Validate one guided-setup section using doctor readiness helpers."""
    section = str(section or "").strip().lower()

    if section == "identity":
        if not str(cfg.device_name or "").strip():
            return False, "Device name is empty."
        if cfg.profile not in {"away", "home", "night", "testing", "custom"}:
            return False, "Starting profile is invalid."
        return True, "Identity and profile are valid."

    if section == "provider":
        if cfg.bot.provider == "local":
            return True, "Local provider needs no bot credential."
        if cfg.bot.provider not in {"bale", "telegram"}:
            return False, "Notification provider is invalid."
        if not str(cfg.bot.api_base or "").strip():
            return False, "Provider API base is empty."
        return _bot_connectivity(
            cfg,
            config_module.get_bot_token(cfg.bot.provider),
        )

    if section == "owner":
        if cfg.bot.provider == "local":
            return True, "Local provider needs no remote owner pairing."
        if isinstance(cfg.bot.chat_id, int):
            return True, "Owner pairing is present."
        return False, "Remote provider has no paired owner chat."

    if section == "camera":
        if not cfg.camera.enabled:
            return True, "Camera is disabled by configuration."
        return _camera_ok(cfg.camera.index)

    if section == "audio":
        if cfg.audio.sound_detection_enabled:
            ok, detail = _microphone_ok(cfg)
            if not ok:
                return ok, detail
        if cfg.audio.tts_enabled:
            ok, detail = _audio_player_ok()
            if not ok:
                return ok, detail
        return True, "Configured audio features are usable."

    if section == "security":
        if cfg.security.input_action not in {"warning_lock", "warning", "notify", "lock"}:
            return False, "Unexpected-input action is invalid."
        if cfg.security.input_backend not in {"auto", "evdev", "pynput"}:
            return False, "Input-monitor backend is invalid."
        return True, "Security behavior values are valid."

    if section == "communication":
        if cfg.communication.surface not in {"guard_chat", "live_notepad", "both", "fullscreen"}:
            return False, "Communication surface is invalid."
        return True, "Communication surface is valid."

    if section == "screen":
        if cfg.screen.screenshots_enabled:
            ok, detail = _screenshot_backend_ok()
            if not ok:
                return ok, detail
        if cfg.screen.screen_video_enabled:
            ok, detail = _screen_video_backend_ok()
            if not ok:
                return ok, detail
        return True, "Configured screen-capture features are usable."

    if section == "apps_api":
        if cfg.api.enabled:
            if cfg.api.host != "127.0.0.1":
                return False, "Local API host must remain 127.0.0.1."
            if not 1024 <= int(cfg.api.port) <= 65535:
                return False, "Local API port is outside the supported range."
            if not config_module.get_api_token():
                return False, "Local API is enabled but its protected token is missing."
        return True, "Apps and local API configuration are valid."

    if section == "monitors":
        if cfg.monitors.failed_login_events:
            return _failed_login_monitor_ok()
        return True, "Configured monitoring features are valid."

    if section == "startup":
        if cfg.startup.enabled:
            return _autostart_ok()
        return True, "Autostart is disabled by configuration."

    return False, f"Unknown setup section: {section}"


def _print_group(title: str, category: Category, checks: list[DoctorCheck]) -> None:
    group = [item for item in checks if item.category == category]
    if not group:
        return
    print(f"\n{title}")
    print("-" * len(title))
    for item in group:
        if item.ok:
            status = "OK" if category != "optional" else "INFO"
        else:
            status = "FAIL" if category == "required" else "WARN"
        print(f"[{status}] {item.name}: {item.detail}")
        if not item.ok and item.action:
            print(f"       Next step: {item.action}")


def run_doctor() -> int:
    checks = collect_checks()
    print("Laptop Guard readiness doctor")
    print("Checks are based on the features currently enabled in your configuration.")

    _print_group("Required", "required", checks)
    _print_group("Recommended", "recommended", checks)
    _print_group("Optional / disabled", "optional", checks)

    required_failed = [item for item in checks if item.category == "required" and not item.ok]
    recommended_failed = [item for item in checks if item.category == "recommended" and not item.ok]

    print("\nReadiness summary")
    print("-----------------")
    if required_failed:
        count = len(required_failed)
        print(f"NOT READY: {count} required check{'s' if count != 1 else ''} need attention.")
        print("Fix the required items above, then run: ./run.sh doctor")
        return 2

    print("READY: all required checks passed for the configured feature set.")
    if recommended_failed:
        count = len(recommended_failed)
        print(f"{count} recommended check{'s' if count != 1 else ''} can still be improved without blocking startup.")
    print("Next: ./run.sh")
    return 0


def main() -> int:
    return run_doctor()


if __name__ == "__main__":
    raise SystemExit(main())
