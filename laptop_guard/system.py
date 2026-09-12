from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def run_first(commands: list[list[str]], timeout: int = 5) -> bool:
    for cmd in commands:
        if not shutil.which(cmd[0]):
            continue
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout,
                check=False,
            )
            if result.returncode == 0:
                return True
        except subprocess.SubprocessError:
            pass
    return False


def lock_screen() -> bool:
    return run_first([["loginctl", "lock-session"], ["xdg-screensaver", "lock"]])


def unlock_screen() -> bool:
    return run_first([["loginctl", "unlock-session"]])


def desktop_notify(title: str, body: str) -> None:
    if shutil.which("notify-send"):
        subprocess.Popen(
            ["notify-send", title, body],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def current_session_type() -> str:
    import os

    return os.environ.get("XDG_SESSION_TYPE", "unknown")
