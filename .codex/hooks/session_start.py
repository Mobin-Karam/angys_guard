#!/usr/bin/env python3
from __future__ import annotations

import json
import sys


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:
        # Hooks should never break a session because of malformed optional input.
        pass

    message = (
        "Laptop Guard project rules are active. Read AGENTS.md and the closest "
        "nested AGENTS.md before editing. Never read or print .env/secrets.json, "
        "stop-PIN material, credentials, or captured evidence. Preserve owner "
        "authorization/privacy boundaries. Use project skills for issue work, "
        "security review, verification, and release readiness when relevant."
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": message,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
