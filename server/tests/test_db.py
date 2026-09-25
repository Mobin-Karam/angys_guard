from __future__ import annotations

import os
import sqlite3
import tempfile

from server.app.db import connection, initialize, purge_expired_records


def test_purge_expired_records_removes_old_diagnostics_but_keeps_recent_audit():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "managed.db")
        initialize(path)
        with connection(path) as db:
            db.execute("INSERT INTO accounts(id, email, password_hash, created_at) VALUES ('account', 'owner@example.test', 'hash', 1)")
            db.execute("INSERT INTO devices(id, account_id, name, credential_hash, created_at) VALUES ('device', 'account', 'Desktop', 'hash', 1)")
            db.execute("INSERT INTO pairing_codes(code_hash, account_id, purpose, expires_at) VALUES ('expired-code-hash', 'account', 'device', 99)")
            db.execute("INSERT INTO bot_confirmations(provider, chat_id, action, device_id, token_hash, expires_at) VALUES ('telegram', 'chat', 'revoke', 'device', 'hash', 99)")
            db.execute("INSERT INTO commands(id, device_id, action, requested_at, expires_at, completed_at, result) VALUES ('old', 'device', 'status', 1, 2, 2, 'failed: raw private diagnostic')")
            db.execute("INSERT INTO commands(id, device_id, action, requested_at, expires_at, completed_at, result) VALUES ('recent', 'device', 'status', 199, 200, 200, 'completed: local status')")
            db.execute("INSERT INTO commands(id, device_id, action, requested_at, expires_at) VALUES ('expired-pending', 'device', 'status', 1, 2)")

        purge_expired_records(path, timestamp=200, command_audit_retention_seconds=100)

        with connection(path) as db:
            assert db.execute("SELECT count(*) FROM pairing_codes").fetchone()[0] == 0
            assert db.execute("SELECT count(*) FROM bot_confirmations").fetchone()[0] == 0
            assert [row[0] for row in db.execute("SELECT id FROM commands ORDER BY id")] == ["recent"]


def test_upgrade_invalidates_old_cleartext_pairing_codes():
    with tempfile.TemporaryDirectory() as directory:
        path = os.path.join(directory, "legacy.db")
        with sqlite3.connect(path) as db:
            db.execute(
                "CREATE TABLE pairing_codes (code TEXT PRIMARY KEY, account_id TEXT, purpose TEXT, device_name TEXT, expires_at INTEGER, consumed_at INTEGER)"
            )
            db.execute("INSERT INTO pairing_codes VALUES ('OLD-CODE', 'account', 'device', NULL, 9999999, NULL)")

        initialize(path)

        with connection(path) as db:
            assert "code_hash" in {row[1] for row in db.execute("PRAGMA table_info(pairing_codes)")}
            assert db.execute("SELECT count(*) FROM pairing_codes").fetchone()[0] == 0
            db.execute("INSERT INTO pairing_codes(code_hash, account_id, purpose, expires_at) VALUES ('new-code-hash', 'account', 'device', 9999999)")
