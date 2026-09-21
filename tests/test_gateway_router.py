import pytest

from angys_platform.gateway import GatewayDenied, GatewayRouter, ProviderUpdateAdapter
from angys_platform.identity import IdentityService


def test_gateway_routes_only_linked_owner_fixed_actions(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    user = identity.register("owner", "password")
    device = identity.register_device(user["id"], "linux", "host")
    router = GatewayRouter(identity)

    router.link_provider_account("bale", "owner-chat", user["id"])
    routed = router.route("bale", "owner-chat", device, "reboot")

    assert routed.device_id == device
    assert routed.action == "reboot"
    with pytest.raises(GatewayDenied):
        router.route("bale", "other-chat", device, "reboot")
    with pytest.raises(GatewayDenied):
        router.route("bale", "owner-chat", device, "shell")
    with pytest.raises(GatewayDenied):
        router.route("telegram", "owner-chat", device, "reboot")


def test_gateway_provider_link_survives_router_restart(tmp_path):
    database = tmp_path / "identity.db"
    identity = IdentityService(database)
    user = identity.register("owner", "password")
    device = identity.register_device(user["id"], "linux", "host")

    GatewayRouter(identity).link_provider_account("telegram", "12345", user["id"])
    routed = GatewayRouter(IdentityService(database)).route(
        "telegram", "12345", device, "status"
    )

    assert routed.account_id == user["id"]


def test_gateway_rejects_unknown_account_and_invalid_provider(tmp_path):
    router = GatewayRouter(IdentityService(tmp_path / "identity.db"))

    with pytest.raises(GatewayDenied):
        router.link_provider_account("telegram", "12345", 999)
    with pytest.raises(GatewayDenied):
        router.link_provider_account("unknown", "12345", 1)
    with pytest.raises(GatewayDenied):
        router.link_provider_account(None, "12345", 1)  # type: ignore[arg-type]


def test_provider_update_adapter_routes_only_explicit_command(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    owner = identity.register("owner", "password")
    device = identity.register_device(owner["id"], "linux", "host")
    router = GatewayRouter(identity)
    router.link_provider_account("telegram", "99", owner["id"])
    adapter = ProviderUpdateAdapter(router)

    routed = adapter.receive("telegram", {"message": {"from": {"id": 99}, "text": f"/device {device} shutdown"}})
    assert routed.action == "shutdown"
    with pytest.raises(GatewayDenied):
        adapter.receive("telegram", {"message": {"from": {"id": 99}, "text": "/device arbitrary shell"}})
