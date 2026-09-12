from pathlib import Path

import laptop_guard.config as config
from laptop_guard.models import AppConfig


def test_v4_config_sections_roundtrip(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(config, "APP_DIR", tmp_path / "config")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(config, "CONFIG_PATH", tmp_path / "config" / "config.toml")
    monkeypatch.setattr(config, "SECRETS_PATH", tmp_path / "config" / "secrets.json")
    monkeypatch.setattr(config, "MEDIA_DIR", tmp_path / "data" / "media")

    cfg = AppConfig(setup_complete=True, profile="night", device_name="Test Laptop")
    cfg.camera.pre_event_seconds = 7
    cfg.camera.tamper_enabled = True
    cfg.monitors.offline_queue = True
    cfg.health.low_battery_percent = 25
    config.save_config(cfg)

    loaded = config.load_config()
    assert loaded.profile == "night"
    assert loaded.device_name == "Test Laptop"
    assert loaded.camera.pre_event_seconds == 7
    assert loaded.camera.tamper_enabled is True
    assert loaded.monitors.offline_queue is True
    assert loaded.health.low_battery_percent == 25
