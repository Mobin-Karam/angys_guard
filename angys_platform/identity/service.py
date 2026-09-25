from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
import time
import uuid
from pathlib import Path


class IdentityService:
    """SQLite-backed account and device identity service.

    This is the first server-side identity boundary for Platform v2. The storage
    layer intentionally remains SQLite so deployment can start without external
    infrastructure.
    """

    def __init__(self, database: str | Path = "angysguard_platform.db"):
        self.database = str(database)
        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.database)

    def _initialize(self):
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS users_devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    device_id TEXT UNIQUE NOT NULL,
                    os TEXT NOT NULL,
                    hostname TEXT NOT NULL,
                    permissions TEXT NOT NULL DEFAULT '{}',
                    status TEXT NOT NULL DEFAULT 'active',
                    last_seen INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS provider_links (
                    provider TEXT NOT NULL,
                    provider_user_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    linked_at INTEGER NOT NULL,
                    PRIMARY KEY(provider, provider_user_id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
                """
            )

    @staticmethod
    def _hash(password: str) -> str:
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 310000
        ).hex()
        return f"pbkdf2_sha256${salt}${digest}"

    @staticmethod
    def _verify(password: str, stored: str) -> bool:
        _, salt, digest = stored.split("$", 2)
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 310000
        ).hex()
        return hmac.compare_digest(candidate, digest)

    def register(self, username: str, password: str):
        with self._connect() as db:
            cur = db.execute(
                "INSERT INTO users(username,password_hash,created_at) VALUES(?,?,?)",
                (username, self._hash(password), int(time.time())),
            )
            return {"id": cur.lastrowid, "username": username}

    def authenticate(self, username: str, password: str):
        with self._connect() as db:
            row = db.execute(
                "SELECT id,password_hash FROM users WHERE username=?", (username,)
            ).fetchone()
            if not row or not self._verify(password, row[1]):
                raise ValueError("invalid credentials")
            token = secrets.token_urlsafe(32)
            db.execute(
                "INSERT INTO sessions(token,user_id,created_at) VALUES(?,?,?)",
                (token, row[0], int(time.time())),
            )
            return token

    def register_device(self, user_id: int, os: str, hostname: str):
        device_id = str(uuid.uuid4())
        with self._connect() as db:
            db.execute(
                """INSERT INTO users_devices
                (user_id,device_id,os,hostname,last_seen)
                VALUES(?,?,?,?,?)""",
                (user_id, device_id, os, hostname, int(time.time())),
            )
        return device_id

    def heartbeat(self, device_id: str):
        with self._connect() as db:
            db.execute(
                "UPDATE users_devices SET last_seen=? WHERE device_id=?",
                (int(time.time()), device_id),
            )

    def device_owner(self, device_id: str) -> int | None:
        """Return the active account that owns a device, if any."""
        with self._connect() as db:
            row = db.execute(
                "SELECT user_id FROM users_devices WHERE device_id=? AND status='active'",
                (device_id,),
            ).fetchone()
        return int(row[0]) if row else None

    def link_provider_account(
        self, provider: str, provider_user_id: str, user_id: int
    ) -> None:
        """Persist a provider account link after the pairing flow authorizes it."""
        with self._connect() as db:
            if not db.execute("SELECT 1 FROM users WHERE id=?", (user_id,)).fetchone():
                raise ValueError("unknown user")
            db.execute(
                """INSERT INTO provider_links(provider,provider_user_id,user_id,linked_at)
                VALUES(?,?,?,?)
                ON CONFLICT(provider,provider_user_id) DO UPDATE SET
                    user_id=excluded.user_id,
                    linked_at=excluded.linked_at""",
                (provider, provider_user_id, user_id, int(time.time())),
            )

    def linked_provider_account(
        self, provider: str, provider_user_id: str
    ) -> int | None:
        """Return the linked account for one provider identity, if present."""
        with self._connect() as db:
            row = db.execute(
                "SELECT user_id FROM provider_links WHERE provider=? AND provider_user_id=?",
                (provider, provider_user_id),
            ).fetchone()
        return int(row[0]) if row else None
