"""Boot-time auto-arm waits for provider control and a local grace period."""

from __future__ import annotations

import threading
import time
from types import SimpleNamespace

from laptop_guard.guard import LaptopGuard


def _guard() -> tuple[LaptopGuard, list[dict[str, object]], list[str]]:
    guard = LaptopGuard.__new__(LaptopGuard)
    changes: list[dict[str, object]] = []
    notices: list[str] = []
    guard.config = SimpleNamespace(
        security=SimpleNamespace(auto_arm=True, arm_delay=3.0),
        startup=SimpleNamespace(auto_arm_grace_seconds=90),
    )
    guard.state_lock = threading.RLock()
    guard.state = SimpleNamespace(mutate=lambda **kwargs: changes.append(kwargs))
    guard.mouse_anchor = object()
    guard.events = SimpleNamespace(add=lambda *_args: None)
    guard._send_async = lambda text, *_args: notices.append(text)
    guard._startup_auto_arm_pending = False
    return guard, changes, notices


def test_auto_arm_is_deferred_and_clears_stale_boot_state():
    guard, changes, _notices = _guard()

    guard._defer_startup_auto_arm()

    assert guard._startup_auto_arm_pending is True
    assert changes == [{"armed": False, "grace_until": 0.0, "arm_ready_at": 0.0}]


def test_auto_arm_activates_only_after_provider_readiness_with_grace():
    guard, changes, notices = _guard()
    guard._defer_startup_auto_arm()
    before = time.time()

    guard._complete_startup_auto_arm()

    assert guard._startup_auto_arm_pending is False
    assert changes[-1]["armed"] is True
    assert changes[-1]["arm_ready_at"] >= before + 89
    assert notices and "/disarm" in notices[0]
