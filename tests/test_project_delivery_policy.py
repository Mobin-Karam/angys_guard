from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLUEPRINT = ROOT / ".github" / "repository-management" / "project-v2.json"
ISSUES = ROOT / ".github" / "repository-management" / "issues.json"
MILESTONES = ROOT / ".github" / "repository-management" / "milestones.json"
BOOTSTRAP = ROOT / "scripts" / "bootstrap_github_project.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "project-v2-bootstrap.yml"
PROJECT_DOC = ROOT / "docs" / "PROJECT_MANAGEMENT.md"
RENAME_DOC = ROOT / "docs" / "REPOSITORY_RENAME_AND_PROJECTS.md"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_project_blueprint_uses_live_and_target_repository_names() -> None:
    blueprint = _json(BLUEPRINT)

    assert blueprint["title"] == "AngysGuard — Product, Platform & Architecture Delivery"
    assert blueprint["owner"] == "Mobin-Karam"
    assert blueprint["repository_current"] == "Mobin-Karam/angys_guard"
    assert blueprint["repository_target"] == "Mobin-Karam/angysguard"


def test_every_managed_delivery_issue_is_grouped_once() -> None:
    blueprint = _json(BLUEPRINT)
    managed = {int(number) for number in _json(ISSUES)}
    grouped = [
        int(number)
        for numbers in blueprint["milestone_issue_groups"].values()
        for number in numbers
    ]

    assert len(grouped) == len(set(grouped))
    assert set(grouped) == managed
    assert blueprint["milestone_issue_groups"]["project"] == [9]


def test_blueprint_groups_match_repository_milestones() -> None:
    blueprint = _json(BLUEPRINT)
    issues = _json(ISSUES)
    milestones = {item["title"] for item in _json(MILESTONES)}
    target_to_milestone = {
        "v11.2": "v11.2 — Setup & Security Hardening",
        "v11.3": "v11.3 — Non-Technical UX",
        "v12.0": "v12.0 — Production-Ready Release",
        "v13.0": "v13.0 — AngysGuard Self-Hosted UX & Linux App",
        "v14.0": "v14.0 — AngysGuard Managed Control",
        "Future Platform Expansion": "Future Platform Expansion — Windows & Android",
        "Architecture Evolution": "Architecture Evolution — Modular Monolith",
    }

    for target, numbers in blueprint["milestone_issue_groups"].items():
        if target == "project":
            assert numbers == [9]
            assert issues["9"]["milestone"] is None
            assert "project" in issues["9"]["labels"]
            continue

        milestone = target_to_milestone[target]
        assert milestone in milestones
        for number in numbers:
            assert issues[str(number)]["milestone"] == milestone


def test_project_bootstrap_syncs_only_stable_status_states() -> None:
    script = BOOTSTRAP.read_text(encoding="utf-8")
    blueprint = _json(BLUEPRINT)

    assert "--json url,labels,state" in script
    assert 'set_status_if_available "$url" "Done"' in script
    assert 'set_status_if_available "$url" "Validation"' in script
    assert 'select(.name == "Status")' in script
    assert 'select(.name == $value)' in script
    assert 'set_field "$url" "Blocked" "$blocked"' in script
    assert blueprint["status_policy"]["closed"] == "Done"
    assert blueprint["status_policy"]["needs_validation"] == "Validation"
    assert "preserve existing project Status" in blueprint["status_policy"]["other_open"]

    # Rerunning synchronization must not flatten active human workflow states.
    assert 'set_field "$url" "Status" "Backlog"' not in script
    assert 'set_field "$url" "Status" "Ready"' not in script
    assert 'set_field "$url" "Status" "In progress"' not in script
    assert 'set_field "$url" "Status" "Review"' not in script


def test_project_workflow_keeps_elevated_token_manual_and_scoped() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in text
    assert "ANGYSGUARD_PROJECT_TOKEN" in text
    assert "scripts/bootstrap_github_project.sh" in text
    assert "pull_request:" not in text
    assert "push:" not in text


def test_umbrella_tracker_is_documented_as_long_lived() -> None:
    project = PROJECT_DOC.read_text(encoding="utf-8")
    rename = RENAME_DOC.read_text(encoding="utf-8")

    assert "Issue #9 is intentionally a long-lived project tracker" in project
    assert "Closes #9" in project
    assert "closed issue" in project and "Status = Done" in project
    assert "warns and preserves the current Status" in project
    assert "status:needs-validation" in project
    assert "Status = Validation" in project

    assert "Mobin-Karam/angys_guard" in rename
    assert "Mobin-Karam/laptop_guard_v3" not in rename
    assert "preserves other open Project Status values" in rename
