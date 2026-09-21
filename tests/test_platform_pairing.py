import pytest

from angys_platform.identity import PairingDenied, PairingService


def test_pairing_code_is_short_lived_and_single_use(tmp_path):
    pairing = PairingService(tmp_path / "pairing.db")
    code = pairing.start("device", now=100)
    assert pairing.consume(code, now=101) == "device"
    with pytest.raises(PairingDenied): pairing.consume(code, now=102)


def test_pairing_code_expires(tmp_path):
    pairing = PairingService(tmp_path / "pairing.db")
    code = pairing.start("device", now=100)
    with pytest.raises(PairingDenied): pairing.consume(code, now=401)
