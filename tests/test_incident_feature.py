from __future__ import annotations

from types import SimpleNamespace

from laptop_guard.events import EventLog
from laptop_guard.features.incidents import IncidentFeature
from laptop_guard.guard import LaptopGuard
from laptop_guard.models import AppConfig, BotConfig
from laptop_guard.storage import EventStore


class FakeApi:
    def __init__(self) -> None:
        self.sent: list[tuple[str, object]] = []

    def send_photo(self, _chat_id, path, caption):
        self.sent.append((caption, path))

    def send_video(self, _chat_id, path, caption):
        self.sent.append((caption, path))

    def send_document(self, _chat_id, path, caption):
        self.sent.append((caption, path))


def test_incident_menu_filters_and_acknowledges(tmp_path):
    store = EventStore(tmp_path / "events.db")
    log = EventLog(tmp_path / "events.jsonl", store=store)
    event_id = store.add("failed_login", "source=sshd", severity="critical")
    guard = LaptopGuard.__new__(LaptopGuard)
    guard.events = log

    text, markup = guard.incident_menu("critical")
    assert f"#{event_id}" in text
    assert "incident:ack:" in str(markup)

    text, _markup = guard.acknowledge_incident(str(event_id))
    assert "تأیید شد" in text
    assert store.recent_incidents(("critical",))[0].acknowledged_at is not None


def test_incident_evidence_rejects_paths_outside_media_root(tmp_path, monkeypatch):
    store = EventStore(tmp_path / "events.db")
    outside = tmp_path / "outside.txt"
    outside.write_text("not evidence", encoding="utf-8")
    event_id = store.add("input", "mouse", str(outside), "high")
    guard = LaptopGuard.__new__(LaptopGuard)
    guard.events = EventLog(tmp_path / "events.jsonl", store=store)
    guard.api = FakeApi()
    guard.state = SimpleNamespace(mutate=lambda **_changes: None)
    replies: list[str] = []
    guard._reply_to_chat = lambda _chat_id, text, *_args: replies.append(text)
    media_root = tmp_path / "media"
    media_root.mkdir()
    monkeypatch.setattr("laptop_guard.guard.MEDIA_DIR", media_root)

    guard.open_incident_evidence(7, str(event_id))

    assert not guard.api.sent
    assert "خارج از محدوده" in replies[-1]


def test_incident_feature_routes_only_known_actions():
    calls: list[tuple] = []
    host = SimpleNamespace(
        feature_incident_menu=lambda severity: (f"menu:{severity}", {}),
        feature_acknowledge_incident=lambda event_id: (f"ack:{event_id}", {}),
        feature_edit_or_reply=lambda *args: calls.append(args),
        feature_open_incident_evidence=lambda *args: calls.append(args),
    )
    feature = IncidentFeature(host)

    feature._callback(7, 2, "incident:high")
    feature._callback(7, 2, "incident:ack:12")
    feature._callback(7, 2, "incident:unexpected")

    assert calls[0][2] == "menu:high"
    assert calls[1][2] == "ack:12"
    assert calls[2][2] == "menu:all"
