from __future__ import annotations

import json
import os
import re
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .config import LOG_DIR, get_api_token, get_bot_tokens

if TYPE_CHECKING:
    from rich.console import Console

    from .models import AppConfig

DIAGNOSTICS_PATH = LOG_DIR / "runtime-diagnostics.jsonl"


@dataclass(frozen=True, slots=True)
class RecoveryGuidance:
    capability: str
    summary: str
    actions: tuple[str, ...]


class GuidedRuntimeError(RuntimeError):
    def __init__(self, guidance: RecoveryGuidance) -> None:
        super().__init__(guidance.summary)
        self.guidance = guidance


def is_provider_auth_error(exc: BaseException) -> bool:
    try:
        from .providers.base import ProviderAuthError

        if isinstance(exc, ProviderAuthError):
            return True
    except Exception:
        pass

    text = str(exc).lower()
    return any(
        marker in text
        for marker in (
            "401",
            "unauthorized",
            "invalid token",
            "token is invalid",
            "forbidden token",
            "expired token",
        )
    )


def _known_secrets() -> tuple[str, ...]:
    values: list[str] = []
    try:
        bot_tokens = get_bot_tokens()
    except Exception:
        bot_tokens = ()
    for value in bot_tokens:
        clean = str(value or "").strip()
        if len(clean) >= 4 and clean not in values:
            values.append(clean)

    try:
        api_token = get_api_token().strip()
    except Exception:
        api_token = ""
    if len(api_token) >= 4 and api_token not in values:
        values.append(api_token)
    return tuple(values)


def sanitize_diagnostic(text: str) -> str:
    clean = str(text or "")
    for value in _known_secrets():
        clean = clean.replace(value, "<redacted>")

    clean = re.sub(
        r"(?i)(/bot)[^/\s?]+",
        r"\1<redacted>",
        clean,
    )
    clean = re.sub(
        r"(?i)(authorization\s*[:=]\s*(?:bearer\s+)?)[^\s,;]+",
        r"\1<redacted>",
        clean,
    )
    clean = re.sub(
        r"(?i)((?:bot_?token|api_?token|api_?key|token)\s*[:=]\s*)[^\s,;]+",
        r"\1<redacted>",
        clean,
    )
    return clean


def write_runtime_diagnostic(
    context: str,
    exc: BaseException,
    *,
    path: Path = DIAGNOSTICS_PATH,
) -> Path | None:
    """Append a sanitized diagnostic record without exposing stored credentials."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tb = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
        record = {
            "time": datetime.now().astimezone().isoformat(timespec="seconds"),
            "context": str(context),
            "exception_type": type(exc).__name__,
            "message": sanitize_diagnostic(str(exc)),
            "traceback": sanitize_diagnostic(tb),
        }
        flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        fd = os.open(path, flags, 0o600)
        try:
            os.chmod(path, 0o600)
            with os.fdopen(fd, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            try:
                os.close(fd)
            except OSError:
                pass
            raise
        return path
    except OSError:
        return None


def print_recovery(
    console: Console,
    guidance: RecoveryGuidance,
    *,
    diagnostic_path: Path | None = None,
) -> None:
    console.print(f"[red]{guidance.capability} needs attention.[/red]")
    console.print(guidance.summary)
    console.print("[bold]Next actions:[/bold]")
    for action in guidance.actions:
        console.print(f"  - {action}")
    if diagnostic_path is not None:
        console.print(f"[dim]Diagnostic details: {diagnostic_path}[/dim]")


def configuration_recovery(exc: BaseException) -> RecoveryGuidance:
    text = str(exc).lower()

    if "owner chat" in text or "pair" in text:
        return RecoveryGuidance(
            "Owner pairing",
            "The remote owner is not paired or the saved pairing needs repair.",
            (
                "Run: ./run.sh reconfigure owner",
                "Then test it with: ./run.sh test bot",
                "If the problem remains, run: ./run.sh doctor",
            ),
        )

    if any(
        marker in text
        for marker in ("token", "credential", "authentication", "unauthorized", "401")
    ):
        return RecoveryGuidance(
            "Provider credentials",
            "The configured bot credential is missing, expired, rejected, or could not be validated.",
            (
                "Run: ./run.sh reconfigure provider",
                "If the provider/account changed, run: ./run.sh reconfigure owner",
                "Then test it with: ./run.sh test bot",
            ),
        )

    if any(
        marker in text
        for marker in ("could not reach", "bot service", "network", "proxy", "timed out")
    ):
        return RecoveryGuidance(
            "Notification provider",
            "Laptop Guard could not reach the configured bot provider.",
            (
                "Check the network/proxy settings.",
                "Run: ./run.sh test bot",
                "If provider settings changed, run: ./run.sh reconfigure provider",
            ),
        )

    if "unsupported provider" in text or "provider" in text:
        return RecoveryGuidance(
            "Notification provider",
            "The saved notification-provider configuration is not usable.",
            (
                "Run: ./run.sh reconfigure provider",
                "Then run: ./run.sh doctor",
            ),
        )

    return RecoveryGuidance(
        "Runtime configuration",
        "Laptop Guard cannot start with the current saved configuration.",
        (
            "Run: ./run.sh setup",
            "Then run: ./run.sh doctor",
        ),
    )


def _capability_guidance(capability: str) -> RecoveryGuidance:
    if capability == "camera":
        return RecoveryGuidance(
            "Camera",
            "Camera protection is enabled, but the configured camera is unavailable or cannot be opened.",
            (
                "Run: ./run.sh test camera",
                "Reconnect/allow the camera, or run: ./run.sh reconfigure camera",
                "If camera protection is optional for you, disable it in the Camera section.",
            ),
        )
    if capability == "audio":
        return RecoveryGuidance(
            "Audio",
            "An enabled audio feature cannot use the configured microphone or playback backend.",
            (
                "Run: ./run.sh test microphone",
                "On Ubuntu, install audio backends with: sudo apt install ffmpeg pulseaudio-utils alsa-utils",
                "Or run: ./run.sh reconfigure audio and disable the optional audio feature.",
            ),
        )
    if capability == "input":
        return RecoveryGuidance(
            "Keyboard / mouse monitoring",
            "Laptop Guard cannot read input activity with the configured backend.",
            (
                "Run: ./run.sh test input",
                "Run: ./run.sh reconfigure security and choose auto/pynput if appropriate.",
                "If evdev is required, review /dev/input permissions; on Ubuntu the input group may require sign-out/sign-in after access is granted.",
            ),
        )
    if capability == "screen":
        return RecoveryGuidance(
            "Screen capture",
            "An enabled screen-capture feature has no usable backend in this desktop session.",
            (
                "Run: ./run.sh test screen",
                "Run: ./run.sh reconfigure screen to disable an optional capture feature.",
                "Then run: ./run.sh doctor",
            ),
        )
    if capability == "journal":
        return RecoveryGuidance(
            "Failed-login monitoring",
            "Failed-login monitoring is enabled, but this user cannot read the required system journal.",
            (
                "Run: journalctl --lines=1 --no-pager",
                "Grant this user journal access, or run: ./run.sh reconfigure monitors and disable failed-login monitoring.",
                "Then run: ./run.sh doctor",
            ),
        )
    if capability == "lock":
        return RecoveryGuidance(
            "Screen lock",
            "The configured security behavior needs a desktop lock backend, but none is available.",
            (
                "Run: ./run.sh test lock",
                "On Ubuntu, install the fallback tools with: sudo apt install xdg-utils",
                "Then run: ./run.sh doctor",
            ),
        )
    return RecoveryGuidance(
        "Runtime dependency",
        "A required runtime dependency or backend is unavailable.",
        (
            "Run: ./run.sh doctor",
            "Then rerun the specific hardware test shown by Doctor.",
        ),
    )


def startup_recovery_issues(cfg: AppConfig) -> list[RecoveryGuidance]:
    """Return configured startup capabilities that need recovery before Guard starts."""
    from . import doctor
    from .input_monitor import InputMonitor

    issues: list[RecoveryGuidance] = []

    if cfg.camera.enabled:
        ok, _detail = doctor.validate_setup_section(cfg, "camera")
        if not ok:
            issues.append(_capability_guidance("camera"))

    audio_problem = False
    if cfg.audio.sound_detection_enabled:
        ok, _detail = doctor._microphone_ok(cfg)
        audio_problem = not ok

    playback_required = bool(
        cfg.audio.tts_enabled
        or cfg.tts.enabled
        or cfg.audio.play_remote_voice
    )
    if playback_required and not audio_problem:
        ok, _detail = doctor._audio_player_ok()
        audio_problem = not ok

    if cfg.tts.enabled and not audio_problem:
        ok, _detail = doctor._persian_tts_ok()
        audio_problem = not ok

    if audio_problem:
        issues.append(_capability_guidance("audio"))

    try:
        monitor = InputMonitor(
            cfg.security.mouse_move_threshold,
            lambda *_: None,
            backend=cfg.security.input_backend,
        )
        input_ok = monitor.available
    except Exception:
        input_ok = False
    if not input_ok:
        issues.append(_capability_guidance("input"))

    screenshot_required = bool(
        cfg.screen.screenshots_enabled
        or cfg.security.input_screen_snapshot
    )
    video_required = bool(
        cfg.screen.screen_video_enabled
        or cfg.security.input_screen_video_seconds > 0
    )
    screen_problem = False
    if screenshot_required:
        ok, _detail = doctor._screenshot_backend_ok()
        screen_problem = not ok
    if video_required and not screen_problem:
        ok, _detail = doctor._screen_video_backend_ok()
        screen_problem = not ok
    if screen_problem:
        issues.append(_capability_guidance("screen"))

    if cfg.monitors.failed_login_events:
        ok, _detail = doctor.validate_setup_section(cfg, "monitors")
        if not ok:
            issues.append(_capability_guidance("journal"))

    if doctor._lock_required(cfg):
        ok, _detail = doctor._lock_backend_ok()
        if not ok:
            issues.append(_capability_guidance("lock"))

    return issues


def guidance_for_exception(
    context: str,
    exc: BaseException,
) -> RecoveryGuidance | None:
    context_key = str(context or "").lower()
    text = str(exc).lower()

    if is_provider_auth_error(exc):
        return configuration_recovery(exc)

    if "provider" in context_key or "bot" in context_key:
        try:
            from .providers.base import ProviderConnectionError

            provider_connection_error = isinstance(exc, ProviderConnectionError)
        except Exception:
            provider_connection_error = False

        if provider_connection_error or any(
            marker in text
            for marker in (
                "connection",
                "network",
                "could not reach",
                "timeout",
                "timed out",
                "name resolution",
                "proxy",
            )
        ):
            return RecoveryGuidance(
                "Notification provider",
                "Laptop Guard could not reach the configured bot provider.",
                (
                    "Check the network/proxy settings.",
                    "Run: ./run.sh test bot",
                    "If credentials changed, run: ./run.sh reconfigure provider",
                ),
            )

    permission = isinstance(exc, PermissionError) or any(
        marker in text for marker in ("permission denied", "operation not permitted", "access denied")
    )
    if permission:
        if "camera" in context_key:
            return _capability_guidance("camera")
        if "audio" in context_key or "microphone" in context_key:
            return _capability_guidance("audio")
        if "screen" in context_key:
            return _capability_guidance("screen")
        if "journal" in context_key:
            return _capability_guidance("journal")
        return _capability_guidance("input")

    if isinstance(exc, (ModuleNotFoundError, ImportError, FileNotFoundError)):
        if any(marker in context_key for marker in ("audio", "microphone")):
            return _capability_guidance("audio")
        if "camera" in context_key:
            return _capability_guidance("camera")
        if "screen" in context_key:
            return _capability_guidance("screen")
        return _capability_guidance("dependency")

    if any(marker in text for marker in ("ffmpeg", "pactl", "alsa", "pulse")):
        return _capability_guidance("audio")
    if any(marker in text for marker in ("camera", "video capture", "v4l2")):
        return _capability_guidance("camera")
    if any(marker in text for marker in ("evdev", "/dev/input", "pynput")):
        return _capability_guidance("input")

    return None
