from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from laptop_guard import cli
from laptop_guard import config
from laptop_guard import service
from laptop_guard.models import AppConfig


class _Result:
    def __init__(self, returncode: int = 0) -> None:
        self.returncode = returncode


def test_service_status_reports_systemctl_failure(monkeypatch):
    monkeypatch.setattr(
        service.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=1),
    )
    assert service.status_service() is False


def test_cli_service_propagates_failure(monkeypatch):
    monkeypatch.setattr(service, "status_service", lambda: False)
    assert cli.cmd_service(SimpleNamespace(action="status")) == 2


def test_install_service_writes_safe_user_unit_and_enables_it(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service_dir = tmp_path / "systemd" / "user"
    service_path = service_dir / "laptop-guard.service"
    cfg = AppConfig(setup_complete=True)
    cfg.bot.provider = "local"
    calls: list[list[str]] = []

    monkeypatch.setattr(service, "SERVICE_DIR", service_dir)
    monkeypatch.setattr(service, "SERVICE_PATH", service_path)
    monkeypatch.setattr(config, "setup_is_complete", lambda: True)
    monkeypatch.setattr(config, "load_config", lambda: cfg)
    monkeypatch.setattr(config, "get_bot_token", lambda: "")
    monkeypatch.setattr(
        service.subprocess,
        "run",
        lambda command, **_kwargs: calls.append(list(command)) or _Result(0),
    )

    assert service.install_service(start_now=True) is True

    unit = service_path.read_text(encoding="utf-8")
    assert f"ExecStart={service.sys.executable} -m laptop_guard run" in unit
    assert "Environment=PYTHONUNBUFFERED=1" in unit
    assert "PassEnvironment=DISPLAY WAYLAND_DISPLAY" in unit
    assert "token" not in unit.lower()
    assert calls == [
        ["systemctl", "--user", "daemon-reload"],
        ["systemctl", "--user", "enable", "--now", "laptop-guard.service"],
    ]


def test_install_service_refuses_incomplete_setup_without_systemctl(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(service, "SERVICE_DIR", tmp_path / "systemd" / "user")
    monkeypatch.setattr(
        service,
        "SERVICE_PATH",
        tmp_path / "systemd" / "user" / "laptop-guard.service",
    )
    monkeypatch.setattr(config, "setup_is_complete", lambda: False)
    monkeypatch.setattr(
        service.subprocess,
        "run",
        lambda command, **_kwargs: calls.append(list(command)) or _Result(0),
    )

    assert service.install_service() is False
    assert calls == []
    assert not service.SERVICE_PATH.exists()


def test_set_autostart_disable_persists_config_and_calls_systemctl(
    monkeypatch,
) -> None:
    cfg = AppConfig(setup_complete=True)
    cfg.startup.enabled = True
    saved: list[bool] = []
    calls: list[list[str]] = []

    monkeypatch.setattr(config, "load_config", lambda: cfg)
    monkeypatch.setattr(
        config,
        "save_config",
        lambda current: saved.append(bool(current.startup.enabled)),
    )
    monkeypatch.setattr(
        service.subprocess,
        "run",
        lambda command, **_kwargs: calls.append(list(command)) or _Result(0),
    )

    assert service.set_autostart(False, start_now=True) is True
    assert saved == [False]
    assert calls == [
        ["systemctl", "--user", "disable", "--now", "laptop-guard.service"]
    ]


def test_uninstall_service_removes_unit_and_reloads_systemd(
    tmp_path: Path,
    monkeypatch,
) -> None:
    service_path = tmp_path / "laptop-guard.service"
    service_path.write_text("[Service]\n", encoding="utf-8")
    calls: list[list[str]] = []

    monkeypatch.setattr(service, "SERVICE_PATH", service_path)
    monkeypatch.setattr(
        service.subprocess,
        "run",
        lambda command, **_kwargs: calls.append(list(command)) or _Result(0),
    )

    assert service.uninstall_service() is True
    assert not service_path.exists()
    assert calls == [
        ["systemctl", "--user", "disable", "--now", "laptop-guard.service"],
        ["systemctl", "--user", "daemon-reload"],
    ]


def test_start_and_stop_service_use_fixed_systemctl_actions(tmp_path: Path, monkeypatch) -> None:
    service_path = tmp_path / "laptop-guard.service"
    service_path.write_text("[Service]\n", encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(service, "SERVICE_PATH", service_path)
    monkeypatch.setattr(
        service.subprocess,
        "run",
        lambda command, **_kwargs: calls.append(list(command)) or _Result(0),
    )

    assert service.start_service() is True
    assert service.stop_service() is True
    assert calls == [
        ["systemctl", "--user", "start", "laptop-guard.service"],
        ["systemctl", "--user", "stop", "laptop-guard.service"],
    ]
