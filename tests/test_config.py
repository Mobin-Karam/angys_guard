from laptop_guard.config import AppConfig


def test_default_warning_sequence_is_five_seconds(monkeypatch):
    monkeypatch.delenv('WARNING_SECONDS', raising=False)
    cfg = AppConfig()
    assert cfg.security.warning_seconds == 5
    assert cfg.security.lock_after_warning is True
    assert cfg.security.warning_images is True
