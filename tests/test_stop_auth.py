from pathlib import Path

from laptop_guard.stop_auth import StopPinStore
from laptop_guard.exit_watchdog import _authorized_safe_exit


def test_stop_pin_is_hashed_and_verifies(tmp_path):
    path = tmp_path / "stop-pin.json"
    store = StopPinStore(path)
    result = store.set_pin("482915")
    assert result.ok is True
    assert store.configured is True
    raw = path.read_text(encoding="utf-8")
    assert "482915" not in raw
    assert store.verify("482915") is True
    assert store.verify("482916") is False


def test_stop_pin_validation(tmp_path):
    store = StopPinStore(tmp_path / "pin.json")
    assert store.set_pin("12").ok is False
    assert store.set_pin("abcd").ok is False
    assert store.set_pin("1234").ok is True


def test_safe_exit_token_is_one_time(tmp_path):
    path = tmp_path / "safe.token"
    path.write_text("secret", encoding="utf-8")
    assert _authorized_safe_exit(str(path), "secret") is True
    assert path.exists() is False
    assert _authorized_safe_exit(str(path), "secret") is False
