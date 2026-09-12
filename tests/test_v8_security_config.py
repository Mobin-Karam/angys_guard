from laptop_guard.config import AppConfig


def test_exit_lock_is_enabled_by_default(monkeypatch):
    monkeypatch.delenv("LOCK_ON_GUARD_EXIT", raising=False)
    cfg = AppConfig()
    assert cfg.security.lock_on_guard_exit is True


def test_remote_unlock_is_opt_in(monkeypatch):
    monkeypatch.delenv("ALLOW_REMOTE_UNLOCK", raising=False)
    cfg = AppConfig()
    assert cfg.security.allow_remote_unlock is False


def test_chat_direction_defaults_to_auto(monkeypatch):
    monkeypatch.delenv("CHAT_DIRECTION", raising=False)
    cfg = AppConfig()
    assert cfg.chat.direction == "auto"


def test_remote_power_is_opt_in(monkeypatch):
    monkeypatch.delenv("ALLOW_REMOTE_POWER", raising=False)
    cfg = AppConfig()
    assert cfg.security.allow_remote_power is False
