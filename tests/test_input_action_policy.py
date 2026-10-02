"""Input-response policy must match the setting shown in setup."""

from __future__ import annotations

import threading
from types import SimpleNamespace

import laptop_guard.guard as guard_module
from laptop_guard.guard import LaptopGuard


def _guard_for(action: str) -> tuple[LaptopGuard, list[str]]:
    guard = LaptopGuard.__new__(LaptopGuard)
    guard.config = SimpleNamespace(
        security=SimpleNamespace(
            input_action=action,
            input_cooldown=0,
            warning_seconds=5,
            warning_video=True,
            lock_after_warning=action == "warning_lock",
            camera_snapshot_on_input=False,
            screen_snapshot_on_input=False,
        )
    )
    guard.state_lock = threading.RLock()
    guard.state = SimpleNamespace(active=lambda: True, last_input_alert=0.0, last_input_kind="")
    guard.events = SimpleNamespace(add=lambda *_args: None)
    guard.stop_event = threading.Event()
    guard._lock_generation = 0
    guard.warning_proc = None
    notifications: list[str] = []
    guard.feature_notify_owner = lambda text, *_args, **_kwargs: notifications.append(text)
    guard._capture_input_evidence = lambda _stamp: None
    guard._send_async = lambda _text: None
    guard.lock_screen = lambda: True
    return guard, notifications


def test_notify_input_action_does_not_launch_a_warning_or_lock(monkeypatch) -> None:
    guard, notifications = _guard_for("notify")
    launched: list[int] = []
    monkeypatch.setattr(guard_module, "launch_warning", lambda seconds: launched.append(seconds))

    guard.trigger_input_alert("mouse movement")

    assert launched == []
    assert notifications and "خودکار قفل نخواهد شد" in notifications[0]


def test_warning_input_action_does_not_lock_after_the_visible_warning(monkeypatch) -> None:
    guard, notifications = _guard_for("warning")
    launched: list[int] = []
    monkeypatch.setattr(guard_module, "launch_warning", lambda seconds: launched.append(seconds))

    guard.trigger_input_alert("keyboard")

    assert launched == [5]
    assert notifications and "خودکار قفل نخواهد شد" in notifications[0]


def test_warning_lock_input_action_keeps_the_explicit_lock_message(monkeypatch) -> None:
    guard, notifications = _guard_for("warning_lock")
    monkeypatch.setattr(guard_module, "launch_warning", lambda _seconds: None)

    guard.trigger_input_alert("keyboard")

    assert notifications and "سپس سیستم قفل خواهد شد" in notifications[0]
