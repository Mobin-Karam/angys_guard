from __future__ import annotations

import threading
from typing import Callable

try:
    import pyudev
except Exception:  # pragma: no cover
    pyudev = None


class USBMonitor:
    def __init__(self, callback: Callable[[str, str], None]) -> None:
        self.callback = callback
        self.thread: threading.Thread | None = None
        self.stop_event = threading.Event()

    @property
    def available(self) -> bool:
        return pyudev is not None

    def start(self) -> bool:
        if pyudev is None or self.thread:
            return False
        self.thread = threading.Thread(target=self._worker, daemon=True, name="usb-monitor")
        self.thread.start()
        return True

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

    def _worker(self) -> None:
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem="usb")
        monitor.start()
        while not self.stop_event.is_set():
            device = monitor.poll(timeout=1)
            if device is None:
                continue
            action = str(getattr(device, "action", "change") or "change")
            vendor = str(device.get("ID_VENDOR_FROM_DATABASE") or device.get("ID_VENDOR") or "USB")
            model = str(device.get("ID_MODEL_FROM_DATABASE") or device.get("ID_MODEL") or "device")
            serial = str(device.get("ID_SERIAL_SHORT") or "")
            detail = f"{vendor} {model}".strip()
            if serial:
                detail += f" • {serial}"
            self.callback(action, detail)
