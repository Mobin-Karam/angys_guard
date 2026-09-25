"""Small, dependency-free primitives for the managed test service.

The service deliberately keeps Windows credentials out of its data model.  It
stores only salted account-password verifiers and hashes of revocable device
credentials.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(password: str, *, salt: bytes | None = None) -> str:
    if len(password) < 12:
        raise ValueError("password must contain at least 12 characters")
    salt = salt or os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600_000)
    return f"pbkdf2_sha256$600000${_b64(salt)}${_b64(derived)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256" or int(rounds) < 600_000:
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), _unb64(salt), int(rounds)
        )
        return hmac.compare_digest(actual, _unb64(expected))
    except (ValueError, TypeError):
        return False


def new_opaque_token() -> str:
    return secrets.token_urlsafe(32)


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def device_command_payload(
    *,
    device_id: str,
    account_id: str,
    action: str,
    command_id: str,
    issued_at: int,
    expires_at: int,
) -> bytes:
    """Canonical finite command payload shared with the desktop verifier."""

    return "\n".join((device_id, account_id, action, command_id, str(issued_at), str(expires_at))).encode("utf-8")


def sign_device_command(
    credential_hash: str,
    *,
    device_id: str,
    account_id: str,
    action: str,
    command_id: str,
    issued_at: int,
    expires_at: int,
) -> str:
    """Sign a command using a key only the enrolled device can derive.

    The database holds a hash of the device credential, not the credential
    itself. The device derives the same SHA-256 bytes from its keyring-held
    credential. This pilot symmetric design gives each device a distinct key;
    a future managed production service should migrate to an asymmetric issuer.
    """

    try:
        key = bytes.fromhex(credential_hash)
    except ValueError as error:
        raise ValueError("invalid enrolled device credential digest") from error
    return _b64(
        hmac.new(
            key,
            device_command_payload(
                device_id=device_id,
                account_id=account_id,
                action=action,
                command_id=command_id,
                issued_at=issued_at,
                expires_at=expires_at,
            ),
            hashlib.sha256,
        ).digest()
    )


def new_pairing_code() -> str:
    # Deliberately short enough to enter in a bot, but only useful for 10 minutes
    # and always bound to a pending account action.
    return "-".join((secrets.token_hex(2), secrets.token_hex(2))).upper()


def issue_token(subject: str, secret: str, *, lifetime_seconds: int = 900) -> str:
    now = int(time.time())
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _b64(
        json.dumps({"sub": subject, "iat": now, "exp": now + lifetime_seconds}, separators=(",", ":")).encode()
    )
    signed = f"{header}.{payload}".encode("ascii")
    signature = _b64(hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


def verify_token(token: str, secret: str) -> dict[str, Any] | None:
    try:
        header, payload, signature = token.split(".")
        signed = f"{header}.{payload}".encode("ascii")
        expected = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _unb64(signature)):
            return None
        claims = json.loads(_unb64(payload))
        return claims if isinstance(claims.get("sub"), str) and int(claims["exp"]) >= int(time.time()) else None
    except (ValueError, TypeError, json.JSONDecodeError):
        return None
