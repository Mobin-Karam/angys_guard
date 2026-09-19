from platform.identity import IdentityService


def test_identity_account_login_and_device(tmp_path):
    service = IdentityService(tmp_path / "identity.db")

    user = service.register("alice", "correct horse battery staple")
    token = service.authenticate("alice", "correct horse battery staple")
    device = service.register_device(user["id"], "linux", "guard-host")

    assert user["username"] == "alice"
    assert token
    assert device

    service.heartbeat(device)
