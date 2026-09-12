from types import SimpleNamespace

from laptop_guard import config as config_module
from laptop_guard import service
from laptop_guard.models import AppConfig


def test_startup_and_arming_are_separate_defaults():
    cfg = AppConfig()
    assert cfg.startup.enabled is False
    assert cfg.security.auto_arm is False


def test_enabling_for_next_login_does_not_start_immediately(tmp_path, monkeypatch):
    cfg = AppConfig()
    service_path = tmp_path / "laptop-guard.service"
    service_path.write_text("unit")
    commands = []

    monkeypatch.setattr(service, "SERVICE_PATH", service_path)
    monkeypatch.setattr(config_module, "load_config", lambda: cfg)
    monkeypatch.setattr(config_module, "save_config", lambda value: None)
    monkeypatch.setattr(
        service.subprocess,
        "run",
        lambda command, **_kwargs: commands.append(command) or SimpleNamespace(returncode=0),
    )

    assert service.set_autostart(True, start_now=False) is True
    assert cfg.startup.enabled is True
    assert commands == [["systemctl", "--user", "enable", "laptop-guard.service"]]
