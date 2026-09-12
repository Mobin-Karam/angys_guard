import json
from pathlib import Path

import laptop_guard.chat_surface as cs


def test_chat_manager_writes_owner_and_reads_visitor(tmp_path, monkeypatch):
    monkeypatch.setattr(cs, "CHAT_DIR", tmp_path)
    monkeypatch.setattr(cs, "INBOX", tmp_path / "inbox.jsonl")
    monkeypatch.setattr(cs, "OUTBOX", tmp_path / "outbox.jsonl")
    monkeypatch.setattr(cs, "MIRROR", tmp_path / "mirror.txt")
    monkeypatch.setattr(cs, "STATE", tmp_path / "state.json")
    got = []
    mgr = cs.SecurityChatManager(got.append)
    mgr.send_owner("سلام")
    assert "سلام" in cs.INBOX.read_text(encoding="utf-8")
    assert "سلام" in cs.MIRROR.read_text(encoding="utf-8")
    with cs.OUTBOX.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"time": "12:00:00", "text": "پاسخ"}, ensure_ascii=False) + "\n")
    # Exercise the parser directly without depending on timing.
    mgr._outbox_pos = 0
    import threading, time
    mgr._ensure_poller()
    deadline = time.time() + 2
    while time.time() < deadline and not got:
        time.sleep(0.05)
    mgr.stop()
    assert got == ["پاسخ"]
