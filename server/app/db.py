"""SQLite persistence for the deliberately small managed-test deployment."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS accounts (
  id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS devices (
  id TEXT PRIMARY KEY, account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  name TEXT NOT NULL, credential_hash TEXT NOT NULL, created_at INTEGER NOT NULL,
  revoked_at INTEGER, last_seen_at INTEGER
);
CREATE TABLE IF NOT EXISTS pairing_codes (
  code TEXT PRIMARY KEY, account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  purpose TEXT NOT NULL, device_name TEXT, expires_at INTEGER NOT NULL, consumed_at INTEGER
);
CREATE TABLE IF NOT EXISTS bot_chats (
  provider TEXT NOT NULL, chat_id TEXT NOT NULL, account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  created_at INTEGER NOT NULL, selected_device_id TEXT REFERENCES devices(id) ON DELETE SET NULL,
  PRIMARY KEY(provider, chat_id)
);
CREATE TABLE IF NOT EXISTS bot_confirmations (
  provider TEXT NOT NULL, chat_id TEXT NOT NULL, action TEXT NOT NULL,
  device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL, expires_at INTEGER NOT NULL, consumed_at INTEGER,
  PRIMARY KEY(provider, chat_id, action)
);
CREATE TABLE IF NOT EXISTS commands (
  id TEXT PRIMARY KEY, device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  action TEXT NOT NULL, requested_at INTEGER NOT NULL, expires_at INTEGER NOT NULL,
  origin_provider TEXT, origin_chat_id TEXT, claimed_at INTEGER, completed_at INTEGER, result TEXT
);
CREATE INDEX IF NOT EXISTS commands_pending_by_device ON commands(device_id, completed_at, expires_at);
"""


def initialize(path: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(target) as connection:
        connection.executescript(SCHEMA)
        # Safe for the initial test schema and for databases created before the
        # one-shot command claim field was introduced.
        columns = {row[1] for row in connection.execute("PRAGMA table_info(commands)")}
        if "claimed_at" not in columns:
            connection.execute("ALTER TABLE commands ADD COLUMN claimed_at INTEGER")
        if "origin_provider" not in columns:
            connection.execute("ALTER TABLE commands ADD COLUMN origin_provider TEXT")
        if "origin_chat_id" not in columns:
            connection.execute("ALTER TABLE commands ADD COLUMN origin_chat_id TEXT")
        chat_columns = {row[1] for row in connection.execute("PRAGMA table_info(bot_chats)")}
        if "selected_device_id" not in chat_columns:
            connection.execute("ALTER TABLE bot_chats ADD COLUMN selected_device_id TEXT")


@contextmanager
def connection(path: str) -> Iterator[sqlite3.Connection]:
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()
