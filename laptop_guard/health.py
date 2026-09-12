from __future__ import annotations

import shutil
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

try:
    import psutil
except Exception:  # pragma: no cover - optional runtime degradation
    psutil = None

from .config import DATA_DIR
from .models import HealthConfig


@dataclass
class HealthSnapshot:
    cpu_percent: float | None = None
    memory_percent: float | None = None
    disk_free_gb: float | None = None
    battery_percent: float | None = None
    power_plugged: bool | None = None
    temperature_c: float | None = None
    uptime_seconds: float | None = None


def _temperature() -> float | None:
    if psutil is None or not hasattr(psutil, "sensors_temperatures"):
        return None
    try:
        temps = psutil.sensors_temperatures() or {}
        values: list[float] = []
        for entries in temps.values():
            for item in entries:
                current = getattr(item, "current", None)
                if isinstance(current, (int, float)) and -20 < current < 150:
                    values.append(float(current))
        return max(values) if values else None
    except Exception:
        return None


def collect_health() -> HealthSnapshot:
    usage = shutil.disk_usage(DATA_DIR if DATA_DIR.exists() else Path.home())
    if psutil is None:
        return HealthSnapshot(disk_free_gb=usage.free / (1024 ** 3))
    try:
        battery = psutil.sensors_battery()
    except Exception:
        battery = None
    try:
        boot = psutil.boot_time()
    except Exception:
        boot = None
    return HealthSnapshot(
        cpu_percent=float(psutil.cpu_percent(interval=None)),
        memory_percent=float(psutil.virtual_memory().percent),
        disk_free_gb=usage.free / (1024 ** 3),
        battery_percent=float(battery.percent) if battery else None,
        power_plugged=bool(battery.power_plugged) if battery else None,
        temperature_c=_temperature(),
        uptime_seconds=max(0.0, time.time() - boot) if boot else None,
    )


class HealthMonitor:
    def __init__(
        self,
        config: HealthConfig,
        callback: Callable[[str, str, str], None],
    ) -> None:
        self.config = config
        self.callback = callback
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.last: HealthSnapshot | None = None
        self._flags: dict[str, bool] = {}

    @property
    def available(self) -> bool:
        return psutil is not None

    def start(self) -> None:
        if not self.config.enabled or self.thread:
            return
        self.thread = threading.Thread(target=self._worker, daemon=True, name="health-monitor")
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

    def snapshot(self) -> HealthSnapshot:
        snap = collect_health()
        self.last = snap
        return snap

    def _set_flag(self, key: str, value: bool, severity: str, title: str, detail: str) -> None:
        previous = self._flags.get(key, False)
        self._flags[key] = value
        if value and not previous:
            self.callback(severity, title, detail)
        elif previous and not value and self.config.notify_changes:
            self.callback("info", f"{title} برطرف شد", detail)

    def _worker(self) -> None:
        previous_power: bool | None = None
        while not self.stop_event.is_set():
            snap = self.snapshot()
            if snap.battery_percent is not None:
                self._set_flag(
                    "battery_critical",
                    snap.battery_percent <= self.config.critical_battery_percent,
                    "critical",
                    "باتری بحرانی",
                    f"Battery: {snap.battery_percent:.0f}%",
                )
                self._set_flag(
                    "battery_low",
                    self.config.critical_battery_percent < snap.battery_percent <= self.config.low_battery_percent,
                    "warning",
                    "باتری کم",
                    f"Battery: {snap.battery_percent:.0f}%",
                )
            if snap.disk_free_gb is not None:
                self._set_flag(
                    "disk_low",
                    snap.disk_free_gb < self.config.min_free_disk_gb,
                    "warning",
                    "فضای ذخیره‌سازی کم",
                    f"Free disk: {snap.disk_free_gb:.1f} GB",
                )
            if snap.temperature_c is not None:
                self._set_flag(
                    "temp_high",
                    snap.temperature_c >= self.config.temperature_warn_c,
                    "warning",
                    "دمای سیستم بالا",
                    f"Temperature: {snap.temperature_c:.1f}°C",
                )
            if previous_power is not None and snap.power_plugged is not None and snap.power_plugged != previous_power:
                self.callback(
                    "notice",
                    "برق متصل شد" if snap.power_plugged else "شارژر جدا شد",
                    f"Battery: {snap.battery_percent:.0f}%" if snap.battery_percent is not None else "",
                )
            if snap.power_plugged is not None:
                previous_power = snap.power_plugged
            self.stop_event.wait(max(10, int(self.config.interval_seconds)))
