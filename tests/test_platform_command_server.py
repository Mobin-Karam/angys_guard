import pytest

from angys_platform.gateway import CommandHandoff, GatewayRouter
from angys_platform.identity import IdentityService
from angys_platform.protocol import DeviceProtocol
from angys_platform.server import CommandServer


def test_server_queues_polls_and_acknowledges_signed_device_command(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    owner = identity.register("owner", "password")
    device = identity.register_device(owner["id"], "linux", "host")
    router = GatewayRouter(identity)
    router.link_provider_account("telegram", "owner", owner["id"])
    secret = b"device-credential"
    server = CommandServer(tmp_path / "server.db", CommandHandoff({device: (1, secret)}))
    queued = server.queue(router.route("telegram", "owner", device, "shutdown"))
    received = server.poll(device)
    assert received and DeviceProtocol(device, owner["id"], 1, secret).accept(received).action == "shutdown"
    server.acknowledge(device, queued.request_id)
    assert server.poll(device) is None


def test_server_rejects_unbounded_device_result(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    owner = identity.register("owner", "password")
    device = identity.register_device(owner["id"], "linux", "host")
    router = GatewayRouter(identity)
    router.link_provider_account("telegram", "9", owner["id"])
    server = CommandServer(tmp_path / "server.db", CommandHandoff({device: (1, b"credential")}))
    queued = server.queue(router.route("telegram", "9", device, "status"))
    server.poll(device)

    with pytest.raises(ValueError, match="invalid command result"):
        server.acknowledge(device, queued.request_id, "x" * 513)
