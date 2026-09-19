from __future__ import annotations

import json
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
    monkeypatch.setattr(config, "SETUP_PROGRESS_PATH", config_dir / "setup-progress.json")
    monkeypatch.setattr(config, "MEDIA_DIR", data_dir / "media")
    monkeypatch.setattr(config, "LOG_DIR", data_dir / "logs")


def _write_legacy_secret(token: str) -> None:
    config.ensure_dirs()
    config._write_secrets({"bot_token": token})


def test_provider_tokens_are_private_scoped_and_separate_from_config(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _redirect_paths(monkeypatch, tmp_path)
    telegram = "test-only-telegram-token"
    bale = "test-only-bale-token"

    config.set_bot_token(telegram, "telegram")
    config.set_bot_token(bale, "bale")
    config.set_api_token("test-only-api-token")
    config.save_config(AppConfig(setup_complete=False))

    assert stat.S_IMODE(config.SECRETS_PATH.stat().st_mode) == 0o600
    assert stat.S_IMODE(config.CONFIG_PATH.stat().st_mode) == 0o600

    public_config = config.CONFIG_PATH.read_text(encoding="utf-8")
    assert telegram not in public_config
    assert bale not in public_config
    assert "test-only-api-token" not in public_config

    data = json.loads(config.SECRETS_PATH.read_text(encoding="utf-8"))
    assert data["telegram_bot_token"] == telegram
    assert data["bale_bot_token"] == bale
    assert "bot_token" not in data

    assert config.get_bot_token("telegram") == telegram
    assert config.get_bot_token("bale") == bale
    assert config.get_api_token() == "test-only-api-token"


def test_updating_telegram_token_preserves_bale_token(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _redirect_paths(monkeypatch, tmp_path)
    config.set_bot_token("telegram-v1", "telegram")
    config.set_bot_token("bale-v1", "bale")

    config.set_bot_token("telegram-v2", "telegram")

    assert config.get_bot_token("telegram") == "telegram-v2"
    assert config.get_bot_token("bale") == "bale-v1"


@pytest.mark.parametrize("provider", ["telegram", "bale"])
def test_completed_legacy_setup_migrates_shared_token_to_known_provider(
    provider: str,
    tmp_path: Path,
    monkeypatch,
) -> None:
    _redirect_paths(monkeypatch, tmp_path)
    legacy = f"test-only-{provider}-legacy-token"
    _write_legacy_secret(legacy)

    cfg = AppConfig(setup_complete=True)
    cfg.bot.provider = provider
    config.save_config(cfg)

    loaded = config.load_config()

    assert loaded.bot.provider == provider
    assert config.get_bot_token(provider) == legacy
    other = "bale" if provider == "telegram" else "telegram"
    assert config.get_bot_token(other) == ""

    data = json.loads(config.SECRETS_PATH.read_text(encoding="utf-8"))
    assert data[f"{provider}_bot_token"] == legacy
    assert "bot_token" not in data
    assert "legacy_bot_token" not in data


def test_pending_legacy_setup_does_not_guess_provider(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _redirect_paths(monkeypatch, tmp_path)
    legacy = "test-only-ambiguous-legacy-token"
    _write_legacy_secret(legacy)

    cfg = AppConfig(setup_complete=False)
    cfg.bot.provider = "telegram"
    config.save_config(cfg)
    config.save_setup_progress({"identity", "owner"})

    loaded = config.load_config()

    assert loaded.setup_complete is False
    assert config.get_bot_token("telegram") == ""
    assert config.get_bot_token("bale") == ""
    assert config.get_legacy_bot_token() == legacy

    data = json.loads(config.SECRETS_PATH.read_text(encoding="utf-8"))
    assert data["legacy_bot_token"] == legacy
    assert "bot_token" not in data


def test_legacy_secret_import_is_bale_scoped(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _redirect_paths(monkeypatch, tmp_path)
    monkeypatch.setenv("BALE_BOT_TOKEN", "test-only-env-bale-token")

    assert config.import_legacy_env_secrets() is True
    assert config.get_bot_token("bale") == "test-only-env-bale-token"
    assert config.get_bot_token("telegram") == ""


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
    monkeypatch.setattr(
        config.os,
        "replace",
        lambda *_args: (_ for _ in ()).throw(OSError()),
    )

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
