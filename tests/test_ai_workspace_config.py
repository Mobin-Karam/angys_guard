from __future__ import annotations

import json
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"
SKILLS = ROOT / ".agents" / "skills"


def load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def test_codex_config_references_existing_custom_agents() -> None:
    config = load_toml(CODEX / "config.toml")
    agents = config["agents"]
    assert agents["enabled"] is True
    for name, value in agents.items():
        if not isinstance(value, dict):
            continue
        config_file = value.get("config_file")
        if not config_file:
            continue
        path = CODEX / config_file
        assert path.is_file(), f"missing config for {name}: {path}"
        agent = load_toml(path)
        assert agent["name"] == name
        assert agent["description"].strip()
        assert agent["developer_instructions"].strip()


def test_codex_hooks_json_is_valid_and_uses_local_handlers() -> None:
    hooks = json.loads((CODEX / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    assert {"SessionStart", "PreToolUse", "PostToolUse"} <= hooks.keys()
    for groups in hooks.values():
        for group in groups:
            for handler in group["hooks"]:
                assert handler["type"] == "command"
                command = handler["command"]
                assert "$(git rev-parse --show-toplevel)/.codex/hooks/" in command


def test_project_skills_have_required_frontmatter() -> None:
    expected = {
        "issue-to-pr",
        "safe-implementation",
        "security-review",
        "test-and-verify",
        "release-readiness",
    }
    found: set[str] = set()
    for skill_file in SKILLS.glob("*/SKILL.md"):
        text = skill_file.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        frontmatter = text.split("---\n", 2)[1]
        name_line = next(line for line in frontmatter.splitlines() if line.startswith("name:"))
        description_line = next(
            line for line in frontmatter.splitlines() if line.startswith("description:")
        )
        name = name_line.partition(":")[2].strip()
        assert description_line.partition(":")[2].strip()
        found.add(name)
    assert expected <= found
