from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path

from .config import DATA_DIR
from .storage import EventStore

EVENTS_FILE = DATA_DIR / "events.jsonl"


class EventLog:
    def __init__(self, path: Path = EVENTS_FILE, store: EventStore | None = None) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.store = store if store is not None else (EventStore() if path == EVENTS_FILE else None)

    def add(self, event_type: str, detail: str, severity: str = "info", media: str = "") -> dict:
        event = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "type": event_type,
            "severity": severity,
            "detail": detail,
            "media": media,
        }
        with self._lock, self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        if self.store is not None:
            try:
                self.store.add(event_type, detail, media, severity)
            except Exception:
                # JSONL remains the fail-safe log if SQLite is unavailable.
                pass
        return event

    def recent(self, limit: int = 10) -> list[dict]:
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return []
        out: list[dict] = []
        for line in lines[-max(1, min(limit, 50)):]:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return out
