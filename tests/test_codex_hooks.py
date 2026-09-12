from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / ".codex" / "hooks"


def run_hook(name: str, payload: dict) -> tuple[int, dict | None, str]:
    result = subprocess.run(
        [sys.executable, str(HOOKS / name)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=5,
        check=False,
    )
    parsed = json.loads(result.stdout) if result.stdout.strip() else None
    return result.returncode, parsed, result.stderr


def test_pre_tool_hook_blocks_destructive_git() -> None:
    code, output, _ = run_hook(
        "pre_tool_use_policy.py",
        {"tool_name": "Bash", "tool_input": {"command": "git reset --hard HEAD"}},
    )
    assert code == 0
    assert output is not None
    decision = output["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "reset" in decision["permissionDecisionReason"]


def test_pre_tool_hook_allows_safe_git_status() -> None:
    code, output, stderr = run_hook(
        "pre_tool_use_policy.py",
        {"tool_name": "Bash", "tool_input": {"command": "git status --short"}},
    )
    assert code == 0
    assert output is None
    assert stderr == ""


def test_pre_tool_hook_blocks_patch_to_env() -> None:
    patch = "*** Begin Patch\n*** Update File: .env\n@@\n-old\n+new\n*** End Patch\n"
    code, output, _ = run_hook(
        "pre_tool_use_policy.py",
        {"tool_name": "apply_patch", "tool_input": {"command": patch}},
    )
    assert code == 0
    assert output is not None
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_session_start_adds_project_context() -> None:
    code, output, _ = run_hook("session_start.py", {"hook_event_name": "SessionStart"})
    assert code == 0
    assert output is not None
    context = output["hookSpecificOutput"]["additionalContext"]
    assert "AGENTS.md" in context
    assert "secrets.json" in context


def test_post_edit_escalates_sensitive_runtime_change() -> None:
    patch = "*** Begin Patch\n*** Update File: laptop_guard/runtime_api.py\n@@\n-x\n+y\n*** End Patch\n"
    code, output, _ = run_hook(
        "post_edit_review.py",
        {"tool_input": {"command": patch}},
    )
    assert code == 0
    assert output is not None
    context = output["hookSpecificOutput"]["additionalContext"]
    assert "Security-sensitive" in context
    assert "security-review" in context
