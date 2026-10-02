"""Regression coverage for intentional local Guard shutdown."""

from __future__ import annotations

import threading
from types import SimpleNamespace

from laptop_guard.guard import LaptopGuard


def test_disarmed_service_stop_does_not_schedule_an_exit_lock() -> None:
    guard = LaptopGuard.__new__(LaptopGuard)
    guard._authorized_exit = False
    guard._exit_lock_requested = False
    guard.config = SimpleNamespace(security=SimpleNamespace(lock_on_guard_exit=True))
    guard.state_lock = threading.RLock()
    guard.state = SimpleNamespace(active=lambda: False)
    events: list[tuple[object, ...]] = []
    guard.events = SimpleNamespace(add=lambda *args: events.append(args))

    guard._request_exit_lock("intentional local service stop")

    assert guard._exit_lock_requested is False
    assert events == []
