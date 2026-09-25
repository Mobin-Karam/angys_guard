from server.app.security import (
    hash_password,
    issue_token,
    new_pairing_code,
    sign_device_command,
    token_digest,
    verify_password,
    verify_token,
)
from fastapi import HTTPException

from server.app.main import Settings, limit_pairing_attempts, redacted_command_state


def test_password_verifier_rejects_short_password_and_wrong_password():
    try:
        hash_password("too-short")
    except ValueError:
        pass
    else:
        raise AssertionError("short passwords must be rejected")
    encoded = hash_password("a secure test password")
    assert verify_password("a secure test password", encoded)
    assert not verify_password("not the password", encoded)


def test_sessions_are_signed_and_expire():
    token = issue_token("account-1", "x" * 32, lifetime_seconds=60)
    assert verify_token(token, "x" * 32)["sub"] == "account-1"
    assert verify_token(token, "y" * 32) is None


def test_device_credentials_are_not_stored_in_cleartext():
    raw = "test-device-token"
    assert token_digest(raw) != raw


def test_pairing_codes_have_80_bits_of_human_enterable_entropy():
    code = new_pairing_code()
    assert len(code) == 24
    assert code.count("-") == 4
    assert all(character in "0123456789ABCDEF-" for character in code)


def test_device_command_signatures_bind_scope_and_expiry():
    key = token_digest("test-device-token")
    signed = sign_device_command(
        key,
        device_id="device-1",
        account_id="account-1",
        action="status",
        command_id="command-1",
        issued_at=1_700_000_000,
        expires_at=1_700_000_060,
    )
    assert signed != sign_device_command(
        key,
        device_id="device-1",
        account_id="account-1",
        action="lock",
        command_id="command-1",
        issued_at=1_700_000_000,
        expires_at=1_700_000_060,
    )


def test_command_audit_never_returns_raw_agent_diagnostics():
    completed = {"completed_at": 1, "expires_at": 2, "result": "completed: /home/user/private-file"}
    denied = {"completed_at": 1, "expires_at": 2, "result": "denied: local consent is absent"}
    failed = {"completed_at": 1, "expires_at": 2, "result": "failed: token=secret"}
    assert redacted_command_state(completed) == "completed"
    assert redacted_command_state(denied) == "denied"
    assert redacted_command_state(failed) == "failed"


def test_command_audit_retention_setting_is_bounded(monkeypatch):
    monkeypatch.setenv("ANGYSGUARD_SERVER_SECRET", "x" * 32)
    monkeypatch.setenv("ANGYSGUARD_COMMAND_AUDIT_RETENTION_SECONDS", "2592000")
    assert Settings.from_environment().command_audit_retention_seconds == 2592000
    monkeypatch.setenv("ANGYSGUARD_COMMAND_AUDIT_RETENTION_SECONDS", "86399")
    try:
        Settings.from_environment()
    except RuntimeError:
        pass
    else:
        raise AssertionError("retention below one day must fail closed")


def test_pairing_attempts_are_rate_limited(monkeypatch):
    monkeypatch.setattr("server.app.main.PAIRING_ATTEMPT_LIMIT", 2)
    scope = "test-pairing-scope"
    limit_pairing_attempts(scope)
    limit_pairing_attempts(scope)
    try:
        limit_pairing_attempts(scope)
    except HTTPException as error:
        assert error.status_code == 429
    else:
        raise AssertionError("pairing attempts must be rate limited")
