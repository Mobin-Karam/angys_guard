from __future__ import annotations

from laptop_guard import doctor
from laptop_guard.models import AppConfig


def test_required_failure_is_actionable_and_returns_nonzero(monkeypatch, capsys):
    monkeypatch.setattr(
        doctor,
        "collect_checks",
        lambda: [
            doctor.DoctorCheck(
                "Camera",
                "required",
                False,
                "Configured camera is unavailable.",
                "Run: ./run.sh test camera",
            ),
            doctor.DoctorCheck(
                "Tkinter",
                "recommended",
                False,
                "Tkinter is unavailable.",
                "Run: sudo apt install python3-tk",
            ),
        ],
    )

    assert doctor.run_doctor() == 2
    output = capsys.readouterr().out
    assert "Required" in output
    assert "Next step: Run: ./run.sh test camera" in output
    assert "NOT READY" in output
    assert "Next: ./run.sh" not in output


def test_recommended_failure_does_not_block_readiness(monkeypatch, capsys):
    monkeypatch.setattr(
        doctor,
        "collect_checks",
        lambda: [
            doctor.DoctorCheck("Python", "required", True, "Python is ready."),
            doctor.DoctorCheck(
                "Tkinter",
                "recommended",
                False,
                "Tkinter is unavailable.",
                "Run: sudo apt install python3-tk",
            ),
        ],
    )

    assert doctor.run_doctor() == 0
    output = capsys.readouterr().out
    assert "READY: all required checks passed" in output
    assert "1 recommended check" in output
    assert "Next: ./run.sh" in output


def test_secret_permissions_require_private_mode(tmp_path, monkeypatch):
    path = tmp_path / "secrets.json"
    monkeypatch.setattr(doctor.config_module, "SECRETS_PATH", path)

    path.write_text('{"bot_token": "test-only-secret"}\n', encoding="utf-8")
    path.chmod(0o644)
    ok, detail = doctor._secret_permissions_ok()
    assert ok is False
    assert "test-only-secret" not in detail

    path.chmod(0o600)
    ok, detail = doctor._secret_permissions_ok()
    assert ok is True
    assert "0600" in detail


def test_bot_connectivity_never_exposes_token(monkeypatch):
    from laptop_guard import providers

    token = "test-only-super-secret-token"

    class FailingBot:
        client = None

        def get_me(self):
            raise RuntimeError(f"request failed for /bot{token}/getMe")

    monkeypatch.setattr(providers, "build_provider", lambda *_args, **_kwargs: FailingBot())
    cfg = AppConfig(setup_complete=True)
    cfg.bot.provider = "bale"
    cfg.bot.api_base = "https://example.invalid"

    ok, detail = doctor._bot_connectivity(cfg, token)

    assert ok is False
    assert token not in detail
    assert "authenticate or reach" in detail


def test_configured_required_feature_failure_has_recovery_action(monkeypatch):
    cfg = AppConfig(setup_complete=True)
    cfg.bot.provider = "local"
    cfg.camera.enabled = True
    cfg.audio.sound_detection_enabled = False
    cfg.security.lock_on_guard_exit = False
    cfg.security.lock_after_countdown = False
    cfg.security.input_action = "notify"
    cfg.security.warning_video = False
    cfg.security.input_screen_snapshot = False
    cfg.security.input_screen_video_seconds = 0
    cfg.security.stop_auth_enabled = False
    cfg.screen.screenshots_enabled = False
    cfg.screen.screen_video_enabled = False
    cfg.monitors.failed_login_events = False
    cfg.startup.enabled = False
    cfg.tts.enabled = False

    monkeypatch.setattr(doctor.platform, "system", lambda: "Linux")
    monkeypatch.setattr(doctor, "_python_version_ok", lambda: (True, "ok"))
    monkeypatch.setattr(doctor, "_venv_health_ok", lambda: (True, "ok"))
    monkeypatch.setattr(doctor, "_python_dependencies_ok", lambda: (True, "ok"))
    monkeypatch.setattr(doctor, "_config_integrity", lambda: (True, "ok"))
    monkeypatch.setattr(doctor, "_secret_permissions_ok", lambda: (True, "ok"))
    monkeypatch.setattr(doctor.config_module, "load_config", lambda: cfg)
    monkeypatch.setattr(doctor, "_camera_ok", lambda _index: (False, "camera unavailable"))
    monkeypatch.setattr(doctor, "_microphone_ok", lambda _cfg: (False, "microphone unavailable"))
    monkeypatch.setattr(doctor, "_tk_ok", lambda: (True, "ok"))

    checks = doctor.collect_checks()
    required_failures = [item for item in checks if item.category == "required" and not item.ok]

    assert [item.name for item in required_failures] == ["Camera"]
    assert all(item.action for item in required_failures)
