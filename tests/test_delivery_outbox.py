from __future__ import annotations

import threading
import time
from types import SimpleNamespace

from laptop_guard.events import EventLog
from laptop_guard.guard import LaptopGuard
from laptop_guard.models import AppConfig, BotConfig
from laptop_guard.storage import EventStore


class FlakyApi:
    def __init__(self) -> None:
        self.online = False
        self.sent: list[str] = []

    def send_message(self, _chat_id, text, reply_markup=None) -> None:
        if not self.online:
            raise OSError("provider offline")
        self.sent.append(text)


def make_guard(tmp_path):
    guard = LaptopGuard.__new__(LaptopGuard)
    guard.config = AppConfig(bot=BotConfig(provider="local", chat_id=7))
    guard.events = EventLog(tmp_path / "events.jsonl", store=EventStore(tmp_path / "events.db"))
    guard.api = FlakyApi()
    guard._send_lock = threading.Lock()
    guard._outbox_flush_lock = threading.Lock()
    guard.state = SimpleNamespace(mutate=lambda **_changes: None)
    return guard


def test_failed_text_delivery_is_queued_and_flushed_after_recovery(tmp_path):
    guard = make_guard(tmp_path)
    guard._send("alert one")
    assert guard.events.store.outbox_count() == 1

    guard.api.online = True
    guard._flush_outbox_async()
    for _ in range(30):
        if guard.events.store.outbox_count() == 0:
            break
        time.sleep(0.01)

    assert guard.events.store.outbox_count() == 0
    assert guard.api.sent == ["alert one"]


def test_recovery_export_is_redacted_and_temporary(tmp_path, monkeypatch):
    guard = make_guard(tmp_path)
    documents: list[dict] = []
    guard.api.send_document = lambda _chat_id, path, _caption: documents.append(__import__("json").loads(path.read_text()))
    monkeypatch.setattr("laptop_guard.guard.DATA_DIR", tmp_path)

    guard.export_recovery_diagnostics(7)

    assert documents[0]["owner_binding"] is True
    assert "token" not in str(documents[0]).lower()
    assert not list(tmp_path.glob("*.json"))
