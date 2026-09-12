from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from threading import RLock

from .config import STATE_PATH, ensure_dirs


@dataclass
class RuntimeState:
    armed: bool = False
    grace_until: float = 0.0
    arm_ready_at: float = 0.0
    last_input_alert: float = 0.0
    last_motion_alert: float = 0.0
    last_input_kind: str = ""
    camera_ok: bool = False
    input_ok: bool = False
    audio_recording: bool = False
    bot_online: bool = False
    last_bot_ok: float = 0.0
    last_event_id: int = 0

    def active(self) -> bool:
        now = time.time()
        return self.armed and now >= self.arm_ready_at and now >= self.grace_until


class RuntimeStateStore:
    def __init__(self, path: Path = STATE_PATH) -> None:
        ensure_dirs()
        self.path = path
        self.lock = RLock()
        self._state = self._load()

    def _load(self) -> RuntimeState:
        if not self.path.exists():
            return RuntimeState()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            allowed = RuntimeState.__dataclass_fields__.keys()
            return RuntimeState(**{k: raw[k] for k in raw if k in allowed})
        except Exception:
            return RuntimeState()

    def get(self) -> RuntimeState:
        with self.lock:
            return RuntimeState(**asdict(self._state))

    def mutate(self, **changes) -> RuntimeState:
        with self.lock:
            for key, value in changes.items():
                if hasattr(self._state, key):
                    setattr(self._state, key, value)
            self._save()
            return self.get()

    def refresh(self) -> RuntimeState:
        with self.lock:
            self._state = self._load()
            return self.get()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(self._state), indent=2), encoding="utf-8")
        tmp.replace(self.path)
