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
                payload TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'queued'
            )""")

    def _connect(self):
        return sqlite3.connect(self.database)

    def queue(self, routed: RoutedCommand) -> CommandEnvelope:
        envelope = self.handoff.envelope(routed)
        with self._connect() as db:
            db.execute(
                "INSERT INTO command_outbox(request_id,device_id,payload) VALUES(?,?,?)",
                (envelope.request_id, envelope.device_id, json.dumps(envelope.__dict__)),
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

    def acknowledge(self, device_id: str, request_id: str) -> None:
        with self._connect() as db:
            cur = db.execute(
                "UPDATE command_outbox SET state='acknowledged' WHERE device_id=? AND request_id=? AND state='delivered'",
                (device_id, request_id),
            )
        if cur.rowcount != 1:
            raise ServerDenied("unknown command acknowledgement")
