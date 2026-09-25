from server.app.security import (
    hash_password,
    issue_token,
    sign_device_command,
    token_digest,
    verify_password,
    verify_token,
)
from server.app.main import redacted_command_state


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
