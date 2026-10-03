import json
import os
import time

import laptop_guard.exit_watchdog as watchdog
from laptop_guard.exit_watchdog import _pid_alive


def test_current_pid_is_alive():
    assert _pid_alive(os.getpid()) is True


def test_invalid_pid_is_not_alive():
    assert _pid_alive(-1) is False


def test_inactive_startup_exit_does_not_lock(monkeypatch, tmp_path):
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps({"armed": False}), encoding="utf-8")
    locks: list[bool] = []
    monkeypatch.setattr(watchdog, "_pid_alive", lambda _pid: False)
    monkeypatch.setattr(watchdog.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(watchdog, "lock_screen", lambda: locks.append(True))

    assert watchdog.watch(999999, state_path=str(state_path)) == 0
    assert locks == []


def test_active_guard_exit_still_locks(monkeypatch, tmp_path):
    state_path = tmp_path / "state.json"
    state_path.write_text(
        json.dumps({"armed": True, "arm_ready_at": time.time() - 1, "grace_until": 0}),
        encoding="utf-8",
    )
    locks: list[bool] = []
    monkeypatch.setattr(watchdog, "_pid_alive", lambda _pid: False)
    monkeypatch.setattr(watchdog.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(watchdog, "lock_screen", lambda: locks.append(True))

    assert watchdog.watch(999999, state_path=str(state_path)) == 0
    assert locks == [True]
