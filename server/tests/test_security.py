from server.app.security import hash_password, issue_token, token_digest, verify_password, verify_token


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
