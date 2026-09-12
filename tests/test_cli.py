from laptop_guard import cli


def test_lock_command_reports_failure(monkeypatch):
    monkeypatch.setattr(cli, "lock_screen", lambda: False)
    assert cli.cmd_lock(None) == 2


def test_lock_command_reports_success(monkeypatch):
    monkeypatch.setattr(cli, "lock_screen", lambda: True)
    assert cli.cmd_lock(None) == 0
