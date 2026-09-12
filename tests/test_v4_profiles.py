from laptop_guard.models import AppConfig
from laptop_guard.profiles import apply_profile


def test_away_profile_uses_visible_countdown_lock():
    cfg = AppConfig()
    apply_profile(cfg, "away")
    assert cfg.profile == "away"
    assert cfg.camera.enabled is True
    assert cfg.security.input_action == "warning_lock"
    assert cfg.security.lock_on_input is False
    assert cfg.camera.tamper_enabled is True


def test_testing_profile_reduces_noise():
    cfg = AppConfig()
    apply_profile(cfg, "testing")
    assert cfg.profile == "testing"
    assert cfg.security.input_action == "notify"
    assert cfg.camera.event_clip_seconds == 0
    assert cfg.monitors.usb_events is False
