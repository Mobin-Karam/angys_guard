from angys_platform.gateway import CommandHandoff, GatewayRouter, ProviderUpdateAdapter
from angys_platform.identity import IdentityService, PairingService
from angys_platform.server import CommandServer, OfficialBotService


class FakeProvider:
    def __init__(self, updates): self.updates, self.sent = updates, []
    def get_updates(self, offset=None): return self.updates
    def send_message(self, chat_id, text): self.sent.append((chat_id, text))


class FailingReplyProvider(FakeProvider):
    def send_message(self, chat_id, text):
        raise RuntimeError("provider unavailable")


def test_official_bot_pairs_then_queues_authorized_command(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    owner = identity.register("owner", "password")
    device = identity.register_device(owner["id"], "linux", "host")
    pairing = PairingService(tmp_path / "pairing.db")
    secret = b"credential"
    commands = CommandServer(tmp_path / "server.db", CommandHandoff({device: (1, secret)}))
    provider = FakeProvider([
        {"update_id": 1, "message": {"from": {"id": 9}, "chat": {"id": 9}, "text": f"/pair {pairing.start(device)}"}},
        {"update_id": 2, "message": {"from": {"id": 9}, "chat": {"id": 9}, "text": f"/device {device} lock"}},
    ])
    service = OfficialBotService("telegram", provider, ProviderUpdateAdapter(GatewayRouter(identity), pairing), commands)
    assert service.run_once() == 2
    assert commands.poll(device).action == "lock"
    assert provider.sent == [(9, "Device paired successfully."), (9, "Command queued for the enrolled device.")]


def test_official_bot_returns_completed_device_result(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    owner = identity.register("owner", "password")
    device = identity.register_device(owner["id"], "linux", "host")
    router = GatewayRouter(identity)
    router.link_provider_account("telegram", "9", owner["id"])
    commands = CommandServer(tmp_path / "server.db", CommandHandoff({device: (1, b"credential")}))
    command = commands.queue(router.route("telegram", "9", device, "status"))
    commands.poll(device)
    commands.acknowledge(device, command.request_id, "armed")
    provider = FakeProvider([])
    service = OfficialBotService("telegram", provider, ProviderUpdateAdapter(router), commands)
    service.run_once()
    assert provider.sent == [(9, f"Device result: armed ({command.request_id})")]
    assert commands.completed_replies("telegram") == []


def test_official_bot_retries_result_when_provider_send_fails(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    owner = identity.register("owner", "password")
    device = identity.register_device(owner["id"], "linux", "host")
    router = GatewayRouter(identity)
    router.link_provider_account("telegram", "9", owner["id"])
    commands = CommandServer(tmp_path / "server.db", CommandHandoff({device: (1, b"credential")}))
    command = commands.queue(router.route("telegram", "9", device, "status"))
    commands.poll(device)
    commands.acknowledge(device, command.request_id, "armed")

    OfficialBotService("telegram", FailingReplyProvider([]), ProviderUpdateAdapter(router), commands).run_once()

    assert commands.completed_replies("telegram") == [(command.request_id, "9", "armed")]


def test_official_bot_stops_retrying_after_three_failed_result_replies(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    owner = identity.register("owner", "password")
    device = identity.register_device(owner["id"], "linux", "host")
    router = GatewayRouter(identity)
    router.link_provider_account("telegram", "9", owner["id"])
    commands = CommandServer(tmp_path / "server.db", CommandHandoff({device: (1, b"credential")}))
    command = commands.queue(router.route("telegram", "9", device, "status"))
    commands.poll(device)
    commands.acknowledge(device, command.request_id, "armed")
    service = OfficialBotService("telegram", FailingReplyProvider([]), ProviderUpdateAdapter(router), commands)

    for _ in range(3):
        service.run_once()

    assert commands.completed_replies("telegram") == []
