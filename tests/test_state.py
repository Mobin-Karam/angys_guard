from pathlib import Path

from laptop_guard.state import RuntimeStateStore


def test_state_roundtrip(tmp_path: Path):
    store = RuntimeStateStore(tmp_path / "state.json")
    store.mutate(armed=True, camera_ok=True)
    state = store.refresh()
    assert state.armed is True
    assert state.camera_ok is True
