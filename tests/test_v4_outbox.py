from pathlib import Path

from laptop_guard.storage import EventStore


def test_offline_queue_roundtrip(tmp_path: Path):
    store = EventStore(tmp_path / "events.db")
    item_id = store.enqueue("message", text="security alert", keyboard=[[('OK', 'menu')]])
    assert store.outbox_count() == 1
    pending = store.pending()
    assert pending[0].id == item_id
    assert pending[0].text == "security alert"
    store.mark_failed(item_id, "offline")
    assert store.pending()[0].attempts == 1
    store.mark_delivered(item_id)
    assert store.outbox_count() == 0


def test_event_severity_and_lookup(tmp_path: Path):
    store = EventStore(tmp_path / "events.db")
    event_id = store.add("input", "mouse", severity="high", metadata={"attempt": 2})
    row = store.get(event_id)
    assert row is not None
    assert row[5] == "high"
    assert "attempt" in row[6]
