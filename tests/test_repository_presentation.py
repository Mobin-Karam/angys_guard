from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
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
    assert "# AngysGuard" in text
    assert "Angel of System Guard" in text
    assert "docs/assets/laptop-guard-overview.svg" in text


def test_root_readme_retains_core_repository_sections() -> None:
    text = README.read_text(encoding="utf-8")
    required_sections = (
        "## What is AngysGuard?",
        "## Project status",
        "## Which OS can I use today?",
        "## How can I control AngysGuard?",
        "## Self-hosted Bale / Telegram bot mode",
        "## Future managed AngysGuard bot/service",
        "## What AngysGuard can do",
        "## How it works",
        "## Quick start — Linux today",
        "## Future platform and app targets",
        "## Request another OS or platform",
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


def test_readme_keeps_current_and_future_support_separate() -> None:
    text = README.read_text(encoding="utf-8")
    assert "Ubuntu Desktop 24.04 LTS (amd64)" in text
    assert "v12.0 primary qualification target" in text
    assert "Ubuntu 22.04 / 26.04 LTS" in text
    assert "Windows" in text and "Planned" in text
    assert "Android companion" in text
    assert "These are roadmap targets, **not current support claims**" in text
    assert "must never be sent to Bale, Telegram" in text


def test_repository_profile_is_complete_and_safe_for_github_about() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    description = profile["description"].strip()
    topics = profile["topics"]

    assert description
    assert "AngysGuard" in description
    assert len(description) <= 350
    assert 1 <= len(topics) <= 20
    assert len(topics) == len(set(topics))
    assert {"angysguard", "linux", "security", "python", "laptop-security"} <= set(topics)
    assert profile["readme_source"] == "README.md"
    assert profile["version_source"] == "pyproject.toml"
    assert profile["maintenance_guide"] == "docs/README_MAINTENANCE.md"
    assert (ROOT / profile["social_preview_source"]).is_file()


def test_repository_profile_sync_helper_is_safe_read_only_preview() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    script = ROOT / "scripts" / "sync_repository_profile.py"
    result = subprocess.run(
        [sys.executable, str(script), "--repo", "Mobin-Karam/laptop_guard_v3"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=5,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Read-only preview" in result.stdout
    assert profile["description"] in result.stdout
    assert "Mobin-Karam/laptop_guard_v3" in result.stdout


def test_presentation_and_product_maintenance_workflows_are_wired() -> None:
    required_paths = (
        ROOT / "docs" / "README_MAINTENANCE.md",
        ROOT / "docs" / "ANGYSGUARD_PRODUCT_VISION.md",
        ROOT / "docs" / "PLATFORM_SUPPORT.md",
        ROOT / "docs" / "CONTROL_MODES.md",
        ROOT / ".agents" / "skills" / "repository-presentation" / "SKILL.md",
        ROOT / ".agents" / "skills" / "product-roadmap-maintenance" / "SKILL.md",
        ROOT / ".codex" / "agents" / "repository_curator.toml",
        ROOT / ".codex" / "agents" / "product_planner.toml",
        ROOT / ".github" / "prompts" / "refresh-repository-presentation.prompt.md",
        ROOT / ".github" / "prompts" / "update-product-roadmap.prompt.md",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "platform_request.yml",
    )
    for path in required_paths:
        assert path.is_file(), f"missing presentation/product-maintenance surface: {path}"

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for marker in (
        "README_MAINTENANCE.md",
        "repository-presentation",
        "repository_curator",
        "product-roadmap-maintenance",
        "product_planner",
        "PLATFORM_SUPPORT.md",
        "CONTROL_MODES.md",
    ):
        assert marker in agents


def test_future_security_model_rejects_os_password_over_remote_surfaces() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / "docs" / "CONTROL_MODES.md",
            ROOT / "docs" / "ANGYSGUARD_PRODUCT_VISION.md",
            ROOT / "docs" / "adr" / "0007-passwordless-device-pairing.md",
            ROOT / "AGENTS.md",
        )
    ).lower()
    assert "os password" in combined or "operating-system password" in combined
    assert "never" in combined
    assert "device-scoped" in combined


def test_passwordless_pairing_adr_is_accepted_and_requires_replay_safe_actions() -> None:
    adr = (ROOT / "docs" / "adr" / "0007-passwordless-device-pairing.md").read_text(encoding="utf-8")
    assert "- Status: Accepted" in adr
    for requirement in ("single-use", "revocable", "replay", "local privilege", "OS password"):
        assert requirement.lower() in adr.lower()


def test_managed_onboarding_protocol_keeps_managed_control_planned() -> None:
    protocol = (ROOT / "docs" / "MANAGED_ONBOARDING_PROTOCOL.md").read_text(encoding="utf-8")
    assert "planned architecture" in protocol
    for requirement in ("single-use", "revocation", "service-signed", "self-hosted", "OS password"):
        assert requirement.lower() in protocol.lower()


def test_release_pr_and_runtime_workflows_keep_presentation_trigger() -> None:
    surfaces = {
        ROOT / ".codex" / "agents" / "release_manager.toml": "PLATFORM_SUPPORT.md",
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
