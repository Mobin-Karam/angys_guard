from types import SimpleNamespace

import laptop_guard.guard as guard_module
from laptop_guard.guard import LaptopGuard
from laptop_guard.models import AppConfig


def test_quiet_hours_suppresses_warning_but_never_high_or_critical(monkeypatch):
    guard = LaptopGuard.__new__(LaptopGuard)
    guard.config = AppConfig()
    guard.config.alerts.quiet_hours_enabled = True
    guard.config.alerts.quiet_start_hour = 0
    guard.config.alerts.quiet_end_hour = 23
    monkeypatch.setattr(guard_module, "datetime", SimpleNamespace(now=lambda: SimpleNamespace(hour=12)))

    assert not guard._notification_allowed("warning", "input")
    assert guard._notification_allowed("high", "input")
    assert guard._notification_allowed("critical", "failed_login")


def test_alert_kind_and_severity_preferences_apply_before_delivery():
    guard = LaptopGuard.__new__(LaptopGuard)
    guard.config = AppConfig()
    guard.config.alerts.input_enabled = False
    guard.config.alerts.minimum_severity = "high"

    assert not guard._notification_allowed("high", "input")
    assert not guard._notification_allowed("warning", "motion")
    assert guard._notification_allowed("critical", "failed_login")


def test_alert_menu_exposes_owner_controls():
    guard = LaptopGuard.__new__(LaptopGuard)
    guard.config = AppConfig()

    text, markup = guard.alerts_menu()

    assert "Quiet hours" in text
    callbacks = str(markup)
    assert "alerts:quiet" in callbacks
    assert "alerts:minimum" in callbacks
    assert "alerts:toggle:input" in callbacks
