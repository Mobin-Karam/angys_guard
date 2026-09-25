"""Small, dependency-free signed envelope verifier for enrolled devices."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sqlite3
import time
from dataclasses import dataclass


class ProtocolDenied(ValueError):
    """Raised when an incoming managed command fails closed."""


@dataclass(frozen=True)
class CommandEnvelope:
    device_id: str
    account_id: int
    action: str
    credential_generation: int
    request_id: str
    issued_at: int
    expires_at: int
    signature: str

    def payload(self) -> bytes:
        return json.dumps(
            {
                "account_id": self.account_id,
                "action": self.action,
                "credential_generation": self.credential_generation,
                "device_id": self.device_id,
                "expires_at": self.expires_at,
                "issued_at": self.issued_at,
                "request_id": self.request_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()

    @classmethod
    def issue(
        cls, secret: bytes, device_id: str, account_id: int, action: str,
        credential_generation: int, request_id: str, expires_at: int,
        issued_at: int | None = None,
    ) -> "CommandEnvelope":
        issued_at = int(time.time()) if issued_at is None else issued_at
        unsigned = cls(device_id, account_id, action, credential_generation,
                       request_id, issued_at, expires_at, "")
        signature = base64.urlsafe_b64encode(
            hmac.new(secret, unsigned.payload(), hashlib.sha256).digest()
        ).decode()
        return cls(
            device_id, account_id, action, credential_generation, request_id,
            issued_at, expires_at, signature,
        )


class DeviceProtocol:
    """Verifies finite signed requests before handing them to local policy."""

    ACTIONS = frozenset({"status", "arm", "disarm", "lock", "suspend", "reboot", "shutdown"})

    def __init__(self, device_id: str, account_id: int, credential_generation: int, secret: bytes, cache_path: str = ":memory:"):
        self.device_id = device_id
        self.account_id = account_id
        self.credential_generation = credential_generation
        self.secret = secret
        self._cache_path = cache_path
        self._memory_connection = sqlite3.connect(cache_path) if cache_path == ":memory:" else None
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS consumed_requests (request_id TEXT PRIMARY KEY, expires_at INTEGER NOT NULL)")

    def _connect(self):
        return self._memory_connection or sqlite3.connect(self._cache_path)

    def accept(self, envelope: CommandEnvelope, now: int | None = None) -> CommandEnvelope:
        now = int(time.time()) if now is None else now
        if (envelope.device_id != self.device_id or envelope.account_id != self.account_id
                or envelope.credential_generation != self.credential_generation):
            raise ProtocolDenied("command scope does not match this device")
        if envelope.action not in self.ACTIONS or not envelope.request_id:
            raise ProtocolDenied("unsupported command")
        if envelope.issued_at > now or envelope.expires_at < now:
            raise ProtocolDenied("expired command")
        with self._connect() as db:
            db.execute("DELETE FROM consumed_requests WHERE expires_at < ?", (now,))
            if db.execute("SELECT 1 FROM consumed_requests WHERE request_id=?", (envelope.request_id,)).fetchone():
                raise ProtocolDenied("replayed command")
        expected = base64.urlsafe_b64encode(
            hmac.new(self.secret, envelope.payload(), hashlib.sha256).digest()
        ).decode()
        if not hmac.compare_digest(expected, envelope.signature):
            raise ProtocolDenied("invalid command signature")
        with self._connect() as db:
            db.execute("INSERT INTO consumed_requests(request_id,expires_at) VALUES(?,?)", (envelope.request_id, envelope.expires_at))
        return envelope
