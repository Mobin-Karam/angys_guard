from __future__ import annotations

import json
import re
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Any

from .base import FeatureHost
from .manager import FeatureManager

_AUTH_SOURCES = {
    "gdm-password", "gdm3", "login", "lightdm", "sddm-helper", "sshd",
    "systemd-logind",
}
_FAILURE_PATTERNS = (
    re.compile(r"authentication failure", re.I),
    re.compile(r"failed password", re.I),
    re.compile(r"failed login", re.I),
    re.compile(r"authentication failed", re.I),
    re.compile(r"maximum authentication attempts", re.I),
)
_USER_PATTERNS = (
    re.compile(r"\buser(?:name)?[= ]+([A-Za-z0-9_.@-]{1,64})", re.I),
    re.compile(r"failed password for (?:invalid user )?([A-Za-z0-9_.@-]{1,64})", re.I),
)
_ADDRESS_PATTERN = re.compile(r"\bfrom ([0-9a-f:.]{3,64})\b", re.I)


@dataclass(frozen=True)
class FailedLoginEvent:
    source: str
    username: str = "unknown"
    address: str = ""


def parse_failed_login(record: dict[str, Any]) -> FailedLoginEvent | None:
    message = str(record.get("MESSAGE") or "")
    source = str(
        record.get("SYSLOG_IDENTIFIER")
        or record.get("_COMM")
        or record.get("_SYSTEMD_UNIT")
        or ""
    ).strip().lower()
    source = source.removesuffix(".service")
    if source not in _AUTH_SOURCES and not any(name in source for name in _AUTH_SOURCES):
        return None
    if not any(pattern.search(message) for pattern in _FAILURE_PATTERNS):
        return None
    username = "unknown"
    for pattern in _USER_PATTERNS:
        match = pattern.search(message)
        if match:
            username = match.group(1)
            break
    address_match = _ADDRESS_PATTERN.search(message)
    return FailedLoginEvent(source=source, username=username, address=address_match.group(1) if address_match else "")


class FailedLoginFeature:
    """Streams readable systemd journal authentication failures to the owner."""

    name = "failed-login"

    def __init__(self, host: FeatureHost, enabled: bool = True) -> None:
        self.host = host
        self.enabled = enabled
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._process: subprocess.Popen | None = None
        self._last_key = ""
        self._last_at = 0.0

    def register(self, manager: FeatureManager) -> None:
        return None

    @property
    def available(self) -> bool:
        return shutil.which("journalctl") is not None

    def start(self) -> None:
        if not self.enabled or not self.available or self._thread is not None:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="failed-login-monitor")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        process = self._process
        if process is not None and process.poll() is None:
            process.terminate()
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=1.5)
        self._process = None
        self._thread = None

    def _run(self) -> None:
        try:
            self._process = subprocess.Popen(
                ["journalctl", "--follow", "--lines=0", "--output=json", "--no-pager"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
            if self._process.stdout is None:
                return
            for line in self._process.stdout:
                if self._stop.is_set():
                    break
                try:
                    record = json.loads(line)
                except (TypeError, ValueError):
                    continue
                event = parse_failed_login(record)
                if event is not None:
                    self._notify(event)
        except OSError as exc:
            self.host.feature_event("failed_login_monitor", f"journal unavailable: {exc}", "warning")
        finally:
            self._process = None

    def _notify(self, event: FailedLoginEvent) -> None:
        key = f"{event.source}|{event.username}|{event.address}"
        now = time.monotonic()
        if key == self._last_key and now - self._last_at < 10:
            return
        self._last_key = key
        self._last_at = now
        detail = f"source={event.source}; user={event.username}"
        if event.address:
            detail += f"; address={event.address}"
        self.host.feature_event("failed_login", detail, "critical")
        message = (
            "🚨 تلاش ورود ناموفق به لپ‌تاپ شناسایی شد\n\n"
            f"Source: {event.source}\nUser: {event.username}"
        )
        if event.address:
            message += f"\nAddress: {event.address}"
        self.host.feature_notify_owner(message)
