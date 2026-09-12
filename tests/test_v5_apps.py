from pathlib import Path

from laptop_guard.app_manager import AppManager, DesktopApp


def test_app_manager_respects_allowlist(monkeypatch):
    fake = {
        "firefox.desktop": DesktopApp("firefox.desktop", "Firefox", "firefox", Path("/x")),
        "bad.desktop": DesktopApp("bad.desktop", "Bad", "bad", Path("/y")),
    }
    monkeypatch.setattr(AppManager, "_discover", lambda self: fake)
    mgr = AppManager(["firefox.desktop"])
    assert [a.desktop_id for a in mgr.allowed_apps()] == ["firefox.desktop"]
    ok, _ = mgr.launch("bad.desktop")
    assert ok is False
