from pathlib import Path

import laptop_guard.config as config
from laptop_guard.models import AppConfig


def test_setup_complete_checkpoint(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(config, "APP_DIR", tmp_path / "config")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(config, "CONFIG_PATH", tmp_path / "config" / "config.toml")
    monkeypatch.setattr(config, "SECRETS_PATH", tmp_path / "config" / "secrets.json")
    monkeypatch.setattr(config, "MEDIA_DIR", tmp_path / "data" / "media")

    cfg = AppConfig()
    cfg.bot.provider = "bale"
    cfg.bot.api_base = "https://tapi.bale.ai"
    cfg.bot.chat_id = 42
    config.save_config(cfg)

    loaded = config.load_config()
    assert loaded.bot.provider == "bale"
    assert loaded.bot.chat_id == 42
    assert loaded.setup_complete is False
    assert config.setup_is_complete() is False

    loaded.setup_complete = True
    config.save_config(loaded)
    assert config.setup_is_complete() is True
