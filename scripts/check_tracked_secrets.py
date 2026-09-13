#!/usr/bin/env python3
"""Reject tracked local-secret filenames without reading their contents."""

from __future__ import annotations

import subprocess
from pathlib import PurePosixPath


BLOCKED_NAMES = {
    ".netrc",
    ".npmrc",
    ".pypirc",
    "credentials.json",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "id_rsa",
    "secrets.json",
    "stop-pin.json",
}
BLOCKED_SUFFIXES = {
    ".jks",
    ".key",
    ".p12",
    ".pem",
    ".pfx",
    ".ppk",
    ".secret",
    ".secrets",
}


def is_blocked_path(raw_path: str) -> bool:
    path = PurePosixPath(raw_path)
    name = path.name.lower()
    if name == ".env.example":
        return False
    return (
        name == ".env"
        or name.startswith(".env.")
        or name in BLOCKED_NAMES
        or path.suffix.lower() in BLOCKED_SUFFIXES
    )


def tracked_paths() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [
        item.decode("utf-8", errors="surrogateescape")
        for item in result.stdout.split(b"\0")
        if item
    ]


def main() -> int:
    blocked = sorted(path for path in tracked_paths() if is_blocked_path(path))
    if not blocked:
        return 0
    print("Blocked secret/local files are tracked:")
    print("\n".join(blocked))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
