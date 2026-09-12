from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SERVICE_DIR = Path.home() / ".config" / "systemd" / "user"
SERVICE_PATH = SERVICE_DIR / "laptop-guard.service"


def install_service() -> None:
    SERVICE_DIR.mkdir(parents=True, exist_ok=True)
    content = f"""[Unit]\nDescription=Laptop Guard v6\nAfter=network-online.target graphical-session.target\nWants=network-online.target\n\n[Service]\nType=simple\nExecStart={sys.executable} -m laptop_guard run\nRestart=always\nRestartSec=5\nEnvironment=PYTHONUNBUFFERED=1\nPassEnvironment=DISPLAY WAYLAND_DISPLAY XDG_SESSION_TYPE XDG_CURRENT_DESKTOP DESKTOP_SESSION XDG_RUNTIME_DIR DBUS_SESSION_BUS_ADDRESS PULSE_SERVER\n\n[Install]\nWantedBy=default.target\n"""
    SERVICE_PATH.write_text(content, encoding="utf-8")
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "--user", "enable", "--now", "laptop-guard.service"], check=False)


def uninstall_service() -> None:
    subprocess.run(["systemctl", "--user", "disable", "--now", "laptop-guard.service"], check=False)
    SERVICE_PATH.unlink(missing_ok=True)
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)


def status_service() -> None:
    subprocess.run(["systemctl", "--user", "status", "laptop-guard.service", "--no-pager"], check=False)


def logs_service() -> None:
    subprocess.run(["journalctl", "--user", "-u", "laptop-guard.service", "-n", "150", "--no-pager"], check=False)
