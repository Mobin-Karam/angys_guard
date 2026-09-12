from pathlib import Path

from laptop_guard.models import AppConfig, AudioConfig, CameraConfig, SecurityConfig
from laptop_guard.privacy_light import CameraPrivacyLight
from laptop_guard.warning import WarningScreenManager


def test_v33_safe_defaults():
    cfg = AppConfig()
    assert cfg.security.input_action == "warning_lock"
    assert cfg.security.lock_on_input is False
    assert cfg.security.input_snapshot is True
    assert cfg.security.warning_seconds == 5
    assert cfg.security.lock_after_countdown is True
    assert cfg.security.input_screen_snapshot is True
    assert cfg.audio.play_remote_voice is True
    assert cfg.camera.enabled is True


def test_privacy_light_status_is_non_throwing():
    status = CameraPrivacyLight().status()
    assert isinstance(status.available, bool)
    assert isinstance(status.writable, bool)


def test_warning_manager_initially_not_visible():
    manager = WarningScreenManager()
    assert manager.visible is False
