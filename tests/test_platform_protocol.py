import pytest

from angys_platform.protocol import CommandEnvelope, DeviceProtocol, ProtocolDenied


def test_device_accepts_one_signed_scoped_fixed_command():
    secret = b"test-device-credential"
    command = CommandEnvelope.issue(secret, "device", 7, "reboot", 2, "request-1", 110, 100)
    assert DeviceProtocol("device", 7, 2, secret).accept(command, now=105).action == "reboot"


@pytest.mark.parametrize("action", ["shell", "shutdown; rm -rf /", ""])
def test_device_rejects_non_fixed_actions(action):
    secret = b"test-device-credential"
    command = CommandEnvelope.issue(secret, "device", 7, action, 2, "request", 110, 100)
    with pytest.raises(ProtocolDenied):
        DeviceProtocol("device", 7, 2, secret).accept(command, now=105)


def test_device_rejects_replay_expiry_wrong_scope_and_tampering(tmp_path):
    secret = b"test-device-credential"
    cache = str(tmp_path / "protocol.db")
    device = DeviceProtocol("device", 7, 2, secret, cache)
    command = CommandEnvelope.issue(secret, "device", 7, "status", 2, "request", 110, 100)
    device.accept(command, now=105)
    with pytest.raises(ProtocolDenied): device.accept(command, now=105)
    with pytest.raises(ProtocolDenied):
        DeviceProtocol("device", 7, 2, secret, cache).accept(command, now=105)
    with pytest.raises(ProtocolDenied): device.accept(command, now=111)
    wrong = CommandEnvelope.issue(secret, "other", 7, "status", 2, "other", 110, 100)
    with pytest.raises(ProtocolDenied): device.accept(wrong, now=105)
    forged = CommandEnvelope.issue(b"wrong", "device", 7, "status", 2, "forged", 110, 100)
    with pytest.raises(ProtocolDenied): device.accept(forged, now=105)
