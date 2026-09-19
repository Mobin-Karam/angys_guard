from __future__ import annotations

import stat
from pathlib import Path
from types import SimpleNamespace

from laptop_guard import cli
from laptop_guard import doctor
from laptop_guard import guard
from laptop_guard import input_monitor
from laptop_guard import runtime_config
from laptop_guard import runtime_recovery
from laptop_guard import tests_manual
from laptop_guard.models import AppConfig


def _minimal_runtime_config() -> AppConfig:
    cfg = AppConfig(setup_complete=True)
    cfg.bot.provider = "local"
    cfg.camera.enabled = False
    cfg.audio.sound_detection_enabled = False
    cfg.audio.tts_enabled = False
    cfg.audio.play_remote_voice = False
    cfg.tts.enabled = False
    cfg.screen.screenshots_enabled = False
    cfg.screen.screen_video_enabled = False
    cfg.security.input_screen_snapshot = False
    cfg.security.input_screen_video_seconds = 0
    cfg.monitors.failed_login_events = False
    cfg.security.lock_on_guard_exit = False
    cfg.security.lock_after_countdown = False
    cfg.security.input_action = "notify"
    return cfg


def test_provider_auth_recovery_is_guided_and_secret_free():
    token = "123456:test-only-secret-token"
    exc = runtime_config.RuntimeConfigurationError(
        f"401 Unauthorized at https://example.invalid/bot{token}/getMe"
    )

    guidance = runtime_recovery.configuration_recovery(exc)

    assert guidance.capability == "Provider credentials"
    assert token not in guidance.summary
    assert all(token not in action for action in guidance.actions)
    assert any("reconfigure provider" in action for action in guidance.actions)


def test_diagnostic_log_redacts_known_tokens_and_bot_urls(tmp_path, monkeypatch):
    bot_token = "123456:test-only-secret-token"
    api_token = "api-test-only-secret"
    path = tmp_path / "runtime-diagnostics.jsonl"

    monkeypatch.setattr(runtime_recovery, "get_bot_token", lambda: bot_token)
    monkeypatch.setattr(runtime_recovery, "get_api_token", lambda: api_token)

    try:
        raise RuntimeError(
            f"https://example.invalid/bot{bot_token}/getMe token={api_token}"
        )
    except RuntimeError as exc:
        written = runtime_recovery.write_runtime_diagnostic(
            "provider-test",
            exc,
            path=path,
        )

    assert written == path
    data = path.read_text(encoding="utf-8")
    assert bot_token not in data
    assert api_token not in data
    assert "<redacted>" in data
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_camera_preflight_returns_direct_recovery_actions(monkeypatch):
    cfg = _minimal_runtime_config()
    cfg.camera.enabled = True

    def validate(_cfg, section):
        if section == "camera":
            return False, "camera unavailable"
        return True, "ok"

    monkeypatch.setattr(doctor, "validate_setup_section", validate)
    monkeypatch.setattr(doctor, "_lock_required", lambda _cfg: False)
    monkeypatch.setattr(
        input_monitor.InputMonitor,
        "available",
        property(lambda _self: True),
    )

    issues = runtime_recovery.startup_recovery_issues(cfg)

    assert [item.capability for item in issues] == ["Camera"]
    assert any("./run.sh test camera" in action for action in issues[0].actions)
    assert any("reconfigure camera" in action for action in issues[0].actions)


def test_permission_failure_identifies_input_capability():
    guidance = runtime_recovery.guidance_for_exception(
        "input-monitor-startup",
        PermissionError("permission denied for /dev/input/event4"),
    )

    assert guidance is not None
    assert guidance.capability == "Keyboard / mouse monitoring"
    assert any("./run.sh test input" in action for action in guidance.actions)
    assert all(
        "permission denied for /dev/input/event4" not in action
        for action in guidance.actions
    )


def test_cli_configuration_failure_prints_provider_recovery_without_secret(
    monkeypatch,
    capsys,
):
    token = "123456:test-only-secret-token"

    def fail_config(_console):
        raise runtime_config.RuntimeConfigurationError(
            f"401 Unauthorized /bot{token}/getMe"
        )

    monkeypatch.setattr(runtime_config, "ensure_runtime_configuration", fail_config)
    monkeypatch.setattr(
        runtime_recovery,
        "write_runtime_diagnostic",
        lambda *_args, **_kwargs: None,
    )

    assert cli.cmd_run(None) == 2
    output = capsys.readouterr().out
    assert token not in output
    assert "Provider credentials" in output
    assert "reconfigure provider" in output


def test_cli_unexpected_defect_is_logged_not_dumped(monkeypatch, capsys, tmp_path):
    cfg = _minimal_runtime_config()
    diagnostic = tmp_path / "runtime-diagnostics.jsonl"

    monkeypatch.setattr(
        runtime_config,
        "ensure_runtime_configuration",
        lambda _console: cfg,
    )
    monkeypatch.setattr(
        runtime_recovery,
        "startup_recovery_issues",
        lambda _cfg: [],
    )
    monkeypatch.setattr(
        runtime_recovery,
        "write_runtime_diagnostic",
        lambda *_args, **_kwargs: diagnostic,
    )

    class BrokenGuard:
        def __init__(self, _cfg):
            pass

        def run(self):
            raise AssertionError("internal-defect-detail")

    monkeypatch.setattr(guard, "LaptopGuard", BrokenGuard)

    assert cli.cmd_run(None) == 1
    output = capsys.readouterr().out
    assert "unexpected software error" in output.lower()
    assert "runtime-diagnostics.jsonl" in output
    assert "internal-defect-detail" not in output
    assert "Traceback" not in output


def test_runtime_config_noninteractive_provider_error_does_not_echo_exception(
    monkeypatch,
):
    cfg = AppConfig(setup_complete=True)
    cfg.bot.provider = "bale"
    cfg.bot.api_base = "https://example.invalid"
    token = "123456:test-only-secret-token"

    class FailingBot:
        def get_me(self):
            raise RuntimeError(f"401 Unauthorized /bot{token}/getMe")

    monkeypatch.setattr(runtime_config, "_interactive", lambda: False)
    monkeypatch.setattr(runtime_config, "get_bot_token", lambda: token)
    monkeypatch.setattr(runtime_config, "_provider", lambda *_args: FailingBot())
    monkeypatch.setattr(
        runtime_config,
        "write_runtime_diagnostic",
        lambda *_args, **_kwargs: None,
    )

    try:
        runtime_config._ask_valid_token(
            cfg,
            SimpleNamespace(print=lambda *_a, **_k: None),
        )
    except runtime_config.RuntimeConfigurationError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected RuntimeConfigurationError")

    assert token not in message
    assert "credential was rejected" in message
    assert "reconfigure provider" in message


def test_manual_bot_failure_is_guided_without_token(monkeypatch, capsys):
    cfg = AppConfig(setup_complete=True)
    cfg.bot.provider = "bale"
    cfg.bot.api_base = "https://example.invalid"
    cfg.bot.chat_id = 42
    token = "123456:test-only-secret-token"

    monkeypatch.setattr(
        tests_manual,
        "CONFIG_PATH",
        SimpleNamespace(exists=lambda: True),
    )
    monkeypatch.setattr(tests_manual, "setup_is_complete", lambda: True)
    monkeypatch.setattr(tests_manual, "load_config", lambda: cfg)
    monkeypatch.setattr(tests_manual, "get_bot_token", lambda: token)
    monkeypatch.setattr(
        tests_manual,
        "build_provider",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError(f"401 Unauthorized /bot{token}/getMe")
        ),
    )
    monkeypatch.setattr(
        tests_manual,
        "write_runtime_diagnostic",
        lambda *_args, **_kwargs: None,
    )

    assert tests_manual.test_bot() == 1
    output = capsys.readouterr().out
    assert token not in output
    assert "Provider credentials" in output
    assert "reconfigure provider" in output
