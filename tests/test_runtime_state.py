import time

from laptop_guard.runtime_state import GuardRuntimeState
from laptop_guard.state import RuntimeStateStore


def test_guard_state_persists_assignments(tmp_path):
    path = tmp_path / "state.json"
    state = GuardRuntimeState(RuntimeStateStore(path))
    state.armed = True
    state.arm_ready_at = time.time() - 1
    assert RuntimeStateStore(path).get().armed is True
    assert state.active() is True


def test_guard_state_observes_external_cli_changes(tmp_path):
    path = tmp_path / "state.json"
    state = GuardRuntimeState(RuntimeStateStore(path))
    state.armed = True
    state.arm_ready_at = time.time() - 1
    RuntimeStateStore(path).mutate(armed=False)
    assert state.active() is False
