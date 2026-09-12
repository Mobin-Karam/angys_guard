from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SERVICE_DIR = Path.home() / ".config" / "systemd" / "user"
SERVICE_PATH = SERVICE_DIR / "laptop-guard.service"


def autostart_enabled() -> bool:
    result = subprocess.run(
        ["systemctl", "--user", "is-enabled", "laptop-guard.service"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def set_autostart(enabled: bool, *, start_now: bool = True) -> bool:
    """Enable/disable startup at graphical user login.

    Laptop Guard needs the user's graphical session, so this intentionally uses
    a user service instead of a pre-login system service.
    """
    from .config import load_config, save_config

    cfg = load_config()
    cfg.startup.enabled = bool(enabled)
    save_config(cfg)
    if enabled:
        if not SERVICE_PATH.exists() and not install_service(start_now=False):
            return False
        action = ["systemctl", "--user", "enable"]
        if start_now:
            action.append("--now")
        action.append("laptop-guard.service")
    else:
        action = ["systemctl", "--user", "disable"]
        if start_now:
            action.append("--now")
        action.append("laptop-guard.service")
    return subprocess.run(action, check=False).returncode == 0


def install_service(*, start_now: bool = True) -> bool:
    from .config import get_bot_token, load_config, setup_is_complete

    if not setup_is_complete():
        print("Laptop Guard setup is incomplete. Run './run.sh setup' interactively first.")
        return False
    cfg = load_config()
    if cfg.bot.provider != "local" and not get_bot_token():
        print("Bot token is missing. Run './run.sh' interactively to configure it first.")
        return False

    SERVICE_DIR.mkdir(parents=True, exist_ok=True)
    content = f"""[Unit]\nDescription=Laptop Guard v11\nAfter=network-online.target graphical-session.target\nWants=network-online.target\n\n[Service]\nType=simple\nExecStart={sys.executable} -m laptop_guard run\nRestart=always\nRestartSec=5\nEnvironment=PYTHONUNBUFFERED=1\nPassEnvironment=DISPLAY WAYLAND_DISPLAY XDG_SESSION_TYPE XDG_CURRENT_DESKTOP DESKTOP_SESSION XDG_RUNTIME_DIR DBUS_SESSION_BUS_ADDRESS PULSE_SERVER\n\n[Install]\nWantedBy=default.target\n"""
    SERVICE_PATH.write_text(content, encoding="utf-8")
    reload_result = subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    command = ["systemctl", "--user", "enable"]
    if start_now:
        command.append("--now")
    command.append("laptop-guard.service")
    enable_result = subprocess.run(command, check=False)
    return reload_result.returncode == 0 and enable_result.returncode == 0


def uninstall_service() -> bool:
    disable_result = subprocess.run(["systemctl", "--user", "disable", "--now", "laptop-guard.service"], check=False)
    SERVICE_PATH.unlink(missing_ok=True)
    reload_result = subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    return disable_result.returncode == 0 and reload_result.returncode == 0


def status_service() -> bool:
    result = subprocess.run(["systemctl", "--user", "status", "laptop-guard.service", "--no-pager"], check=False)
    return result.returncode == 0


def logs_service() -> bool:
    result = subprocess.run(["journalctl", "--user", "-u", "laptop-guard.service", "-n", "150", "--no-pager"], check=False)
    return result.returncode == 0
