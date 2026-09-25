import os
import tempfile
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from server.app.main import app
from server.app.security import sign_device_command, token_digest


def test_missing_server_configuration_stays_alive_for_paas_diagnostics(monkeypatch):
    monkeypatch.delenv("ANGYSGUARD_SERVER_SECRET", raising=False)
    with TestClient(app) as client:
        assert client.get("/healthz").json() == {"status": "degraded"}
        ready = client.get("/readyz")
        assert ready.status_code == 503
        assert ready.json() == {"detail": "configuration or storage is unavailable"}


def test_account_enrollment_bot_link_and_fixed_command_queue(monkeypatch):
    with tempfile.TemporaryDirectory() as directory:
        reply = AsyncMock()
        monkeypatch.setattr("server.app.main.respond", reply)
        monkeypatch.setenv("ANGYSGUARD_SERVER_SECRET", "x" * 32)
        monkeypatch.setenv("ANGYSGUARD_DATABASE_PATH", os.path.join(directory, "guard.db"))
        monkeypatch.setenv("ANGYSGUARD_TELEGRAM_WEBHOOK_SECRET", "telegram-webhook-secret")
        with TestClient(app) as client:
            assert client.get("/").json() == {"service": "AngysGuard managed test", "status": "ok", "health": "/healthz"}
            assert client.get("/healthz").json() == {"status": "ok"}
            assert client.get("/readyz").json() == {"status": "ready"}
            created = client.post("/v1/accounts", json={"email": "owner@example.com", "password": "a secure test password"})
            assert created.status_code == 201
            bearer = {"Authorization": f"Bearer {created.json()['access_token']}"}
            device_code = client.post("/v1/devices/pairing-codes", headers=bearer, json={"device_name": "Windows 11"}).json()["pairing_code"]
            device = client.post("/v1/devices/claim", headers=bearer, json={"pairing_code": device_code}).json()
            bot_code = client.post("/v1/bot-pairing-codes", headers=bearer).json()["pairing_code"]
            headers = {"X-Telegram-Bot-Api-Secret-Token": "telegram-webhook-secret"}
            assert client.post("/v1/bots/telegram/updates", headers=headers, json={"message": {"chat": {"id": 12345}, "text": f"/link {bot_code}"}}).json() == {"status": "linked"}
            assert client.post("/v1/bots/telegram/updates", headers=headers, json={"message": {"chat": {"id": 12345}, "text": "/status"}}).json() == {"status": "queued"}
            assert client.post("/v1/bots/telegram/updates", headers=headers, json={"message": {"chat": {"id": 12345}, "text": "/arm"}}).json() == {"status": "queued"}
            queued = client.get("/v1/device/commands", headers={"Authorization": f"Device {device['device_token']}"}).json()["commands"]
            assert len(queued) == 1 and queued[0]["action"] == "status"
            assert queued[0]["account_id"] == created.json()["account_id"]
            assert queued[0]["signature"] == sign_device_command(
                token_digest(device["device_token"]),
                device_id=device["device_id"],
                account_id=created.json()["account_id"],
                action="status",
                command_id=queued[0]["id"],
                issued_at=queued[0]["issued_at"],
                expires_at=queued[0]["expires_at"],
            )
            # A claimed command is not replayed if a network retry occurs after
            # the agent has accepted it (important for the local lock action).
            assert client.get("/v1/device/commands", headers={"Authorization": f"Device {device['device_token']}"}).json() == {"commands": []}
            completed = client.post("/v1/device/commands/complete", headers={"Authorization": f"Device {device['device_token']}"}, json={"command_id": queued[0]["id"], "result": "online"})
            assert completed.status_code == 200
            reply.assert_awaited_with("telegram", "12345", "status: completed")
            assert client.get("/v1/device/commands", headers={"Authorization": f"Device {device['device_token']}"}).json()["commands"][0]["action"] == "arm"
            assert client.post("/v1/bots/telegram/updates", headers=headers, json={"message": {"chat": {"id": 12345}, "text": "/events"}}).json() == {"status": "events"}
            events = reply.await_args_list[-1].args[2]
            assert "status: completed" in events and "arm: pending" in events
            assert "online" not in events
            # A fixed allowlist is the remote-control boundary.
            assert client.post("/v1/bots/telegram/updates", headers=headers, json={"message": {"chat": {"id": 12345}, "text": "/powershell whoami"}}).json() == {"status": "unsupported"}
            assert client.post(f"/v1/devices/{device['device_id']}/revoke", headers=bearer).json() == {"status": "revoked"}
            assert client.get("/v1/device/commands", headers={"Authorization": f"Device {device['device_token']}"}).status_code == 401


def test_bot_selects_one_of_multiple_devices_and_revocation_needs_confirmation(monkeypatch):
    with tempfile.TemporaryDirectory() as directory:
        reply = AsyncMock()
        monkeypatch.setattr("server.app.main.respond", reply)
        monkeypatch.setenv("ANGYSGUARD_SERVER_SECRET", "x" * 32)
        monkeypatch.setenv("ANGYSGUARD_DATABASE_PATH", os.path.join(directory, "guard.db"))
        monkeypatch.setenv("ANGYSGUARD_TELEGRAM_WEBHOOK_SECRET", "telegram-webhook-secret")
        with TestClient(app) as client:
            account = client.post("/v1/accounts", json={"email": "owner@example.com", "password": "a secure test password"}).json()
            bearer = {"Authorization": f"Bearer {account['access_token']}"}
            devices = []
            for name in ("Linux laptop", "Linux desktop"):
                code = client.post("/v1/devices/pairing-codes", headers=bearer, json={"device_name": name}).json()["pairing_code"]
                devices.append(client.post("/v1/devices/claim", headers=bearer, json={"pairing_code": code}).json())
            bot_code = client.post("/v1/bot-pairing-codes", headers=bearer).json()["pairing_code"]
            headers = {"X-Telegram-Bot-Api-Secret-Token": "telegram-webhook-secret"}
            update = lambda text: client.post("/v1/bots/telegram/updates", headers=headers, json={"message": {"chat": {"id": 12345}, "text": text}})
            assert update(f"/link {bot_code}").json() == {"status": "linked"}
            assert update("/status").json() == {"status": "ambiguous"}
            assert update(f"/use {devices[1]['device_id'][:8]}").json() == {"status": "selected"}
            assert update("/status").json() == {"status": "queued"}
            queued = client.get("/v1/device/commands", headers={"Authorization": f"Device {devices[1]['device_token']}"}).json()["commands"]
            assert queued[0]["action"] == "status"
            assert update("/revoke").json() == {"status": "confirmation-required"}
            confirmation_text = reply.await_args_list[-1].args[2]
            confirmation_code = confirmation_text.split("/confirm-revoke ", 1)[1].split()[0]
            assert update(f"/confirm-revoke {confirmation_code}").json() == {"status": "revoked"}
            assert update(f"/confirm-revoke {confirmation_code}").json() == {"status": "invalid-confirmation"}
            assert client.get("/v1/device/commands", headers={"Authorization": f"Device {devices[1]['device_token']}"}).status_code == 401
