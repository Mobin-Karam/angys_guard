from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import EVENT_DB_PATH, ensure_dirs


@dataclass
class OutboxItem:
    id: int
    kind: str
    text: str
    media_path: str
    caption: str
    keyboard_json: str
    attempts: int


@dataclass(frozen=True)
class IncidentItem:
    id: int
    created_at: str
    kind: str
    detail: str
    media_path: str
    severity: str
    acknowledged_at: str | None


class EventStore:
    def __init__(self, path: Path = EVENT_DB_PATH) -> None:
        ensure_dirs()
        self.path = path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.path, timeout=5)

    def _columns(self, db, table: str) -> set[str]:
        return {str(row[1]) for row in db.execute(f"PRAGMA table_info({table})")}

    def _init_db(self) -> None:
        with self._connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    detail TEXT NOT NULL DEFAULT '',
                    media_path TEXT NOT NULL DEFAULT '',
                    severity TEXT NOT NULL DEFAULT 'notice',
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            cols = self._columns(db, "events")
            if "severity" not in cols:
                db.execute("ALTER TABLE events ADD COLUMN severity TEXT NOT NULL DEFAULT 'notice'")
            if "metadata_json" not in cols:
                db.execute("ALTER TABLE events ADD COLUMN metadata_json TEXT NOT NULL DEFAULT '{}'")
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS outbox (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    text TEXT NOT NULL DEFAULT '',
                    media_path TEXT NOT NULL DEFAULT '',
                    caption TEXT NOT NULL DEFAULT '',
                    keyboard_json TEXT NOT NULL DEFAULT '',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT NOT NULL DEFAULT ''
                )
                """
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS incident_acknowledgements (
                    event_id INTEGER PRIMARY KEY,
                    acknowledged_at TEXT NOT NULL,
                    FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE
                )
                """
            )

    def add(
        self,
        kind: str,
        detail: str = "",
        media_path: str = "",
        severity: str = "notice",
        metadata: dict | None = None,
    ) -> int:
        with self._connect() as db:
            cur = db.execute(
                "INSERT INTO events(created_at, kind, detail, media_path, severity, metadata_json) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    datetime.now().isoformat(timespec="seconds"),
                    kind,
                    detail,
                    media_path,
                    severity,
                    json.dumps(metadata or {}, ensure_ascii=False),
                ),
            )
            return int(cur.lastrowid)

    def recent(self, limit: int = 20) -> list[tuple]:
        with self._connect() as db:
            return list(
                db.execute(
                    "SELECT id, created_at, kind, detail, media_path, severity FROM events ORDER BY id DESC LIMIT ?",
                    (limit,),
                )
            )

    def get(self, event_id: int) -> tuple | None:
        with self._connect() as db:
            return db.execute(
                "SELECT id, created_at, kind, detail, media_path, severity, metadata_json FROM events WHERE id=?",
                (event_id,),
            ).fetchone()

    def recent_incidents(self, severities: tuple[str, ...] = (), limit: int = 5) -> list[IncidentItem]:
        """Return a bounded incident view without mutating the original event."""
        allowed = {"warning", "high", "critical"}
        selected = tuple(value for value in severities if value in allowed) or tuple(sorted(allowed))
        safe_limit = max(1, min(int(limit), 10))
        placeholders = ", ".join("?" for _ in selected)
        query = (
            "SELECT events.id, events.created_at, events.kind, events.detail, events.media_path, "
            "events.severity, incident_acknowledgements.acknowledged_at "
            "FROM events LEFT JOIN incident_acknowledgements "
            "ON incident_acknowledgements.event_id = events.id "
            f"WHERE events.severity IN ({placeholders}) ORDER BY events.id DESC LIMIT ?"
        )
        with self._connect() as db:
            rows = db.execute(query, (*selected, safe_limit)).fetchall()
        return [IncidentItem(*row) for row in rows]

    def acknowledge_incident(self, event_id: int) -> bool:
        if event_id <= 0:
            return False
        with self._connect() as db:
            if db.execute("SELECT 1 FROM events WHERE id=?", (event_id,)).fetchone() is None:
                return False
            db.execute(
                "INSERT OR IGNORE INTO incident_acknowledgements(event_id, acknowledged_at) VALUES (?, ?)",
                (event_id, datetime.now().isoformat(timespec="seconds")),
            )
        return True

    def enqueue(
        self,
        kind: str,
        text: str = "",
        media_path: str = "",
        caption: str = "",
        keyboard=None,
    ) -> int:
        """Queue a small owner text notification, retaining at most 100 items."""
        with self._connect() as db:
            db.execute(
                "DELETE FROM outbox WHERE id IN (SELECT id FROM outbox ORDER BY id ASC LIMIT "
                "(SELECT MAX(COUNT(*) - 99, 0) FROM outbox))"
            )
            cur = db.execute(
                "INSERT INTO outbox(created_at, kind, text, media_path, caption, keyboard_json) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    datetime.now().isoformat(timespec="seconds"),
                    kind,
                    text,
                    media_path,
                    caption,
                    json.dumps(keyboard or [], ensure_ascii=False),
                ),
            )
            return int(cur.lastrowid)

    def pending(self, limit: int = 20) -> list[OutboxItem]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT id, kind, text, media_path, caption, keyboard_json, attempts FROM outbox ORDER BY id ASC LIMIT ?",
                (limit,),
            ).fetchall()
        return [OutboxItem(*row) for row in rows]

    def outbox_count(self) -> int:
        with self._connect() as db:
            return int(db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0])

    def outbox_retry_count(self) -> int:
        with self._connect() as db:
            return int(db.execute("SELECT COUNT(*) FROM outbox WHERE attempts > 0").fetchone()[0])

    def latest_outbox_error(self) -> str:
        with self._connect() as db:
            row = db.execute(
                "SELECT last_error FROM outbox WHERE last_error != '' ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return str(row[0]) if row is not None else ""

    def mark_delivered(self, item_id: int) -> None:
        with self._connect() as db:
            db.execute("DELETE FROM outbox WHERE id=?", (item_id,))

    def mark_failed(self, item_id: int, error: str) -> None:
        with self._connect() as db:
            db.execute(
                "UPDATE outbox SET attempts=attempts+1, last_error=? WHERE id=?",
                (error[-500:], item_id),
            )
