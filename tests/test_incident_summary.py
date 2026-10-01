from types import SimpleNamespace

from laptop_guard.guard import LaptopGuard


def test_incident_summary_prioritizes_notable_events_without_media_paths():
    guard = LaptopGuard.__new__(LaptopGuard)
    guard.events = SimpleNamespace(
        recent=lambda _limit: [
            {"time": "2026-01-01T10:00:00", "severity": "info", "type": "camera", "detail": "normal", "media": "/private/normal.png"},
            {"time": "2026-01-01T10:01:00", "severity": "critical", "type": "failed_login", "detail": "source=sshd", "media": "/private/evidence.png"},
        ]
    )

    text = guard.incident_summary_text()

    assert "failed_login" in text
    assert "camera | normal" not in text
    assert "/private/" not in text


def test_incident_summary_handles_empty_event_log():
    guard = LaptopGuard.__new__(LaptopGuard)
    guard.events = SimpleNamespace(recent=lambda _limit: [])

    assert "هنوز رویدادی ثبت نشده" in guard.incident_summary_text()
