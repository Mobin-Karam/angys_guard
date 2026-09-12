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

    def enqueue(
        self,
        kind: str,
        text: str = "",
        media_path: str = "",
        caption: str = "",
        keyboard=None,
    ) -> int:
        with self._connect() as db:
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

    def mark_delivered(self, item_id: int) -> None:
        with self._connect() as db:
            db.execute("DELETE FROM outbox WHERE id=?", (item_id,))

    def mark_failed(self, item_id: int, error: str) -> None:
        with self._connect() as db:
            db.execute(
                "UPDATE outbox SET attempts=attempts+1, last_error=? WHERE id=?",
                (error[-500:], item_id),
            )
