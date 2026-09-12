from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ISSUE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"

REQUIRED_FORMS = {
    "bug_report.yml",
    "setup_installation.yml",
    "provider_bot.yml",
    "feature_request.yml",
    "ui_ux.yml",
    "platform_request.yml",
    "architecture_proposal.yml",
    "documentation.yml",
    "release_packaging.yml",
    "question.yml",
    "config.yml",
    "security-advisory.md",
}


def test_required_issue_forms_exist() -> None:
    present = {path.name for path in ISSUE_DIR.iterdir() if path.is_file()}
    missing = REQUIRED_FORMS - present
    assert not missing, f"missing required issue templates: {sorted(missing)}"


def test_issue_chooser_uses_current_repository_links() -> None:
    config = (ISSUE_DIR / "config.yml").read_text(encoding="utf-8")
    assert "Mobin-Karam/angys_guard" in config
    assert "Mobin-Karam/laptop_guard_v3" not in config
    assert "security/policy" in config
    assert "blank_issues_enabled: false" in config


def test_template_default_labels_are_declared() -> None:
    declared = {
        item["name"]
        for item in json.loads(
            (ROOT / ".github" / "repository-management" / "labels.json").read_text(
                encoding="utf-8"
            )
        )
    }

    unknown: dict[str, list[str]] = {}
    for path in ISSUE_DIR.glob("*.yml"):
        if path.name == "config.yml":
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^labels:\s*\n(?P<labels>(?:\s+-\s+[^\n]+\n)+)^body:", text, re.M)
        if not match:
            continue
        labels = [
            line.split("-", 1)[1].strip().strip('"\'')
            for line in match.group("labels").splitlines()
        ]
        missing = sorted(label for label in labels if label not in declared)
        if missing:
            unknown[path.name] = missing

    assert not unknown, f"issue forms reference undeclared labels: {unknown}"


def test_public_forms_contain_sensitive_data_guardrails() -> None:
    checked = [
        "bug_report.yml",
        "setup_installation.yml",
        "provider_bot.yml",
        "feature_request.yml",
        "question.yml",
    ]
    for name in checked:
        text = (ISSUE_DIR / name).read_text(encoding="utf-8").lower()
        assert "password" in text or "credential" in text or "token" in text, name
        assert "sensitive" in text or "private" in text, name


def test_private_security_reporting_guard_exists() -> None:
    text = (ISSUE_DIR / "security-advisory.md").read_text(encoding="utf-8").lower()
    assert "do not post" in text
    assert "security.md" in text
    assert "private" in text
