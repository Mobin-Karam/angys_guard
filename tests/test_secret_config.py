from __future__ import annotations

import stat
from pathlib import Path

import pytest

import laptop_guard.config as config
from laptop_guard.models import AppConfig


def _redirect_paths(monkeypatch, tmp_path: Path) -> None:
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"
    monkeypatch.setattr(config, "APP_DIR", config_dir)
    monkeypatch.setattr(config, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(config, "DATA_DIR", data_dir)
    monkeypatch.setattr(config, "CONFIG_PATH", config_dir / "config.toml")
    monkeypatch.setattr(config, "SECRETS_PATH", config_dir / "secrets.json")
    monkeypatch.setattr(config, "MEDIA_DIR", data_dir / "media")
    monkeypatch.setattr(config, "LOG_DIR", data_dir / "logs")


def test_tokens_are_private_and_separate_from_config(tmp_path: Path, monkeypatch) -> None:
    _redirect_paths(monkeypatch, tmp_path)
    config.set_bot_token("test-only-bot-token")
    config.set_api_token("test-only-api-token")
    config.save_config(AppConfig(setup_complete=True))

    assert stat.S_IMODE(config.SECRETS_PATH.stat().st_mode) == 0o600
    assert stat.S_IMODE(config.CONFIG_PATH.stat().st_mode) == 0o600
    public_config = config.CONFIG_PATH.read_text(encoding="utf-8")
    assert "test-only-bot-token" not in public_config
    assert "test-only-api-token" not in public_config
    assert config.get_bot_token() == "test-only-bot-token"
    assert config.get_api_token() == "test-only-api-token"


def test_legacy_secret_import_is_optional_without_environment(
    tmp_path: Path, monkeypatch
) -> None:
    _redirect_paths(monkeypatch, tmp_path)
    monkeypatch.delenv("BALE_BOT_TOKEN", raising=False)

    assert config.import_legacy_env_secrets() is False
    assert not config.SECRETS_PATH.exists()
    assert config.load_config() == AppConfig()


def test_private_write_preserves_destination_on_replace_failure(
    tmp_path: Path, monkeypatch
) -> None:
    destination = tmp_path / "secrets.json"
    destination.write_text("old content", encoding="utf-8")
    destination.chmod(0o644)
    real_mkstemp = config.tempfile.mkstemp

    def checked_mkstemp(*args, **kwargs):
        fd, name = real_mkstemp(*args, **kwargs)
        assert stat.S_IMODE(Path(name).stat().st_mode) == 0o600
        return fd, name

    monkeypatch.setattr(config.tempfile, "mkstemp", checked_mkstemp)
    monkeypatch.setattr(config.os, "replace", lambda *_args: (_ for _ in ()).throw(OSError()))

    with pytest.raises(OSError):
        config._atomic_write_private(destination, "new content")

    assert destination.read_text(encoding="utf-8") == "old content"
    assert list(tmp_path.glob(".secrets.json-*")) == []


def test_private_write_normalizes_existing_permissions(tmp_path: Path) -> None:
    destination = tmp_path / "config.toml"
    destination.write_text("old", encoding="utf-8")
    destination.chmod(0o644)

    config._atomic_write_private(destination, "new")

    assert destination.read_text(encoding="utf-8") == "new"
    assert stat.S_IMODE(destination.stat().st_mode) == 0o600
