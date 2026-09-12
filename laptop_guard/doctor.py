from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path

from .config import get_bot_token, load_config
from .warning_sequence import VIDEO_PATH
from .stop_auth import StopPinStore


def _tk_ok() -> bool:
    try:
        import tkinter  # noqa: F401
        return True
    except Exception:
        return False


def _psutil_ok() -> bool:
    try:
        import psutil  # noqa: F401
        return True
    except Exception:
        return False


def _persian_tts_ok() -> bool:
    try:
        import py_persian_tts  # noqa: F401
        return True
    except Exception:
        return False


def _warning_video_ok() -> bool:
    return VIDEO_PATH.exists() and VIDEO_PATH.stat().st_size > 0


def _video_player_ok() -> bool:
    return bool(shutil.which("ffplay") or shutil.which("mpv") or shutil.which("cvlc") or shutil.which("vlc"))


def _failed_login_monitor_ok() -> bool:
    if platform.system() != "Linux" or not shutil.which("journalctl"):
        return False
    try:
        result = subprocess.run(
            ["journalctl", "--lines=1", "--output=json", "--no-pager"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def run_doctor() -> int:
    cfg = load_config()
    linux = platform.system() != "Windows"
    checks = [
        (f"{cfg.bot.provider.title()} token configured", bool(get_bot_token()) if cfg.bot.provider != "local" else True, cfg.bot.provider != "local"),
        ("Owner chat id configured", cfg.bot.chat_id is not None, False),
        ("Tkinter chat UI", _tk_ok(), False),
        ("Warning countdown video", _warning_video_ok(), cfg.security.warning_video),
        ("Fullscreen video player", _video_player_ok(), cfg.security.warning_video),
        ("psutil system status", _psutil_ok(), False),
        ("Persian TTS package", (not cfg.tts.enabled) or _persian_tts_ok(), cfg.tts.enabled),
        ("Audio playback backend", bool(shutil.which("ffplay") or shutil.which("paplay") or shutil.which("pw-play") or shutil.which("aplay")), cfg.tts.enabled),
        ("ffmpeg audio/video", bool(shutil.which("ffmpeg")), False),
        ("notify-send", (not linux) or bool(shutil.which("notify-send")), False),
        ("Linux lock backend", (not linux) or bool(shutil.which("loginctl") or shutil.which("xdg-screensaver")), True),
        ("Linux unlock backend", (not linux) or bool(shutil.which("loginctl")), False),
        ("Screenshot backend", (not linux) or bool(shutil.which("gnome-screenshot") or shutil.which("grim") or shutil.which("spectacle") or shutil.which("import")), False),
        ("Screen video backend", (not linux) or bool(shutil.which("wf-recorder") or shutil.which("ffmpeg")), False),
        ("Exit-lock watchdog", cfg.security.lock_on_guard_exit, False),
        ("Protected Ctrl+C stop", cfg.security.stop_auth_enabled, False),
        ("Stop PIN configured", StopPinStore().configured, False),
        ("Remote unlock opt-in", cfg.security.allow_remote_unlock, False),
        ("Failed-login journal access", _failed_login_monitor_ok(), cfg.monitors.failed_login_events),
    ]
    width = max(len(name) for name, _, _ in checks)
    required_missing = False
    for name, ok, required in checks:
        label = "OK" if ok else ("MISSING" if required else "OFF/OPTIONAL")
        print(f"{name:<{width}} : {label}")
        if required and not ok:
            required_missing = True
    if not _tk_ok():
        print("\nTkinter is optional for the core bot and warning video; install python3-tk only for local Guard Chat UI.")
    if cfg.security.warning_video and not _video_player_ok():
        print("Install ffmpeg (provides ffplay), mpv, or VLC to enable the fullscreen warning video.")
    if cfg.security.lock_on_guard_exit:
        print("Exit-lock: enabled. SIGHUP/SIGTERM/abrupt death lock the OS session; authorized Ctrl+C can exit through PIN + Bale confirmation.")
    if cfg.security.stop_auth_enabled and not StopPinStore().configured:
        print("Protected stop is enabled but no Stop PIN is configured. Set it from the authorized Bale chat with /stoppin.")
    if cfg.tts.enabled and not _persian_tts_ok():
        print("Persian TTS is enabled but py-persian-tts is missing. Run: .venv/bin/pip install py-persian-tts==3.0.2")
    if cfg.monitors.failed_login_events and not _failed_login_monitor_ok():
        print("Failed-login alerts need readable systemd journal authentication entries; check journalctl permissions.")
    return 0 if (cfg.bot.provider == "local" or bool(get_bot_token())) and not required_missing else 2


def main() -> int:
    return run_doctor()


if __name__ == "__main__":
    raise SystemExit(main())
