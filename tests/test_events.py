from laptop_guard.events import EventLog


def test_event_log_roundtrip(tmp_path):
    log = EventLog(tmp_path / 'events.jsonl')
    log.add('input', 'keyboard', 'high')
    items = log.recent(5)
    assert items[-1]['type'] == 'input'
    assert items[-1]['detail'] == 'keyboard'
