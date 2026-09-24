from dataclasses import replace

import pytest

from angys_platform.gateway import GatewayRouter
from angys_platform.identity import IdentityService
from angys_platform.server import WakeDenied, WakeOnLanGateway
from angys_platform.server import CommandServer, OfficialBotService
from angys_platform.gateway import CommandHandoff, ProviderUpdateAdapter


class FakeSocket:
    def __init__(self, *_): self.options, self.sent = [], []
    def __enter__(self): return self
    def __exit__(self, *_): return None
    def setsockopt(self, *value): self.options.append(value)
    def sendto(self, packet, target): self.sent.append((packet, target))


class FakeProvider:
    def __init__(self, updates): self.updates, self.sent = updates, []
    def get_updates(self, offset=None): return self.updates
    def send_message(self, chat_id, text): self.sent.append((chat_id, text))


def _route(tmp_path, action="wake"):
    identity = IdentityService(tmp_path / "identity.db")
    owner = identity.register("owner", "password")
    device = identity.register_device(owner["id"], "linux", "host")
    router = GatewayRouter(identity)
    router.link_provider_account("telegram", "9", owner["id"])
    return owner, device, router.route("telegram", "9", device, action)


def test_wol_sends_magic_packet_only_to_enrolled_owner_target(tmp_path):
    owner, device, route = _route(tmp_path)
    sockets = []
    def factory(*args):
        item = FakeSocket(*args)
        sockets.append(item)
        return item
    wol = WakeOnLanGateway(tmp_path / "wake.db", factory)
    wol.configure(device, owner["id"], "AA-BB-CC-DD-EE-FF", "192.168.1.255")

    wol.wake(route)

    assert sockets[0].sent == [(b"\xff" * 6 + bytes.fromhex("aabbccddeeff") * 16, ("192.168.1.255", 9))]


def test_wol_rejects_arbitrary_targets_and_revoked_or_wrong_owner_requests(tmp_path):
    owner, device, route = _route(tmp_path)
    wol = WakeOnLanGateway(tmp_path / "wake.db", FakeSocket)
    with pytest.raises(WakeDenied):
        wol.configure(device, owner["id"], "not-a-mac", "192.168.1.255")
    with pytest.raises(WakeDenied):
        wol.configure(device, owner["id"], "aa:bb:cc:dd:ee:ff", "192.168.1.1")
    wol.configure(device, owner["id"], "aa:bb:cc:dd:ee:ff", "192.168.1.255")
    wol.revoke(device, owner["id"])
    with pytest.raises(WakeDenied, match="unavailable"):
        wol.wake(route)
    with pytest.raises(WakeDenied, match="not a wake"):
        wol.wake(replace(route, action="status"))


def test_official_bot_dispatches_only_configured_wake_action(tmp_path):
    owner, device, route = _route(tmp_path)
    sockets = []
    def factory(*args):
        item = FakeSocket(*args)
        sockets.append(item)
        return item
    wol = WakeOnLanGateway(tmp_path / "wake.db", factory)
    wol.configure(device, owner["id"], "aa:bb:cc:dd:ee:ff", "192.168.1.255")
    provider = FakeProvider([{"update_id": 1, "message": {"from": {"id": 9}, "chat": {"id": 9}, "text": f"/device {device} wake"}}])
    service = OfficialBotService("telegram", provider, ProviderUpdateAdapter(GatewayRouter(IdentityService(tmp_path / "identity.db"))), CommandServer(tmp_path / "commands.db", CommandHandoff({device: (1, b"credential")})), wol)

    assert service.run_once() == 1
    assert sockets[0].sent
    assert provider.sent == [(9, "Wake packet sent to the enrolled device network.")]
