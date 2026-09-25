import os
import tempfile
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from server.app.main import app


def test_account_enrollment_bot_link_and_fixed_command_queue(monkeypatch):
    with tempfile.TemporaryDirectory() as directory:
        reply = AsyncMock()
        monkeypatch.setattr("server.app.main.respond", reply)
        monkeypatch.setenv("ANGYSGUARD_SERVER_SECRET", "x" * 32)
        monkeypatch.setenv("ANGYSGUARD_DATABASE_PATH", os.path.join(directory, "guard.db"))
        monkeypatch.setenv("ANGYSGUARD_TELEGRAM_WEBHOOK_SECRET", "telegram-webhook-secret")
        with TestClient(app) as client:
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
            # A claimed command is not replayed if a network retry occurs after
            # the agent has accepted it (important for the local lock action).
            assert client.get("/v1/device/commands", headers={"Authorization": f"Device {device['device_token']}"}).json() == {"commands": []}
            completed = client.post("/v1/device/commands/complete", headers={"Authorization": f"Device {device['device_token']}"}, json={"command_id": queued[0]["id"], "result": "online"})
            assert completed.status_code == 200
            reply.assert_awaited_with("telegram", "12345", "status: online")
            assert client.get("/v1/device/commands", headers={"Authorization": f"Device {device['device_token']}"}).json()["commands"][0]["action"] == "arm"
            # A fixed allowlist is the remote-control boundary.
            assert client.post("/v1/bots/telegram/updates", headers=headers, json={"message": {"chat": {"id": 12345}, "text": "/powershell whoami"}}).json() == {"status": "unsupported"}
            assert client.post(f"/v1/devices/{device['device_id']}/revoke", headers=bearer).json() == {"status": "revoked"}
            assert client.get("/v1/device/commands", headers={"Authorization": f"Device {device['device_token']}"}).status_code == 401
