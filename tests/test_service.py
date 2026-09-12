from types import SimpleNamespace

from laptop_guard import cli
from laptop_guard import service


def test_service_status_reports_systemctl_failure(monkeypatch):
    monkeypatch.setattr(service.subprocess, "run", lambda *_args, **_kwargs: SimpleNamespace(returncode=1))
    assert service.status_service() is False


def test_cli_service_propagates_failure(monkeypatch):
    monkeypatch.setattr(service, "status_service", lambda: False)
    assert cli.cmd_service(SimpleNamespace(action="status")) == 2
