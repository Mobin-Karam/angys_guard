from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
import time
from pathlib import Path


def _run_first(commands: list[list[str]], timeout: int = 8) -> bool:
    for cmd in commands:
        if not cmd:
            continue
        if os.path.sep not in cmd[0] and not shutil.which(cmd[0]):
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
        except (OSError, subprocess.SubprocessError):
            continue
    return False


def lock_screen() -> bool:
    if platform.system() == "Windows":
        return _run_first([["rundll32.exe", "user32.dll,LockWorkStation"]], timeout=5)
    return _run_first(
        [
            ["loginctl", "lock-session"],
            ["xdg-screensaver", "lock"],
            ["gnome-screensaver-command", "-l"],
        ]
    )


def unlock_screen() -> tuple[bool, str]:
    """Best-effort owner-requested session unlock.

    Windows intentionally returns unsupported: bypassing the Windows secure
    logon screen would require credential handling that Laptop Guard does not do.
    Linux uses the session manager's normal unlock request and may still be
    refused by the desktop/session policy.
    """
    if platform.system() == "Windows":
        return False, "Remote unlock is not supported on Windows secure logon."
    ok = _run_first([["loginctl", "unlock-session"]], timeout=5)
    if ok:
        return True, "Linux session unlock requested."
    return False, "The current Linux session manager refused or does not support remote unlock."


def suspend_system() -> bool:
    if platform.system() == "Windows":
        return _run_first(
            [["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"]],
            timeout=5,
        )
    return _run_first([["systemctl", "suspend"], ["loginctl", "suspend"]], timeout=8)


def reboot_system() -> bool:
    if platform.system() == "Windows":
        return _run_first([["shutdown", "/r", "/t", "0"]], timeout=5)
    return _run_first([["systemctl", "reboot"], ["loginctl", "reboot"]], timeout=8)


def poweroff_system() -> bool:
    if platform.system() == "Windows":
        return _run_first([["shutdown", "/s", "/t", "0"]], timeout=5)
    return _run_first([["systemctl", "poweroff"], ["loginctl", "poweroff"]], timeout=8)


def _human_bytes(value: int) -> str:
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def system_snapshot() -> dict[str, str]:
    data: dict[str, str] = {
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "arch": platform.machine() or "unknown",
        "python": platform.python_version(),
    }
    try:
        usage = shutil.disk_usage(Path.home())
        data["disk"] = f"{_human_bytes(usage.used)} / {_human_bytes(usage.total)}"
    except OSError:
        data["disk"] = "unknown"

    try:
        import psutil  # type: ignore

        data["uptime"] = _format_duration(max(0, int(time.time() - psutil.boot_time())))
        data["cpu"] = f"{psutil.cpu_percent(interval=0.15):.0f}%"
        mem = psutil.virtual_memory()
        data["memory"] = f"{mem.percent:.0f}% ({_human_bytes(mem.used)} / {_human_bytes(mem.total)})"
        battery = psutil.sensors_battery()
        if battery is not None:
            state = "charging" if battery.power_plugged else "battery"
            data["battery"] = f"{battery.percent:.0f}% ({state})"
        else:
            data["battery"] = "n/a"
    except Exception:
        data.setdefault("uptime", "unknown")
        data.setdefault("cpu", "unknown")
        data.setdefault("memory", "unknown")
        data.setdefault("battery", "unknown")
    return data


def _format_duration(seconds: int) -> str:
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    if days:
        return f"{days}d {hours}h {minutes}m"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
