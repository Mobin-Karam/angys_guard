import os

from laptop_guard.exit_watchdog import _pid_alive


def test_current_pid_is_alive():
    assert _pid_alive(os.getpid()) is True


def test_invalid_pid_is_not_alive():
    assert _pid_alive(-1) is False
