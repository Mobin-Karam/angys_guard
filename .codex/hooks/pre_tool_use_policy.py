#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import PurePosixPath


DESTRUCTIVE_BASH_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bgit\s+reset\s+--hard\b", re.I), "git reset --hard can destroy unrelated work"),
    (re.compile(r"\bgit\s+clean\s+-[^\n;&|]*f", re.I), "git clean can delete untracked project files"),
    (re.compile(r"\bgit\s+(?:checkout|restore)\s+(?:--\s+)?\.\s*(?:$|[;&|])", re.I), "bulk checkout/restore can overwrite unrelated work"),
    (re.compile(r"\bgit\s+push\b[^\n]*(?:--force(?:-with-lease)?|\s-f(?:\s|$))", re.I), "force-pushing is not permitted by the project agent policy"),
    (re.compile(r"\brm\s+-(?=[^\s]*r)(?=[^\s]*f)[^\s]*\s+(?:/|\.|\.\.)\s*(?:$|[;&|])", re.I), "recursive deletion of /, . or .. is unsafe"),
)

SECRET_READ_RE = re.compile(
    r"\b(?:cat|head|tail|less|more|strings|xxd)\b[^\n;&|]*"
    r"(?:^|[\s'\"])(?:\.env(?!\.(?:example|sample))|"
    r"(?:~/?|/[^\s'\"]*/)?\.config/laptop-guard/secrets\.json|secrets\.json)(?:[\s'\"]|$)",
    re.I,
)

PATCH_FILE_RE = re.compile(r"^\*\*\*\s+(?:Add|Update|Delete) File:\s+(.+?)\s*$", re.M)
PROTECTED_BASENAMES = {".env", "secrets.json"}


def deny(reason: str) -> int:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


def protected_patch_target(command: str) -> str | None:
    for raw_path in PATCH_FILE_RE.findall(command):
        path = raw_path.strip().replace("\\", "/")
        if PurePosixPath(path).name in PROTECTED_BASENAMES:
            return path
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input") or {}
    command = str(tool_input.get("command") or "") if isinstance(tool_input, dict) else ""

    if tool_name == "Bash":
        for pattern, reason in DESTRUCTIVE_BASH_RULES:
            if pattern.search(command):
                return deny(reason)
        if SECRET_READ_RE.search(command):
            return deny("reading project/user secret files is prohibited; inspect schema/code instead")

    if tool_name in {"apply_patch", "Edit", "Write"}:
        protected = protected_patch_target(command)
        if protected:
            return deny(f"editing protected secret file {protected!r} is prohibited")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
