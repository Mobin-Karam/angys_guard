from __future__ import annotations

import time

from .state import RuntimeState, RuntimeStateStore


class GuardRuntimeState:
    """Live facade over the shared persisted runtime state.

    Assignments are immediately persisted. `active()` refreshes owner-controlled
    fields so CLI arm/disarm/grace changes are observed by a running guard.
    """

    _CONTROL_FIELDS = ("armed", "grace_until", "arm_ready_at")

    def __init__(self, store: RuntimeStateStore | None = None) -> None:
        object.__setattr__(self, "store", store or RuntimeStateStore())
        object.__setattr__(self, "_state", self.store.refresh())

    def __getattr__(self, name: str):
        state = object.__getattribute__(self, "_state")
        if name in RuntimeState.__dataclass_fields__:
            return getattr(state, name)
        raise AttributeError(name)

    def __setattr__(self, name: str, value) -> None:
        if name not in RuntimeState.__dataclass_fields__:
            object.__setattr__(self, name, value)
            return
        state = object.__getattribute__(self, "_state")
        setattr(state, name, value)
        self.store.mutate(**{name: value})

    def refresh(self) -> RuntimeState:
        fresh = self.store.refresh()
        object.__setattr__(self, "_state", fresh)
        return fresh

    def mutate(self, **changes) -> RuntimeState:
        allowed = RuntimeState.__dataclass_fields__
        clean = {name: value for name, value in changes.items() if name in allowed}
        if not clean:
            return object.__getattribute__(self, "_state")
        fresh = self.store.mutate(**clean)
        object.__setattr__(self, "_state", fresh)
        return fresh

    def active(self) -> bool:
        fresh = self.store.refresh()
        state = object.__getattribute__(self, "_state")
        for name in self._CONTROL_FIELDS:
            setattr(state, name, getattr(fresh, name))
        now = time.time()
        return state.armed and now >= state.arm_ready_at and now >= state.grace_until
