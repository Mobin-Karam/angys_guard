#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys


PATCH_FILE_RE = re.compile(r"^\*\*\*\s+(?:Add|Update|Delete) File:\s+(.+?)\s*$", re.M)
SECURITY_SENSITIVE = (
    "config",
    "secret",
    "auth",
    "stop_",
    "runtime_api",
    "provider",
    "bale_api",
    "telegram",
    "camera",
    "audio",
    "screen",
    "input",
    "service",
    "system",
    "warning",
    "api",
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = payload.get("tool_input") or {}
    command = str(tool_input.get("command") or "") if isinstance(tool_input, dict) else ""
    paths = [p.strip().replace("\\", "/") for p in PATCH_FILE_RE.findall(command)]
    runtime_paths = [p for p in paths if p.startswith("laptop_guard/")]
    if not runtime_paths:
        return 0

    lowered = "\n".join(runtime_paths).lower()
    sensitive = any(marker in lowered for marker in SECURITY_SENSITIVE)
    if sensitive:
        context = (
            "Security-sensitive Laptop Guard runtime code was edited. Before completion, "
            "run focused regression tests, then use the security-review workflow/agent and "
            "the applicable full checks from docs/TESTING.md."
        )
    else:
        context = (
            "Laptop Guard runtime code was edited. Add/run focused regression tests and "
            "finish with the applicable verification from docs/TESTING.md before completion."
        )

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": context,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
