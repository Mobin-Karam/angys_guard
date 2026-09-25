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
  code_hash TEXT PRIMARY KEY, account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
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
  issued_at INTEGER, signature TEXT, origin_provider TEXT, origin_chat_id TEXT,
  claimed_at INTEGER, completed_at INTEGER, result TEXT
);
CREATE INDEX IF NOT EXISTS commands_pending_by_device ON commands(device_id, completed_at, expires_at);
"""

PAIRING_CODES_SCHEMA = """
CREATE TABLE pairing_codes (
  code_hash TEXT PRIMARY KEY, account_id TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  purpose TEXT NOT NULL, device_name TEXT, expires_at INTEGER NOT NULL, consumed_at INTEGER
)
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
        if "issued_at" not in columns:
            connection.execute("ALTER TABLE commands ADD COLUMN issued_at INTEGER")
        if "signature" not in columns:
            connection.execute("ALTER TABLE commands ADD COLUMN signature TEXT")
        pairing_columns = {row[1] for row in connection.execute("PRAGMA table_info(pairing_codes)")}
        if "code_hash" not in pairing_columns:
            # Pending pre-hash codes cannot be safely migrated: retaining their
            # cleartext would preserve the secret this migration removes.
            connection.execute("DROP TABLE pairing_codes")
            connection.execute(PAIRING_CODES_SCHEMA)
        chat_columns = {row[1] for row in connection.execute("PRAGMA table_info(bot_chats)")}
        if "selected_device_id" not in chat_columns:
            connection.execute("ALTER TABLE bot_chats ADD COLUMN selected_device_id TEXT")


def purge_expired_records(path: str, *, timestamp: int, command_audit_retention_seconds: int) -> None:
    """Delete expired pilot credentials and aged command diagnostics.

    Command results can include local diagnostics supplied by the desktop agent.
    They are intentionally retained only for the small pilot's bounded audit
    window and are never returned verbatim through the bot.
    """

    cutoff = timestamp - command_audit_retention_seconds
    with connection(path) as db:
        db.execute("DELETE FROM pairing_codes WHERE expires_at < ?", (timestamp,))
        db.execute("DELETE FROM bot_confirmations WHERE expires_at < ?", (timestamp,))
        db.execute(
            "DELETE FROM commands WHERE completed_at IS NOT NULL AND completed_at < ?",
            (cutoff,),
        )
        db.execute(
            "DELETE FROM commands WHERE completed_at IS NULL AND expires_at < ?",
            (cutoff,),
        )


@contextmanager
def connection(path: str) -> Iterator[sqlite3.Connection]:
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()
