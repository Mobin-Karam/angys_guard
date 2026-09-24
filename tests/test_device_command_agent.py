from angys_platform.agent import DeviceCommandAgent
from angys_platform.gateway import CommandHandoff, GatewayRouter
from angys_platform.identity import IdentityService
from angys_platform.protocol import DeviceProtocol
from angys_platform.server import CommandServer


def test_enrolled_agent_verifies_and_dispatches_fixed_command(tmp_path):
    identity = IdentityService(tmp_path / "identity.db")
    owner = identity.register("owner", "password")
    device = identity.register_device(owner["id"], "linux", "host")
    router = GatewayRouter(identity)
    router.link_provider_account("telegram", "owner", owner["id"])
    secret, observed = b"device-credential", []
    transport = CommandServer(tmp_path / "server.db", CommandHandoff({device: (1, secret)}))
    transport.queue(router.route("telegram", "owner", device, "lock"))
    agent = DeviceCommandAgent(transport, DeviceProtocol(device, owner["id"], 1, secret), {"lock": lambda: observed.append("lock")})
    assert agent.run_once() is True
    assert observed == ["lock"]
    assert agent.run_once() is False
