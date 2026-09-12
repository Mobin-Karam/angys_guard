from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable

from .config import DATA_DIR
from .text_direction import resolve_direction

CHAT_DIR = DATA_DIR / "security_chat"
INBOX = CHAT_DIR / "inbox.jsonl"
OUTBOX = CHAT_DIR / "outbox.jsonl"
MIRROR = CHAT_DIR / "security-chat.txt"
STATE = CHAT_DIR / "state.json"


def _append(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
        fh.flush()


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(path)


class SecurityChatManager:
    """Visible local chat. Only text entered in its reply box is transmitted."""

    def __init__(self, visitor_callback: Callable[[str], None] | None = None) -> None:
        CHAT_DIR.mkdir(parents=True, exist_ok=True)
        INBOX.touch(exist_ok=True)
        OUTBOX.touch(exist_ok=True)
        self.visitor_callback = visitor_callback
        self._proc: subprocess.Popen | None = None
        self._poll_thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._outbox_pos = OUTBOX.stat().st_size
        self._lock = threading.RLock()
        self.session_id = ""
        self.history: list[tuple[str, str, str]] = []
        self.direction = "auto"

    @property
    def active(self) -> bool:
        return bool(self._proc and self._proc.poll() is None)

    def _resolved_direction(self, text: str) -> str:
        return resolve_direction(text, self.direction, "rtl")

    def _write_mirror(self) -> None:
        # Keep the mirror in logical Unicode order. Modern editors will apply
        # BiDi themselves, and the content stays searchable/copyable correctly.
        labels = {
            "owner": "مالک / Owner",
            "visitor": "کاربر لپ‌تاپ / Local user",
            "system": "سیستم / System",
        }
        lines = ["LAPTOP GUARD — SECURITY CHAT", "=" * 52, ""]
        for ts, role, text in self.history[-150:]:
            direction = self._resolved_direction(text)
            lines.extend(
                [
                    f"[{ts}] {labels.get(role, role)} [{direction.upper()}]:",
                    text,
                    "",
                ]
            )
        _atomic_text(MIRROR, "\n".join(lines))

    def _message(
        self,
        role: str,
        text: str,
        seconds: int | None = None,
        *,
        kind: str = "message",
    ) -> dict:
        clean = str(text).strip()[:8000]
        payload = {
            "id": uuid.uuid4().hex,
            "session_id": self.session_id,
            "time": datetime.now().strftime("%H:%M:%S"),
            "role": role,
            "kind": kind,
            # IMPORTANT: send/store logical Unicode, never visual/reversed text.
            "text": clean,
            "direction": self._resolved_direction(clean),
        }
        if seconds is not None:
            payload["seconds"] = int(seconds)
        return payload

    def _send(self, role: str, text: str, seconds: int | None = None) -> None:
        clean = str(text).strip()
        if not clean:
            return
        payload = self._message(role, clean, seconds)
        _append(INBOX, payload)
        with self._lock:
            self.history.append((payload["time"], role, clean))
            self._write_mirror()

    def send_owner(self, text: str, seconds: int | None = None) -> None:
        self._send("owner", text, seconds)

    def send_system(self, text: str, seconds: int | None = None) -> None:
        self._send("system", text, seconds)

    def start(
        self,
        initial_text: str,
        seconds: int = 120,
        allow_reply: bool = True,
        direction: str = "auto",
        **_: object,
    ) -> bool:
        seconds = max(15, min(int(seconds), 3600))
        self.direction = direction if direction in {"auto", "rtl", "ltr"} else "auto"

        if not self.active:
            self.session_id = uuid.uuid4().hex
            INBOX.write_text("", encoding="utf-8")
            OUTBOX.write_text("", encoding="utf-8")
            self._outbox_pos = 0
            self.history = []
            _atomic_text(
                STATE,
                json.dumps(
                    {
                        "session_id": self.session_id,
                        "seconds": seconds,
                        "allow_reply": bool(allow_reply),
                        "direction": self.direction,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            )

            # Write before launch so the first Persian/Arabic message is not lost.
            self.send_system(initial_text, seconds)
            try:
                self._proc = subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "laptop_guard.chat_window",
                        "--seconds",
                        str(seconds),
                        "--allow-reply",
                        "1" if allow_reply else "0",
                        "--session-id",
                        self.session_id,
                        "--direction",
                        self.direction,
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(0.12)
                if self._proc.poll() is not None:
                    self._proc = None
            except OSError:
                self._proc = None
        else:
            self.send_system(initial_text, seconds)

        self._ensure_poller()
        return self.active

    def dismiss(self) -> bool:
        proc = self._proc
        if proc and proc.poll() is None:
            try:
                _append(INBOX, self._message("system", "close", kind="control"))
            except OSError:
                pass
            try:
                proc.wait(timeout=0.8)
            except subprocess.TimeoutExpired:
                try:
                    proc.terminate()
                except OSError:
                    pass
            self._proc = None
            return True

        self._proc = None
        return False

    def _ensure_poller(self) -> None:
        if self._poll_thread and self._poll_thread.is_alive():
            return
        self._stop.clear()
        self._poll_thread = threading.Thread(
            target=self._poll_outbox,
            daemon=True,
            name="guard-chat-outbox",
        )
        self._poll_thread.start()

    def _poll_outbox(self) -> None:
        while not self._stop.wait(0.25):
            try:
                size = OUTBOX.stat().st_size
                if size < self._outbox_pos:
                    self._outbox_pos = 0
                if size == self._outbox_pos:
                    continue

                with OUTBOX.open("r", encoding="utf-8") as fh:
                    fh.seek(self._outbox_pos)
                    data = fh.read()
                    self._outbox_pos = fh.tell()

                for line in data.splitlines():
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    item_session = item.get("session_id")
                    # Backward compatibility: older local writers did not add a
                    # session_id. If one is present it must match this session.
                    if item_session not in (None, "") and item_session != self.session_id:
                        continue

                    text = str(item.get("text") or "").strip()
                    if not text:
                        continue

                    ts = str(item.get("time") or datetime.now().strftime("%H:%M:%S"))
                    with self._lock:
                        self.history.append((ts, "visitor", text))
                        self._write_mirror()

                    if self.visitor_callback:
                        try:
                            self.visitor_callback(text)
                        except Exception:
                            pass
            except OSError:
                pass

    def stop(self) -> None:
        self._stop.set()
        self.dismiss()
        if self._poll_thread and self._poll_thread.is_alive():
            self._poll_thread.join(timeout=1.0)
