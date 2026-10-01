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


def test_outbox_is_bounded_to_one_hundred_messages(tmp_path: Path):
    store = EventStore(tmp_path / "events.db")
    for number in range(102):
        store.enqueue("message", text=str(number))

    assert store.outbox_count() == 100
    assert store.pending(1)[0].text == "2"


def test_event_severity_and_lookup(tmp_path: Path):
    store = EventStore(tmp_path / "events.db")
    event_id = store.add("input", "mouse", severity="high", metadata={"attempt": 2})
    row = store.get(event_id)
    assert row is not None
    assert row[5] == "high"
    assert "attempt" in row[6]


def test_incidents_can_be_filtered_and_acknowledged_without_rewriting_event(tmp_path: Path):
    store = EventStore(tmp_path / "events.db")
    warning_id = store.add("input", "keyboard", severity="warning")
    critical_id = store.add("failed_login", "sshd", severity="critical")

    assert [item.id for item in store.recent_incidents(("critical",))] == [critical_id]
    assert store.acknowledge_incident(warning_id)
    assert not store.acknowledge_incident(99999)

    rows = store.recent_incidents(("warning", "critical"))
    assert rows[0].id == critical_id
    assert rows[1].id == warning_id
    assert rows[1].acknowledged_at is not None
    assert store.get(warning_id)[3] == "keyboard"
