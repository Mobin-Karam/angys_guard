from __future__ import annotations

import argparse
import os
import time

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


def watch(parent_pid: int, interval: float = 0.25) -> int:
    """Lock the normal desktop session when the guard process disappears.

    This is intentionally a separate process so SIGKILL, terminal closure or a
    crash of the main guard still leaves a chance to issue the OS lock request.
    """
    interval = max(0.1, min(float(interval), 2.0))
    while _pid_alive(parent_pid):
        # On POSIX the child's PPID changes as soon as its parent disappears;
        # checking both PID liveness and parentage also avoids a rare PID-reuse race.
        if os.name != "nt" and os.getppid() != parent_pid:
            break
        time.sleep(interval)
    # Small delay lets a terminating process complete its own direct lock first.
    time.sleep(0.05)
    lock_screen()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-pid", type=int, required=True)
    parser.add_argument("--interval", type=float, default=0.25)
    args = parser.parse_args()
    return watch(args.parent_pid, args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
