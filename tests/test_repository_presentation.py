from __future__ import annotations

import json
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PROFILE = ROOT / ".github" / "repository-profile.json"


def load_pyproject() -> dict:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def test_root_readme_is_the_package_landing_page() -> None:
    project = load_pyproject()["project"]
    text = README.read_text(encoding="utf-8")

    assert project["readme"] == "README.md"
    assert project["version"] in text
    assert "docs/assets/laptop-guard-overview.svg" in text


def test_root_readme_retains_core_repository_sections() -> None:
    text = README.read_text(encoding="utf-8")
    required_sections = (
        "## What is Laptop Guard?",
        "## Project status",
        "## What Laptop Guard can do",
        "## How it works",
        "## Quick start",
        "## Repository map",
        "## Graphify-first engineering",
        "## Security and privacy boundaries",
        "## Testing and validation",
        "## Documentation",
        "## Roadmap",
        "## Contributing",
        "## Repository presentation maintenance",
        "## License",
    )
    for heading in required_sections:
        assert heading in text, f"missing README section: {heading}"


def test_repository_profile_is_complete_and_safe_for_github_about() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    description = profile["description"].strip()
    topics = profile["topics"]

    assert description
    assert len(description) <= 350
    assert 1 <= len(topics) <= 20
    assert len(topics) == len(set(topics))
    assert {"linux", "security", "python", "laptop-security"} <= set(topics)
    assert profile["readme_source"] == "README.md"
    assert profile["version_source"] == "pyproject.toml"
    assert profile["maintenance_guide"] == "docs/README_MAINTENANCE.md"
    assert (ROOT / profile["social_preview_source"]).is_file()


def test_presentation_maintenance_workflow_is_wired_for_agents() -> None:
    required_paths = (
        ROOT / "docs" / "README_MAINTENANCE.md",
        ROOT / ".agents" / "skills" / "repository-presentation" / "SKILL.md",
        ROOT / ".codex" / "agents" / "repository_curator.toml",
        ROOT / ".github" / "prompts" / "refresh-repository-presentation.prompt.md",
    )
    for path in required_paths:
        assert path.is_file(), f"missing presentation-maintenance surface: {path}"

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "README_MAINTENANCE.md" in agents
    assert "repository-presentation" in agents
    assert "repository_curator" in agents


def test_release_pr_and_runtime_workflows_keep_presentation_trigger() -> None:
    surfaces = {
        ROOT / ".codex" / "agents" / "release_manager.toml": "repository-presentation",
        ROOT / ".agents" / "skills" / "release-readiness" / "SKILL.md": "repository-presentation",
        ROOT / ".agents" / "skills" / "safe-implementation" / "SKILL.md": "README_MAINTENANCE.md",
        ROOT / ".agents" / "skills" / "issue-to-pr" / "SKILL.md": "repository-presentation",
        ROOT / ".github" / "pull_request_template.md": "test_repository_presentation.py",
        ROOT / "docs" / "MAINTAINER_CHECKLIST.md": "repository-presentation",
        ROOT / ".codex" / "hooks" / "post_edit_review.py": "README_MAINTENANCE.md",
    }
    for path, marker in surfaces.items():
        text = path.read_text(encoding="utf-8")
        assert marker in text, f"presentation trigger missing from {path}: {marker}"


def test_graphify_generated_assets_do_not_dominate_language_stats() -> None:
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "graphify-out/graph.html linguist-generated=true" in attributes
    assert "graphify-out/graph.json linguist-generated=true" in attributes
