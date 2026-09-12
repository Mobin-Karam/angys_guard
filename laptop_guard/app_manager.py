from __future__ import annotations

import configparser
import os
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import psutil


@dataclass
class DesktopApp:
    desktop_id: str
    name: str
    exec_bin: str
    path: Path


class AppManager:
    """Conservative GUI application manager.

    It uses .desktop entries rather than exposing an arbitrary shell. Closing is
    limited to the current user's processes whose executable matches a known,
    allowlisted desktop application.
    """

    DENY_EXEC = {"systemd", "gnome-shell", "Xorg", "Xwayland", "dbus-daemon", "pipewire", "wireplumber", "python", "python3"}

    def __init__(self, allowlist: list[str], allow_launch: bool = True, allow_close: bool = True) -> None:
        self.allowlist = set(allowlist)
        self.allow_launch = allow_launch
        self.allow_close = allow_close
        self.apps = self._discover()

    def _discover(self) -> dict[str, DesktopApp]:
        result: dict[str, DesktopApp] = {}
        roots = [Path.home()/".local/share/applications", Path.home()/".local/share/flatpak/exports/share/applications", Path("/usr/share/applications"), Path("/var/lib/snapd/desktop/applications"), Path("/var/lib/flatpak/exports/share/applications")]
        for root in roots:
            if not root.exists():
                continue
            for path in root.glob("*.desktop"):
                try:
                    cp = configparser.ConfigParser(interpolation=None, strict=False)
                    cp.read(path, encoding="utf-8")
                    sec = cp["Desktop Entry"]
                    if sec.get("Type") != "Application" or sec.getboolean("NoDisplay", fallback=False):
                        continue
                    name = sec.get("Name", path.stem).strip()
                    raw_exec = sec.get("Exec", "").strip()
                    if not raw_exec:
                        continue
                    # Strip desktop field codes, keep the executable only.
                    cleaned = re.sub(r"%[fFuUdDnNickvm]", "", raw_exec).strip()
                    parts = shlex.split(cleaned)
                    if not parts:
                        continue
                    exe = os.path.basename(parts[0])
                    result[path.name] = DesktopApp(path.name, name, exe, path)
                except Exception:
                    continue
        return result

    def allowed_apps(self) -> list[DesktopApp]:
        return sorted([a for k, a in self.apps.items() if not self.allowlist or k in self.allowlist], key=lambda a: a.name.lower())

    def launch(self, desktop_id: str) -> tuple[bool, str]:
        if not self.allow_launch:
            return False, "Application launching is disabled."
        app = self.apps.get(desktop_id)
        if not app or (self.allowlist and desktop_id not in self.allowlist):
            return False, "Application is not in the local allowlist."
        if not shutil.which("gtk-launch"):
            return False, "gtk-launch is not installed."
        try:
            subprocess.Popen(["gtk-launch", desktop_id.removesuffix(".desktop")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Launched {app.name}."
        except Exception as exc:
            return False, str(exc)

    def running(self) -> list[tuple[int, DesktopApp]]:
        username = psutil.Process().username()
        allowed = {a.exec_bin: a for a in self.allowed_apps() if a.exec_bin not in self.DENY_EXEC}
        rows: list[tuple[int, DesktopApp]] = []
        seen: set[tuple[int, str]] = set()
        for proc in psutil.process_iter(["pid", "name", "username", "exe"]):
            try:
                if proc.info.get("username") != username:
                    continue
                name = os.path.basename(proc.info.get("exe") or proc.info.get("name") or "")
                app = allowed.get(name)
                if not app:
                    continue
                key = (proc.pid, app.desktop_id)
                if key not in seen:
                    rows.append((proc.pid, app)); seen.add(key)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return rows

    def close(self, pid: int) -> tuple[bool, str]:
        if not self.allow_close:
            return False, "Application closing is disabled."
        running = {p: app for p, app in self.running()}
        app = running.get(pid)
        if not app:
            return False, "Process is not an allowed GUI application."
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return True, f"Close requested for {app.name}."
        except (psutil.NoSuchProcess, psutil.AccessDenied) as exc:
            return False, str(exc)
