from __future__ import annotations

import platform
import shutil

from .config import load_config
from .warning_sequence import ASSET_DIR


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


def _warning_assets_ok() -> bool:
    return all((ASSET_DIR / f"{n}.png").exists() for n in range(1, 6))


def main() -> int:
    cfg = load_config()
    linux = platform.system() != "Windows"
    checks = [
        ("Bale token configured", bool(cfg.bale.token), True),
        ("Bale chat id configured", cfg.bale.chat_id is not None, False),
        ("Tkinter fullscreen UI", _tk_ok(), False),
        ("Warning images 1..5", _warning_assets_ok(), True),
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
        ("Remote unlock opt-in", cfg.security.allow_remote_unlock, False),
    ]
    width = max(len(name) for name, _, _ in checks)
    for name, ok, required in checks:
        label = "OK" if ok else ("MISSING" if required else "OFF/OPTIONAL")
        print(f"{name:<{width}} : {label}")
    if not _tk_ok():
        print("\nTkinter is optional for the core bot. Install python3-tk to enable fullscreen warning/chat windows.")
    if cfg.security.lock_on_guard_exit:
        print("Exit-lock: enabled. Closing/killing the guard process requests an immediate OS lock.")
    if cfg.tts.enabled and not _persian_tts_ok():
        print("Persian TTS is enabled but py-persian-tts is missing. Run: .venv/bin/pip install py-persian-tts==3.0.2")
    return 0 if bool(cfg.bale.token) and _warning_assets_ok() else 2


if __name__ == "__main__":
    raise SystemExit(main())
