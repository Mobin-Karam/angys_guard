from laptop_guard.events import EventLog
from laptop_guard.storage import EventStore


def test_event_log_roundtrip(tmp_path):
    log = EventLog(tmp_path / 'events.jsonl')
    log.add('input', 'keyboard', 'high')
    items = log.recent(5)
    assert items[-1]['type'] == 'input'
    assert items[-1]['detail'] == 'keyboard'


def test_guard_events_are_visible_in_shared_sqlite_store(tmp_path):
    store = EventStore(tmp_path / 'events.sqlite3')
    log = EventLog(tmp_path / 'events.jsonl', store=store)
    log.add('arm', 'Guard armed', 'info')
    row = store.recent(1)[0]
    assert row[2] == 'arm'
    assert row[3] == 'Guard armed'
