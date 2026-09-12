from __future__ import annotations

import hashlib
import hmac
import json
import os
import select
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .config import CONFIG_DIR

STOP_PIN_PATH = CONFIG_DIR / "stop-pin.json"


@dataclass(slots=True)
class PinCheck:
    ok: bool
    reason: str = ""


class StopPinStore:
    """Persistent local shutdown PIN verifier.

    The plaintext PIN is never stored. The Bale owner sets it once and only a
    salted scrypt hash is kept on disk with user-only permissions.
    """

    def __init__(self, path: Path = STOP_PIN_PATH) -> None:
        self.path = Path(path)

    @property
    def configured(self) -> bool:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return bool(data.get("salt") and data.get("digest"))
        except (OSError, ValueError, TypeError):
            return False

    @staticmethod
    def validate_pin(pin: str) -> PinCheck:
        value = str(pin or "").strip()
        if not value.isdigit():
            return PinCheck(False, "PIN must contain digits only.")
        if not 4 <= len(value) <= 10:
            return PinCheck(False, "PIN must be 4 to 10 digits.")
        return PinCheck(True)

    @staticmethod
    def _derive(pin: str, salt: bytes) -> bytes:
        return hashlib.scrypt(
            pin.encode("utf-8"),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
            dklen=32,
        )

    def set_pin(self, pin: str) -> PinCheck:
        check = self.validate_pin(pin)
        if not check.ok:
            return check
        salt = os.urandom(16)
        digest = self._derive(pin.strip(), salt)
        payload = {
            "version": 1,
            "algorithm": "scrypt",
            "salt": salt.hex(),
            "digest": digest.hex(),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=".stop-pin-", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(tmp_name, 0o600)
            os.replace(tmp_name, self.path)
            try:
                os.chmod(self.path, 0o600)
            except OSError:
                pass
        finally:
            try:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
            except OSError:
                pass
        return PinCheck(True)

    def verify(self, pin: str) -> bool:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            salt = bytes.fromhex(str(data["salt"]))
            expected = bytes.fromhex(str(data["digest"]))
        except (OSError, ValueError, KeyError, TypeError):
            return False
        try:
            actual = self._derive(str(pin or "").strip(), salt)
        except Exception:
            return False
        return hmac.compare_digest(actual, expected)

    def clear(self) -> bool:
        try:
            self.path.unlink()
            return True
        except FileNotFoundError:
            return False
        except OSError:
            return False


def read_secret_with_timeout(prompt: str, timeout: int) -> str | None:
    """Read one hidden terminal line with a hard timeout.

    Returns None when no interactive TTY is available or the timeout expires.
    The function deliberately does not spawn a forever-blocked input() thread.
    """
    timeout = max(1, min(int(timeout), 120))
    if not getattr(sys.stdin, "isatty", lambda: False)():
        return None

    if os.name == "nt":
        try:
            import msvcrt
            import time

            sys.stdout.write(prompt)
            sys.stdout.flush()
            chars: list[str] = []
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    if ch in {"\r", "\n"}:
                        sys.stdout.write("\n")
                        sys.stdout.flush()
                        return "".join(chars).strip()
                    if ch == "\x08":
                        if chars:
                            chars.pop()
                        continue
                    if ch == "\x03":
                        return "cancel"
                    if ch.isprintable():
                        chars.append(ch)
                time.sleep(0.05)
            sys.stdout.write("\n")
            sys.stdout.flush()
            return None
        except Exception:
            return None

    try:
        import termios

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        new = termios.tcgetattr(fd)
        new[3] &= ~termios.ECHO
        sys.stdout.write(prompt)
        sys.stdout.flush()
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, new)
            ready, _, _ = select.select([sys.stdin], [], [], timeout)
            if not ready:
                return None
            return sys.stdin.readline().strip()
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            except Exception:
                pass
            sys.stdout.write("\n")
            sys.stdout.flush()
    except Exception:
        return None
