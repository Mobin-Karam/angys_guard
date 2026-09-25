"""Managed test service: accounts, enrollment, bot links and fixed action queue.

This intentionally is not a generic remote administration service.  A connected
bot can enqueue only the actions in ALLOWED_ACTIONS and the Windows agent decides
whether its locally enabled capability permits the requested action.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated, Literal

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from .db import connection, initialize
from .security import (
    hash_password,
    issue_token,
    new_opaque_token,
    new_pairing_code,
    token_digest,
    verify_password,
    verify_token,
)

ALLOWED_ACTIONS = frozenset({"status", "arm", "disarm", "lock"})
PAIRING_LIFETIME_SECONDS = 600
COMMAND_LIFETIME_SECONDS = 120
AUTH_WINDOW_SECONDS = 900
AUTH_ATTEMPT_LIMIT = 10
_auth_attempts: dict[str, list[int]] = {}
_auth_attempts_lock = threading.Lock()


@dataclass(frozen=True)
class Settings:
    database_path: str
    jwt_secret: str
    telegram_token: str | None
    telegram_webhook_secret: str | None
    bale_token: str | None
    bale_webhook_secret: str | None

    @classmethod
    def from_environment(cls) -> "Settings":
        secret = os.environ.get("ANGYSGUARD_SERVER_SECRET", "")
        if len(secret) < 32:
            raise RuntimeError("ANGYSGUARD_SERVER_SECRET must be at least 32 characters")
        return cls(
            database_path=os.environ.get("ANGYSGUARD_DATABASE_PATH", "/data/angysguard.db"),
            jwt_secret=secret,
            telegram_token=os.environ.get("ANGYSGUARD_TELEGRAM_BOT_TOKEN"),
            telegram_webhook_secret=os.environ.get("ANGYSGUARD_TELEGRAM_WEBHOOK_SECRET"),
            bale_token=os.environ.get("ANGYSGUARD_BALE_BOT_TOKEN"),
            bale_webhook_secret=os.environ.get("ANGYSGUARD_BALE_WEBHOOK_SECRET"),
        )


settings: Settings | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global settings
    settings = Settings.from_environment()
    initialize(settings.database_path)
    yield


app = FastAPI(title="AngysGuard managed test service", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://tauri.localhost"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-Telegram-Bot-Api-Secret-Token", "X-AngysGuard-Bot-Secret"],
)


@app.middleware("http")
async def bound_request_size(request: Request, call_next):
    length = request.headers.get("content-length")
    if length:
        try:
            too_large = int(length) > 16_384
        except ValueError:
            too_large = True
        if too_large:
            raise HTTPException(status_code=413, detail="request body is too large")
    return await call_next(request)


def require_settings() -> Settings:
    if settings is None:
        raise HTTPException(status_code=503, detail="service is starting")
    return settings


def now() -> int:
    return int(time.time())


def current_account(authorization: Annotated[str | None, Header()] = None) -> str:
    configuration = require_settings()
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="authentication required")
    claims = verify_token(authorization.removeprefix("Bearer "), configuration.jwt_secret)
    if not claims:
        raise HTTPException(status_code=401, detail="invalid or expired session")
    return claims["sub"]


def limit_account_attempts(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    cutoff = now() - AUTH_WINDOW_SECONDS
    with _auth_attempts_lock:
        attempts = [attempt for attempt in _auth_attempts.get(client, []) if attempt >= cutoff]
        if len(attempts) >= AUTH_ATTEMPT_LIMIT:
            _auth_attempts[client] = attempts
            raise HTTPException(status_code=429, detail="too many account attempts; try again later")
        attempts.append(now())
        _auth_attempts[client] = attempts


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=256)


class LoginRequest(RegisterRequest):
    pass


class SessionResponse(BaseModel):
    access_token: str
    account_id: str


class PairStartRequest(BaseModel):
    device_name: str = Field(min_length=1, max_length=80)


class PairClaimRequest(BaseModel):
    pairing_code: str = Field(min_length=9, max_length=16)


class DeviceResponse(BaseModel):
    device_id: str
    device_token: str


class CommandCompletion(BaseModel):
    command_id: str
    result: str = Field(min_length=1, max_length=1000)


class RevokeResponse(BaseModel):
    status: str


class BotUpdate(BaseModel):
    chat_id: str = Field(min_length=1, max_length=128)
    text: str = Field(min_length=1, max_length=300)


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/accounts", response_model=SessionResponse, status_code=201)
def register(payload: RegisterRequest, _: Annotated[None, Depends(limit_account_attempts)]) -> SessionResponse:
    configuration = require_settings()
    account_id = str(uuid.uuid4())
    try:
        verifier = hash_password(payload.password)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    try:
        with connection(configuration.database_path) as db:
            db.execute("INSERT INTO accounts(id, email, password_hash, created_at) VALUES (?, ?, ?, ?)", (account_id, str(payload.email).lower(), verifier, now()))
    except Exception as error:
        if "UNIQUE constraint failed" in str(error):
            raise HTTPException(status_code=409, detail="account already exists") from error
        raise
    return SessionResponse(access_token=issue_token(account_id, configuration.jwt_secret), account_id=account_id)


@app.post("/v1/sessions", response_model=SessionResponse)
def login(payload: LoginRequest, _: Annotated[None, Depends(limit_account_attempts)]) -> SessionResponse:
    configuration = require_settings()
    with connection(configuration.database_path) as db:
        account = db.execute("SELECT id, password_hash FROM accounts WHERE email = ?", (str(payload.email).lower(),)).fetchone()
    if not account or not verify_password(payload.password, account["password_hash"]):
        raise HTTPException(status_code=401, detail="invalid email or password")
    return SessionResponse(access_token=issue_token(account["id"], configuration.jwt_secret), account_id=account["id"])


@app.post("/v1/devices/pairing-codes")
def start_pairing(payload: PairStartRequest, account_id: Annotated[str, Depends(current_account)]) -> dict[str, str | int]:
    configuration = require_settings()
    code = new_pairing_code()
    expires_at = now() + PAIRING_LIFETIME_SECONDS
    with connection(configuration.database_path) as db:
        db.execute("INSERT INTO pairing_codes(code, account_id, purpose, device_name, expires_at) VALUES (?, ?, 'device', ?, ?)", (code, account_id, payload.device_name, expires_at))
    return {"pairing_code": code, "expires_at": expires_at}


@app.post("/v1/devices/claim", response_model=DeviceResponse)
def claim_device(payload: PairClaimRequest, account_id: Annotated[str, Depends(current_account)]) -> DeviceResponse:
    configuration = require_settings()
    with connection(configuration.database_path) as db:
        pending = db.execute("SELECT account_id, device_name, expires_at, consumed_at FROM pairing_codes WHERE code = ? AND purpose = 'device'", (payload.pairing_code.upper(),)).fetchone()
        if not pending or pending["account_id"] != account_id or pending["consumed_at"] or pending["expires_at"] < now():
            raise HTTPException(status_code=400, detail="pairing code is invalid, expired, or already used")
        device_id, device_token = str(uuid.uuid4()), new_opaque_token()
        db.execute("INSERT INTO devices(id, account_id, name, credential_hash, created_at) VALUES (?, ?, ?, ?, ?)", (device_id, account_id, pending["device_name"], token_digest(device_token), now()))
        db.execute("UPDATE pairing_codes SET consumed_at = ? WHERE code = ?", (now(), payload.pairing_code.upper()))
    return DeviceResponse(device_id=device_id, device_token=device_token)


@app.post("/v1/devices/{device_id}/revoke", response_model=RevokeResponse)
def revoke_device(device_id: str, account_id: Annotated[str, Depends(current_account)]) -> RevokeResponse:
    configuration = require_settings()
    with connection(configuration.database_path) as db:
        changed = db.execute("UPDATE devices SET revoked_at = ? WHERE id = ? AND account_id = ? AND revoked_at IS NULL", (now(), device_id, account_id)).rowcount
    if changed != 1:
        raise HTTPException(status_code=404, detail="active device not found")
    return RevokeResponse(status="revoked")


def device_from_token(authorization: Annotated[str | None, Header()] = None):
    configuration = require_settings()
    if not authorization or not authorization.startswith("Device "):
        raise HTTPException(status_code=401, detail="device authentication required")
    with connection(configuration.database_path) as db:
        device = db.execute("SELECT id, account_id, revoked_at FROM devices WHERE credential_hash = ?", (token_digest(authorization.removeprefix("Device ")),)).fetchone()
    if not device or device["revoked_at"]:
        raise HTTPException(status_code=401, detail="unknown or revoked device")
    return device


@app.get("/v1/device/commands")
def poll_commands(device=Depends(device_from_token)) -> dict[str, list[dict[str, str]]]:
    configuration = require_settings()
    with connection(configuration.database_path) as db:
        db.execute("UPDATE devices SET last_seen_at = ? WHERE id = ?", (now(), device["id"]))
        rows = db.execute("SELECT id, action FROM commands WHERE device_id = ? AND claimed_at IS NULL AND completed_at IS NULL AND expires_at >= ? ORDER BY requested_at LIMIT 10", (device["id"], now())).fetchall()
        for row in rows:
            db.execute("UPDATE commands SET claimed_at = ? WHERE id = ? AND claimed_at IS NULL", (now(), row["id"]))
    return {"commands": [{"id": row["id"], "action": row["action"]} for row in rows]}


@app.post("/v1/device/commands/complete", status_code=200)
async def complete_command(payload: CommandCompletion, device=Depends(device_from_token)) -> dict[str, str]:
    configuration = require_settings()
    with connection(configuration.database_path) as db:
        command = db.execute("SELECT action, origin_provider, origin_chat_id FROM commands WHERE id = ? AND device_id = ? AND completed_at IS NULL", (payload.command_id, device["id"])).fetchone()
        if not command:
            raise HTTPException(status_code=404, detail="pending command not found")
        changed = db.execute("UPDATE commands SET completed_at = ?, result = ? WHERE id = ? AND device_id = ? AND completed_at IS NULL", (now(), payload.result, payload.command_id, device["id"])).rowcount
    if command["origin_provider"] and command["origin_chat_id"]:
        try:
            await respond(command["origin_provider"], command["origin_chat_id"], f"{command['action']}: {payload.result}")
        except httpx.HTTPError:
            # The action is already complete. A provider retry must not make the
            # device repeat it or turn this acknowledgement into a 5xx loop.
            pass
    return {"status": "completed"}


def bot_secret(provider: Literal["telegram", "bale"]) -> str | None:
    configuration = require_settings()
    return configuration.telegram_webhook_secret if provider == "telegram" else configuration.bale_webhook_secret


async def respond(provider: str, chat_id: str, text: str) -> None:
    configuration = require_settings()
    token = configuration.telegram_token if provider == "telegram" else configuration.bale_token
    if not token:
        return
    base_url = "https://api.telegram.org" if provider == "telegram" else "https://tapi.bale.ai"
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(f"{base_url}/bot{token}/sendMessage", json={"chat_id": chat_id, "text": text})


@app.post("/v1/bots/{provider}/updates", status_code=200)
async def bot_update(provider: Literal["telegram", "bale"], request: Request) -> dict[str, str]:
    expected = bot_secret(provider)
    supplied = request.headers.get("X-Telegram-Bot-Api-Secret-Token") or request.headers.get("X-AngysGuard-Bot-Secret")
    if not expected or not supplied or not __import__("hmac").compare_digest(expected, supplied):
        raise HTTPException(status_code=401, detail="invalid bot webhook secret")
    raw_update = await request.json()
    # Telegram sends {message:{chat:{id}, text}}. Bale integrations commonly use
    # the same shape; the flat form makes local webhook testing straightforward.
    candidate = raw_update.get("message", raw_update) if isinstance(raw_update, dict) else {}
    chat = candidate.get("chat", {}) if isinstance(candidate, dict) else {}
    try:
        payload = BotUpdate(
            chat_id=str(candidate.get("chat_id", chat.get("id", ""))),
            text=str(candidate.get("text", "")),
        )
    except Exception as error:
        raise HTTPException(status_code=422, detail="unsupported bot update") from error
    configuration = require_settings()
    parts = payload.text.strip().split(maxsplit=1)
    command = parts[0].lower().split("@", 1)[0]
    argument = parts[1].strip().upper() if len(parts) == 2 else ""
    if command == "/link" and argument:
        with connection(configuration.database_path) as db:
            code = db.execute("SELECT account_id, expires_at, consumed_at FROM pairing_codes WHERE code = ? AND purpose = 'bot'", (argument,)).fetchone()
            if not code or code["consumed_at"] or code["expires_at"] < now():
                await respond(provider, payload.chat_id, "Pairing code is invalid or expired.")
                return {"status": "ignored"}
            db.execute("INSERT OR REPLACE INTO bot_chats(provider, chat_id, account_id, created_at) VALUES (?, ?, ?, ?)", (provider, payload.chat_id, code["account_id"], now()))
            db.execute("UPDATE pairing_codes SET consumed_at = ? WHERE code = ?", (now(), argument))
        await respond(provider, payload.chat_id, "Bot linked. Use /devices, /status, /arm, /disarm, or /lock.")
        return {"status": "linked"}
    with connection(configuration.database_path) as db:
        chat = db.execute("SELECT account_id FROM bot_chats WHERE provider = ? AND chat_id = ?", (provider, payload.chat_id)).fetchone()
        if not chat:
            await respond(provider, payload.chat_id, "Link this chat first with /link YOUR-CODE.")
            return {"status": "unlinked"}
        if command == "/devices":
            devices = db.execute("SELECT name, id FROM devices WHERE account_id = ? AND revoked_at IS NULL", (chat["account_id"],)).fetchall()
            await respond(provider, payload.chat_id, "Devices:\n" + "\n".join(f"{row['name']} ({row['id'][:8]})" for row in devices))
            return {"status": "listed"}
        action = command.removeprefix("/")
        if action not in ALLOWED_ACTIONS:
            await respond(provider, payload.chat_id, "Allowed commands: /devices, /status, /arm, /disarm, /lock.")
            return {"status": "unsupported"}
        devices = db.execute("SELECT id FROM devices WHERE account_id = ? AND revoked_at IS NULL ORDER BY last_seen_at DESC", (chat["account_id"],)).fetchall()
        if len(devices) != 1:
            await respond(provider, payload.chat_id, "Choose one enrolled device in the desktop app; multi-device bot selection is not enabled in this test release.")
            return {"status": "ambiguous"}
        db.execute("INSERT INTO commands(id, device_id, action, requested_at, expires_at, origin_provider, origin_chat_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (str(uuid.uuid4()), devices[0]["id"], action, now(), now() + COMMAND_LIFETIME_SECONDS, provider, payload.chat_id))
    await respond(provider, payload.chat_id, f"Requested {action}. The enrolled device must be online and permit that action locally.")
    return {"status": "queued"}


@app.post("/v1/bot-pairing-codes")
def start_bot_pairing(account_id: Annotated[str, Depends(current_account)]) -> dict[str, str | int]:
    configuration = require_settings()
    code, expires_at = new_pairing_code(), now() + PAIRING_LIFETIME_SECONDS
    with connection(configuration.database_path) as db:
        db.execute("INSERT INTO pairing_codes(code, account_id, purpose, expires_at) VALUES (?, ?, 'bot', ?)", (code, account_id, expires_at))
    return {"pairing_code": code, "expires_at": expires_at}
