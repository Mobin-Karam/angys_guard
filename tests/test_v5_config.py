from pathlib import Path

import laptop_guard.config as config
from laptop_guard.models import AppConfig


def test_v5_config_roundtrip_lists_and_sections(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "APP_DIR", tmp_path / "cfg")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(config, "CONFIG_PATH", tmp_path / "cfg" / "config.toml")
    monkeypatch.setattr(config, "SECRETS_PATH", tmp_path / "cfg" / "secrets.json")
    monkeypatch.setattr(config, "MEDIA_DIR", tmp_path / "data" / "media")
    cfg = AppConfig(setup_complete=True)
    cfg.communication.surface = "both"
    cfg.screen.max_burst_seconds = 45
    cfg.apps.allowlist = ["firefox.desktop", "org.gnome.TextEditor.desktop"]
    cfg.api.enabled = True
    cfg.api.port = 9876
    config.save_config(cfg)
    loaded = config.load_config()
    assert loaded.communication.surface == "both"
    assert loaded.screen.max_burst_seconds == 45
    assert loaded.apps.allowlist == cfg.apps.allowlist
    assert loaded.api.enabled is True
    assert loaded.api.port == 9876
