from __future__ import annotations

import stat
from types import SimpleNamespace

from laptop_guard import cli
from laptop_guard import config
from laptop_guard import setup_wizard
from laptop_guard.models import AppConfig


def _fake_handlers(called):
    return {
        key: (lambda _cfg, _console, key=key: called.append(key))
        for key in setup_wizard.SECTION_KEYS
    }


def test_interrupted_setup_resumes_from_first_incomplete(monkeypatch):
    cfg = AppConfig(setup_complete=False)
    called = []
    saved_progress = []

    monkeypatch.setattr(setup_wizard, "load_config", lambda: cfg)
    monkeypatch.setattr(setup_wizard, "CONFIG_PATH", SimpleNamespace(exists=lambda: True))
    monkeypatch.setattr(
        setup_wizard,
        "load_setup_progress",
        lambda: {"identity", "provider"},
    )
    monkeypatch.setattr(setup_wizard, "save_config", lambda _cfg: None)
    monkeypatch.setattr(
        setup_wizard,
        "save_setup_progress",
        lambda completed: saved_progress.append(set(completed)),
    )
    monkeypatch.setattr(
        setup_wizard,
        "_validate_section",
        lambda _cfg, _section: (True, "ok"),
    )
    monkeypatch.setattr(setup_wizard, "_resume_action", lambda: "resume")
    monkeypatch.setattr(setup_wizard, "SECTION_HANDLERS", _fake_handlers(called))

    result = setup_wizard.run_setup(console=SimpleNamespace(
        print=lambda *_a, **_k: None,
        rule=lambda *_a, **_k: None,
    ))

    assert called[0] == "owner"
    assert "identity" not in called
    assert "provider" not in called
    assert called == list(setup_wizard.SECTION_KEYS[2:])
    assert result.setup_complete is True
    assert saved_progress[-1] == set(setup_wizard.SECTION_KEYS)


def test_reconfigure_changes_only_requested_section(monkeypatch):
    cfg = AppConfig(setup_complete=True)
    called = []

    monkeypatch.setattr(setup_wizard, "load_config", lambda: cfg)
    monkeypatch.setattr(
        setup_wizard,
        "load_setup_progress",
        lambda: set(setup_wizard.SECTION_KEYS),
    )
    monkeypatch.setattr(setup_wizard, "save_config", lambda _cfg: None)
    monkeypatch.setattr(setup_wizard, "save_setup_progress", lambda _completed: None)
    monkeypatch.setattr(
        setup_wizard,
        "_validate_section",
        lambda _cfg, _section: (True, "ok"),
    )
    monkeypatch.setattr(setup_wizard, "SECTION_HANDLERS", _fake_handlers(called))

    result = setup_wizard.run_reconfigure(
        "audio",
        console=SimpleNamespace(
            print=lambda *_a, **_k: None,
            rule=lambda *_a, **_k: None,
        ),
    )

    assert called == ["audio"]
    assert result.setup_complete is True


def test_failed_saved_validation_returns_to_relevant_section(monkeypatch):
    cfg = AppConfig(setup_complete=False)
    completed = {"identity", "provider", "owner", "camera"}

    def validate(_cfg, section):
        if section == "provider":
            return False, "provider needs attention"
        return True, "ok"

    monkeypatch.setattr(setup_wizard, "_validate_section", validate)

    valid, issues = setup_wizard._validate_completed(cfg, completed)

    assert "provider" not in valid
    assert issues["provider"] == "provider needs attention"
    assert setup_wizard._first_incomplete(valid) == "provider"


def test_valid_stored_provider_token_is_reused_without_printing_it(monkeypatch, capsys):
    cfg = AppConfig()
    cfg.bot.provider = "bale"
    token = "test-only-secret-token"

    monkeypatch.setattr(setup_wizard, "get_bot_token", lambda: token)
    monkeypatch.setattr(
        setup_wizard,
        "_check_provider_token",
        lambda _cfg, candidate: (candidate == token, "ok"),
    )
    monkeypatch.setattr(
        setup_wizard.getpass,
        "getpass",
        lambda _prompt: (_ for _ in ()).throw(
            AssertionError("valid stored token should not be requested again")
        ),
    )

    console = setup_wizard.Console()
    assert setup_wizard._ensure_provider_token(cfg, console) == token
    assert token not in capsys.readouterr().out


def test_provider_change_invalidates_owner_pairing_checkpoint(monkeypatch):
    cfg = AppConfig(setup_complete=True)
    cfg.bot.provider = "bale"
    completed = set(setup_wizard.SECTION_KEYS)

    def provider_handler(current, _console):
        current.bot.provider = "telegram"

    handlers = dict(setup_wizard.SECTION_HANDLERS)
    handlers["provider"] = provider_handler

    monkeypatch.setattr(setup_wizard, "SECTION_HANDLERS", handlers)
    monkeypatch.setattr(setup_wizard, "save_config", lambda _cfg: None)
    monkeypatch.setattr(setup_wizard, "save_setup_progress", lambda _completed: None)
    monkeypatch.setattr(
        setup_wizard,
        "_validate_section",
        lambda _cfg, _section: (True, "ok"),
    )

    ok = setup_wizard._run_section(
        cfg,
        completed,
        "provider",
        SimpleNamespace(
            print=lambda *_a, **_k: None,
            rule=lambda *_a, **_k: None,
        ),
    )

    assert ok is True
    assert "provider" in completed
    assert "owner" not in completed
    assert cfg.setup_complete is False


def test_setup_progress_is_private_and_round_trips(tmp_path, monkeypatch):
    path = tmp_path / "setup-progress.json"
    monkeypatch.setattr(config, "SETUP_PROGRESS_PATH", path)
    monkeypatch.setattr(config, "APP_DIR", tmp_path)
    monkeypatch.setattr(config, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(config, "MEDIA_DIR", tmp_path / "data" / "media")
    monkeypatch.setattr(config, "LOG_DIR", tmp_path / "data" / "logs")

    config.save_setup_progress({"provider", "identity"})

    assert config.load_setup_progress() == {"identity", "provider"}
    assert stat.S_IMODE(path.stat().st_mode) == 0o600



def test_cli_accepts_targeted_reconfigure_section():
    args = cli.build_parser().parse_args(["reconfigure", "camera"])

    assert args.command == "reconfigure"
    assert args.section == "camera"
    assert args.func is cli.cmd_reconfigure



def test_stored_provider_token_is_preserved_on_network_failure(monkeypatch):
    cfg = AppConfig()
    cfg.bot.provider = "telegram"
    token = "test-only-existing-token"
    saved = []

    monkeypatch.setattr(setup_wizard, "get_bot_token", lambda: token)
    monkeypatch.setattr(
        setup_wizard,
        "_check_provider_token",
        lambda _cfg, candidate: (
            False,
            "Could not reach Telegram. The credential was not proven invalid.",
            "network",
        ),
    )
    monkeypatch.setattr(setup_wizard, "set_bot_token", saved.append)
    monkeypatch.setattr(
        setup_wizard.getpass,
        "getpass",
        lambda _prompt: (_ for _ in ()).throw(
            AssertionError("network failure must not request a replacement token")
        ),
    )

    console = setup_wizard.Console()
    try:
        setup_wizard._ensure_provider_token(cfg, console)
    except setup_wizard.SetupSectionDeferred:
        pass
    else:
        raise AssertionError("network failure should defer the provider section")

    assert saved == []


def test_new_provider_token_network_failure_does_not_loop(monkeypatch):
    cfg = AppConfig()
    cfg.bot.provider = "telegram"
    token = "test-only-candidate-token"
    prompts = []
    saved = []

    monkeypatch.setattr(setup_wizard, "get_bot_token", lambda: "")
    monkeypatch.setattr(
        setup_wizard.getpass,
        "getpass",
        lambda _prompt: prompts.append(_prompt) or token,
    )
    monkeypatch.setattr(
        setup_wizard,
        "_check_provider_token",
        lambda _cfg, candidate: (
            False,
            "Could not reach Telegram. The credential was not proven invalid.",
            "network",
        ),
    )
    monkeypatch.setattr(setup_wizard, "set_bot_token", saved.append)

    try:
        setup_wizard._ensure_provider_token(cfg, setup_wizard.Console())
    except setup_wizard.SetupSectionDeferred:
        pass
    else:
        raise AssertionError("network failure should pause instead of reprompting")

    assert len(prompts) == 1
    assert saved == []


def test_rejected_provider_token_prompts_again_and_saves_only_valid_token(monkeypatch):
    cfg = AppConfig()
    cfg.bot.provider = "telegram"
    rejected = "test-only-rejected-token"
    accepted = "test-only-accepted-token"
    entered = iter([rejected, accepted])
    saved = []

    monkeypatch.setattr(setup_wizard, "get_bot_token", lambda: "")
    monkeypatch.setattr(
        setup_wizard.getpass,
        "getpass",
        lambda _prompt: next(entered),
    )

    def check(_cfg, candidate):
        if candidate == rejected:
            return False, "Telegram rejected the bot credential.", "auth"
        return True, "Telegram bot connection is working.", "ok"

    monkeypatch.setattr(setup_wizard, "_check_provider_token", check)
    monkeypatch.setattr(setup_wizard, "set_bot_token", saved.append)

    result = setup_wizard._ensure_provider_token(cfg, setup_wizard.Console())

    assert result == accepted
    assert saved == [accepted]
