"""Durable server outbox; HTTP/provider adapters call this application layer."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from angys_platform.gateway import CommandHandoff, RoutedCommand
from angys_platform.protocol import CommandEnvelope


class ServerDenied(ValueError):
    """Raised when a device poll or command queue request is invalid."""


class CommandServer:
    """Queue signed commands for enrolled devices without OS/provider access."""

    def __init__(self, database: str | Path, handoff: CommandHandoff) -> None:
        self.database = str(database)
        self.handoff = handoff
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS command_outbox (
                request_id TEXT PRIMARY KEY, device_id TEXT NOT NULL,
                payload TEXT NOT NULL, provider TEXT NOT NULL, provider_user_id TEXT NOT NULL,
                reply_chat_id TEXT NOT NULL,
                state TEXT NOT NULL DEFAULT 'queued', result TEXT,
                reply_attempts INTEGER NOT NULL DEFAULT 0
            )""")
            columns = {row[1] for row in db.execute("PRAGMA table_info(command_outbox)")}
            if "provider" not in columns:
                db.execute("ALTER TABLE command_outbox ADD COLUMN provider TEXT NOT NULL DEFAULT ''")
            if "provider_user_id" not in columns:
                db.execute("ALTER TABLE command_outbox ADD COLUMN provider_user_id TEXT NOT NULL DEFAULT ''")
            if "reply_chat_id" not in columns:
                db.execute("ALTER TABLE command_outbox ADD COLUMN reply_chat_id TEXT NOT NULL DEFAULT ''")
            if "result" not in columns:
                db.execute("ALTER TABLE command_outbox ADD COLUMN result TEXT")
            if "reply_attempts" not in columns:
                db.execute("ALTER TABLE command_outbox ADD COLUMN reply_attempts INTEGER NOT NULL DEFAULT 0")

    def _connect(self):
        return sqlite3.connect(self.database)

    def queue(self, routed: RoutedCommand) -> CommandEnvelope:
        envelope = self.handoff.envelope(routed)
        with self._connect() as db:
            db.execute(
                "INSERT INTO command_outbox(request_id,device_id,payload,provider,provider_user_id,reply_chat_id) VALUES(?,?,?,?,?,?)",
                (envelope.request_id, envelope.device_id, json.dumps(envelope.__dict__), routed.provider, routed.provider_user_id, routed.reply_chat_id),
            )
        return envelope

    def poll(self, device_id: str) -> CommandEnvelope | None:
        with self._connect() as db:
            row = db.execute(
                "SELECT request_id,payload FROM command_outbox WHERE device_id=? AND state='queued' ORDER BY rowid LIMIT 1",
                (device_id,),
            ).fetchone()
            if not row:
                return None
            db.execute("UPDATE command_outbox SET state='delivered' WHERE request_id=?", (row[0],))
        return CommandEnvelope(**json.loads(row[1]))

    def acknowledge(self, device_id: str, request_id: str, result: str = "completed") -> None:
        if not isinstance(result, str) or not result or len(result) > 512:
            raise ServerDenied("invalid command result")
        with self._connect() as db:
            cur = db.execute(
                "UPDATE command_outbox SET state='acknowledged', result=? WHERE device_id=? AND request_id=? AND state='delivered'",
                (result, device_id, request_id),
            )
        if cur.rowcount != 1:
            raise ServerDenied("unknown command acknowledgement")

    def completed_replies(self, provider: str):
        with self._connect() as db:
            rows = db.execute("SELECT request_id,reply_chat_id,result FROM command_outbox WHERE provider=? AND state='acknowledged'", (provider,)).fetchall()
        return rows

    def mark_reply_delivered(self, provider: str, request_id: str) -> None:
        """Mark one result sent only after the provider accepted the reply."""
        with self._connect() as db:
            db.execute(
                "UPDATE command_outbox SET state='replied' WHERE provider=? AND request_id=? AND state='acknowledged'",
                (provider, request_id),
            )

    def record_reply_failure(self, provider: str, request_id: str) -> None:
        """Bound provider-result retries so an outage cannot grow unbounded work."""
        with self._connect() as db:
            db.execute(
                """UPDATE command_outbox
                   SET reply_attempts=reply_attempts+1,
                       state=CASE WHEN reply_attempts+1 >= 3 THEN 'reply_failed' ELSE 'acknowledged' END
                   WHERE provider=? AND request_id=? AND state='acknowledged'""",
                (provider, request_id),
            )
