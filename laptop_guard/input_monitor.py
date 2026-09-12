from __future__ import annotations

import math
import select
import threading
import time
from typing import Callable

try:
    from pynput import keyboard, mouse
except Exception as exc:  # pragma: no cover - environment/backend dependent
    keyboard = None
    mouse = None
    _PYNPUT_ERROR = exc
else:
    _PYNPUT_ERROR = None

try:
    import evdev
    from evdev import ecodes
except Exception as exc:  # pragma: no cover - optional dependency/backend dependent
    evdev = None
    ecodes = None
    _EVDEV_ERROR = exc
else:
    _EVDEV_ERROR = None


class InputMonitor:
    """Detects input *activity*, never stores typed keys or button values.

    auto mode prefers evdev when readable input devices are available, which is
    more reliable under Wayland. If permissions prevent evdev access it falls
    back to pynput.
    """

    def __init__(self, threshold: float, callback: Callable[[str], None], backend: str = "auto") -> None:
        self.threshold = threshold
        self.callback = callback
        self.backend_preference = backend
        self.backend_name = "none"
        self.keyboard_listener = None
        self.mouse_listener = None
        self.anchor = None
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._ev_thread: threading.Thread | None = None
        self._ev_devices = []
        self._rel_accum = 0.0
        self._last_move_emit = 0.0

    def _readable_evdev_devices(self):
        if evdev is None:
            return []
        devices = []
        try:
            for path in evdev.list_devices():
                try:
                    dev = evdev.InputDevice(path)
                    caps = dev.capabilities()
                    if ecodes.EV_KEY in caps or ecodes.EV_REL in caps:
                        devices.append(dev)
                    else:
                        dev.close()
                except (PermissionError, OSError):
                    continue
        except Exception:
            return []
        return devices

    @property
    def available(self) -> bool:
        if self.backend_preference in {"auto", "evdev"}:
            devices = self._readable_evdev_devices()
            if devices:
                for dev in devices:
                    try: dev.close()
                    except Exception: pass
                return True
        return keyboard is not None and mouse is not None

    @property
    def availability_detail(self) -> str:
        ev = self._readable_evdev_devices() if self.backend_preference in {"auto", "evdev"} else []
        for d in ev:
            try: d.close()
            except Exception: pass
        if ev:
            return f"evdev available ({len(ev)} device(s)); key contents are discarded"
        if keyboard is not None and mouse is not None:
            return "pynput available"
        return f"evdev unavailable: {_EVDEV_ERROR}; pynput unavailable: {_PYNPUT_ERROR}"

    def start(self) -> None:
        if self.backend_preference in {"auto", "evdev"}:
            devices = self._readable_evdev_devices()
            if devices:
                self._ev_devices = devices
                self._stop.clear()
                self._ev_thread = threading.Thread(target=self._evdev_loop, daemon=True, name="evdev-activity")
                self._ev_thread.start()
                self.backend_name = "evdev"
                return
            if self.backend_preference == "evdev":
                raise RuntimeError("evdev selected, but no readable input devices were found. Add your user to the input group or choose auto/pynput.")
        if keyboard is None or mouse is None:
            raise RuntimeError(self.availability_detail)
        self.keyboard_listener = keyboard.Listener(on_press=lambda _: self.callback("keyboard"))
        self.mouse_listener = mouse.Listener(
            on_move=self._move,
            on_click=lambda x, y, button, pressed: self.callback("mouse click") if pressed else None,
            on_scroll=lambda x, y, dx, dy: self.callback("mouse scroll"),
        )
        self.keyboard_listener.start(); self.mouse_listener.start()
        self.backend_name = "pynput"

    def _evdev_loop(self) -> None:
        fds = {d.fd: d for d in self._ev_devices}
        while not self._stop.is_set() and fds:
            try:
                readable, _, _ = select.select(list(fds), [], [], 0.5)
            except Exception:
                break
            for fd in readable:
                dev = fds.get(fd)
                if dev is None:
                    continue
                try:
                    for event in dev.read():
                        self._classify_evdev(event)
                except OSError:
                    try: dev.close()
                    except Exception: pass
                    fds.pop(fd, None)
        for dev in list(fds.values()):
            try: dev.close()
            except Exception: pass

    def _classify_evdev(self, event) -> None:
        # Intentionally discard event.code for keyboard keys. This is activity
        # detection, not keylogging.
        if event.type == ecodes.EV_REL:
            if event.code in {ecodes.REL_WHEEL, getattr(ecodes, "REL_HWHEEL", -1)} and event.value:
                self.callback("mouse scroll"); return
            if event.code in {ecodes.REL_X, ecodes.REL_Y}:
                self._rel_accum += abs(float(event.value))
                now = time.monotonic()
                if self._rel_accum >= self.threshold and now - self._last_move_emit >= 0.25:
                    self._rel_accum = 0.0; self._last_move_emit = now; self.callback("mouse movement")
                return
        if event.type == ecodes.EV_KEY and event.value == 1:
            # BTN_* values are pointer/touchpad buttons. We inspect the symbolic
            # class only for routing, then immediately discard it; no key identity
            # is logged or retained.
            name = ecodes.bytype.get(ecodes.EV_KEY, {}).get(event.code, "")
            names = name if isinstance(name, (list, tuple)) else [name]
            if any(str(n).startswith("BTN_") for n in names):
                self.callback("mouse click")
            else:
                self.callback("keyboard")

    def stop(self) -> None:
        self._stop.set()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        for dev in self._ev_devices:
            try: dev.close()
            except Exception: pass
        self._ev_devices = []

    def reset_anchor(self) -> None:
        with self._lock:
            self.anchor = None

    def _move(self, x, y) -> None:
        with self._lock:
            if self.anchor is None:
                self.anchor = (x, y); return
            ax, ay = self.anchor
            if math.hypot(x - ax, y - ay) < self.threshold:
                return
            self.anchor = (x, y)
        self.callback("mouse movement")
