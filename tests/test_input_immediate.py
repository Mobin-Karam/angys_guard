from types import SimpleNamespace

import laptop_guard.input_monitor as input_module
from laptop_guard.input_monitor import InputMonitor


def test_first_pynput_mouse_movement_triggers_immediately():
    events = []
    monitor = InputMonitor(12, events.append, backend="pynput")

    monitor._move(100, 200)

    assert events == ["mouse movement"]


def test_single_nonzero_evdev_relative_event_triggers(monkeypatch):
    fake_codes = SimpleNamespace(
        EV_REL=2,
        EV_KEY=1,
        REL_X=0,
        REL_Y=1,
        REL_WHEEL=8,
        REL_HWHEEL=6,
        bytype={},
    )
    monkeypatch.setattr(input_module, "ecodes", fake_codes)
    events = []
    monitor = InputMonitor(12, events.append, backend="evdev")

    monitor._classify_evdev(SimpleNamespace(type=2, code=0, value=1))

    assert events == ["mouse movement"]
