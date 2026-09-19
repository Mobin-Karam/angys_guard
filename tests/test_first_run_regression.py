from __future__ import annotations

import stat
from pathlib import Path
from types import SimpleNamespace

from laptop_guard import config
from laptop_guard import service
from laptop_guard import setup_wizard
from laptop_guard.models import AppConfig


FAKE_BOT_TOKEN = "test-only-provider-token-not-real"


def _redirect_config_paths(monkeypatch, tmp_path: Path) -> None:
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
    monkeypatch.setattr(config, "STATE_PATH", data_dir / "state.json")
    monkeypatch.setattr(config, "EVENT_DB_PATH", data_dir / "events.sqlite3")
    monkeypatch.setattr(setup_wizard, "CONFIG_PATH", config.CONFIG_PATH)


class _QuietConsole:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def print(self, *parts, **_kwargs) -> None:
        self.lines.append(" ".join(str(part) for part in parts))

    def rule(self, *parts, **_kwargs) -> None:
        self.print(*parts)


def test_first_run_local_setup_completes_with_private_persistence(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _redirect_config_paths(monkeypatch, tmp_path)
    console = _QuietConsole()
    autostart_calls: list[tuple[bool, bool]] = []

    def prompt_ask(prompt: str, **kwargs):
        if prompt == "Notification provider":
            return "local"
        return kwargs.get("default", "")

    monkeypatch.setattr(setup_wizard.Prompt, "ask", prompt_ask)
    monkeypatch.setattr(
        setup_wizard.Confirm,
        "ask",
        lambda _prompt, **kwargs: bool(kwargs.get("default", False)),
    )
    monkeypatch.setattr(
        setup_wizard.IntPrompt,
        "ask",
        lambda _prompt, **kwargs: int(kwargs.get("default", 0)),
    )
    monkeypatch.setattr(
        setup_wizard,
        "discover_cameras",
        lambda: [SimpleNamespace(index=7, label="Mock Camera 7")],
    )
    monkeypatch.setattr(
        setup_wizard,
        "detect_audio_sources",
        lambda: ["mock-microphone"],
    )
    monkeypatch.setattr(setup_wizard.shutil, "which", lambda _name: None)
    monkeypatch.setattr(
        setup_wizard,
        "_validate_section",
        lambda _cfg, _section: (True, "mock readiness ok"),
    )
    monkeypatch.setattr(
        service,
        "set_autostart",
        lambda enabled, start_now=True: autostart_calls.append(
            (bool(enabled), bool(start_now))
        )
        or True,
    )

    result = setup_wizard.run_setup(console=console)

    assert result.setup_complete is True
    assert result.bot.provider == "local"
    assert result.bot.chat_id is None
    assert result.camera.index == 7
    assert result.audio.input == "mock-microphone"
    assert autostart_calls == [(False, False)]

    persisted = config.load_config()
    assert persisted.setup_complete is True
    assert persisted.bot.provider == "local"
    assert persisted.camera.index == 7
    assert persisted.audio.input == "mock-microphone"
    assert config.load_setup_progress() == set(setup_wizard.SECTION_KEYS)

    assert stat.S_IMODE(config.APP_DIR.stat().st_mode) == 0o700
    assert stat.S_IMODE(config.CONFIG_PATH.stat().st_mode) == 0o600
    assert stat.S_IMODE(config.SETUP_PROGRESS_PATH.stat().st_mode) == 0o600
    assert not config.SECRETS_PATH.exists()


def test_provider_setup_uses_fake_validation_without_network_or_token_output(
    monkeypatch,
) -> None:
    cfg = AppConfig()
    console = _QuietConsole()
    saved_tokens: list[str] = []
    validated_tokens: list[str] = []

    def prompt_ask(prompt: str, **kwargs):
        if prompt == "Notification provider":
            return "bale"
        return kwargs.get("default", "")

    monkeypatch.setattr(setup_wizard.Prompt, "ask", prompt_ask)
    monkeypatch.setattr(setup_wizard, "get_bot_token", lambda: "")
    monkeypatch.setattr(setup_wizard.getpass, "getpass", lambda _prompt: FAKE_BOT_TOKEN)
    monkeypatch.setattr(
        setup_wizard,
        "_check_provider_token",
        lambda _cfg, token: validated_tokens.append(token) or (True, "mock provider ok"),
    )
    monkeypatch.setattr(setup_wizard, "set_bot_token", saved_tokens.append)
    monkeypatch.setattr(setup_wizard, "save_config", lambda _cfg: None)

    setup_wizard._configure_provider(cfg, console)

    assert cfg.bot.provider == "bale"
    assert validated_tokens == [FAKE_BOT_TOKEN]
    assert saved_tokens == [FAKE_BOT_TOKEN]
    assert FAKE_BOT_TOKEN not in "\n".join(console.lines)


def test_owner_pairing_ignores_stale_start_and_accepts_new_mock_update() -> None:
    console = _QuietConsole()

    class FakeBot:
        def __init__(self) -> None:
            self.calls: list[int | None] = []

        def get_updates(self, offset=None, timeout=0):
            self.calls.append(offset)
            if len(self.calls) == 1:
                return [
                    {
                        "update_id": 10,
                        "message": {
                            "text": "/start",
                            "chat": {"id": 111},
                        },
                    }
                ]
            return [
                {
                    "update_id": 11,
                    "message": {
                        "text": "/start",
                        "chat": {"id": 222},
                    },
                }
            ]

    bot = FakeBot()
    chat_id = setup_wizard.pair_chat(bot, console, timeout_seconds=1)

    assert chat_id == 222
    assert bot.calls == [None, 11]
