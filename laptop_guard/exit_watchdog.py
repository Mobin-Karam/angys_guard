from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from .system_actions import lock_screen


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _authorized_safe_exit(path: str, token: str) -> bool:
    if not path or not token:
        return False
    p = Path(path)
    try:
        value = p.read_text(encoding="utf-8").strip()
    except OSError:
        return False
    ok = value == token
    try:
        p.unlink()
    except OSError:
        pass
    return ok


def watch(
    parent_pid: int,
    interval: float = 0.25,
    safe_exit_file: str = "",
    safe_exit_token: str = "",
) -> int:
    """Lock when the guard disappears unless it completed owner-authorized exit.

    The separate watchdog covers abrupt exits such as terminal loss or SIGKILL.
    A normal, two-factor approved stop writes a one-time safe-exit token before
    the guard process ends; only then does the watchdog leave without locking.
    """
    interval = max(0.1, min(float(interval), 2.0))
    while _pid_alive(parent_pid):
        if os.name != "nt" and os.getppid() != parent_pid:
            break
        time.sleep(interval)

    time.sleep(0.05)
    if _authorized_safe_exit(safe_exit_file, safe_exit_token):
        return 0

    lock_screen()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-pid", type=int, required=True)
    parser.add_argument("--interval", type=float, default=0.25)
    parser.add_argument("--safe-exit-file", default="")
    parser.add_argument("--safe-exit-token", default="")
    args = parser.parse_args()
    return watch(
        args.parent_pid,
        args.interval,
        args.safe_exit_file,
        args.safe_exit_token,
    )


if __name__ == "__main__":
    raise SystemExit(main())
