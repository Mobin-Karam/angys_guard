#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def _run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=3,
        check=False,
    )


def _graph_status(root: Path) -> str:
    report = root / "graphify-out" / "GRAPH_REPORT.md"
    if not report.exists():
        return "Graphify graph missing: build it before broad repository discovery."

    try:
        text = report.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "Graphify freshness unknown: GRAPH_REPORT.md could not be read."

    match = re.search(r"Built from commit:\s*`?([0-9a-fA-F]{7,40})`?", text)
    if not match:
        return "Graphify freshness unknown: build commit is not recorded in GRAPH_REPORT.md."

    built = match.group(1)
    head_proc = _run(root, "rev-parse", "--short", "HEAD")
    if head_proc.returncode != 0:
        return f"Graphify build={built[:8]}; current HEAD unavailable."
    head = head_proc.stdout.strip()

    if head.startswith(built) or built.startswith(head):
        return f"Graphify appears fresh at {built[:8]}."

    ancestor = _run(root, "merge-base", "--is-ancestor", built, "HEAD")
    if ancestor.returncode != 0:
        return f"Graphify is stale/unrelated (build {built[:8]}, HEAD {head}); refresh before discovery."

    diff = _run(
        root,
        "diff",
        "--name-only",
        f"{built}..HEAD",
        "--",
        ".",
        ":(exclude)graphify-out/**",
    )
    if diff.returncode == 0 and not diff.stdout.strip():
        return f"Graphify is fresh for repository content (build {built[:8]}, HEAD {head}; only graph outputs changed)."

    return f"Graphify is stale (build {built[:8]}, HEAD {head}); run `graphify update .` before broad discovery."


def main() -> int:
    try:
        json.load(sys.stdin)
    except Exception:
        # Hooks should never break a session because of malformed optional input.
        pass

    root_proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=3,
        check=False,
    )
    root = Path(root_proc.stdout.strip()) if root_proc.returncode == 0 else Path.cwd()
    graph_status = _graph_status(root)

    message = (
        "Laptop Guard rules are active. Read AGENTS.md and the closest nested "
        "AGENTS.md. Repository discovery is Graphify-first: check freshness, use "
        "graphify query/explain/path, then read only minimal authoritative files; "
        "never load raw graph.json. "
        + graph_status
        + " Never read/print .env, secrets.json, stop-PIN material, credentials, "
        "or captured evidence. Preserve owner authorization/privacy boundaries."
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
