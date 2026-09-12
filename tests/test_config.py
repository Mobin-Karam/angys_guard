from laptop_guard.config import AppConfig


def test_default_warning_sequence_is_five_seconds(monkeypatch):
    monkeypatch.delenv("WARNING_SECONDS", raising=False)
    monkeypatch.delenv("WARNING_VIDEO", raising=False)
    cfg = AppConfig()
    assert cfg.security.warning_seconds == 5
    assert cfg.security.lock_after_warning is True
    assert cfg.security.warning_video is True


def test_protected_stop_defaults(monkeypatch):
    for name in (
        "STOP_AUTH_ENABLED",
        "STOP_PIN_TIMEOUT",
        "STOP_OWNER_CONFIRM_TIMEOUT",
        "LOCK_ON_STOP_AUTH_FAILURE",
    ):
        monkeypatch.delenv(name, raising=False)
    cfg = AppConfig()
    assert cfg.security.stop_auth_enabled is True
    assert cfg.security.stop_pin_timeout == 15
    assert cfg.security.stop_owner_confirm_timeout == 10
    assert cfg.security.lock_on_stop_auth_failure is True
