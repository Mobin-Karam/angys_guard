"""Single-use, short-lived device pairing codes for provider account linking."""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
import time
from pathlib import Path


class PairingDenied(ValueError):
    """Raised when a pairing code cannot safely be consumed."""


class PairingService:
    def __init__(self, database: str | Path) -> None:
        self.database = str(database)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS pairing_codes (
                code_hash TEXT PRIMARY KEY, device_id TEXT NOT NULL,
                expires_at INTEGER NOT NULL, consumed_at INTEGER
            )""")

    def _connect(self):
        return sqlite3.connect(self.database)

    @staticmethod
    def _hash(code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()

    def start(self, device_id: str, now: int | None = None) -> str:
        now = int(time.time()) if now is None else now
        code = secrets.token_urlsafe(9)
        with self._connect() as db:
            db.execute("DELETE FROM pairing_codes WHERE expires_at < ? OR consumed_at IS NOT NULL", (now,))
            db.execute("INSERT INTO pairing_codes(code_hash,device_id,expires_at) VALUES(?,?,?)", (self._hash(code), device_id, now + 300))
        return code

    def consume(self, code: str, now: int | None = None) -> str:
        now = int(time.time()) if now is None else now
        with self._connect() as db:
            row = db.execute("SELECT device_id,expires_at,consumed_at FROM pairing_codes WHERE code_hash=?", (self._hash(code),)).fetchone()
            if not row or row[1] < now or row[2] is not None:
                raise PairingDenied("invalid or expired pairing code")
            db.execute("UPDATE pairing_codes SET consumed_at=? WHERE code_hash=? AND consumed_at IS NULL", (now, self._hash(code)))
        return str(row[0])
