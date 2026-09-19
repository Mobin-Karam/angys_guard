from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLATFORM = ROOT / "docs" / "PLATFORM_SUPPORT.md"
CHECKLIST = ROOT / "docs" / "RELEASE_CHECKLIST.md"
DOCS_INDEX = ROOT / "docs" / "README.md"
TESTING = ROOT / "docs" / "TESTING.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
BUG_FORM = ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml"


def test_v12_support_matrix_is_explicit_and_bounded() -> None:
    text = PLATFORM.read_text(encoding="utf-8")

    assert "Ubuntu Desktop 24.04 LTS" in text
    assert "Ubuntu Desktop 22.04 LTS" in text
    assert "Ubuntu Desktop 26.04 LTS" in text
    assert "amd64" in text
    assert "Python 3.11" in text
    assert "3.12" in text
    assert "3.13" in text
    assert "GNOME X11" in text
    assert "GNOME Wayland" in text
    assert "evdev" in text
    assert "pynput" in text
    assert "wf-recorder" in text
    assert "ffmpeg" in text
    assert "configured-feature" in text.lower()


def test_release_checklist_covers_required_release_surfaces() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    required = [
        "./install.sh",
        "./run.sh setup",
        "./run.sh doctor",
        "./run.sh test bot",
        "./run.sh test camera",
        "./run.sh test microphone",
        "./run.sh test input",
        "./run.sh test screen",
        "./run.sh test lock",
        "./run.sh service install",
        "./run.sh autostart",
        "offline queue",
        "Update and rollback",
        "Release gate",
        "repository-safety",
        "No unresolved P0",
    ]
    for item in required:
        assert item.lower() in text.lower()


def test_bug_report_instructions_protect_secrets_and_private_evidence() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")

    assert "runtime-diagnostics.jsonl" in text
    assert "not guaranteed to be free of personal metadata" in text
    assert "Never attach or paste" in text
    assert "secrets.json" in text
    assert "stop-pin.json" in text
    assert "OS passwords" in text
    assert "private evidence" in text
    assert "Authorization header" in text


def test_versioning_and_v12_exit_criteria_are_measurable() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")

    assert "pyproject.toml" in text
    assert "X.Y.Z — YYYY-MM-DD" in text
    assert "vX.Y.Z" in text
    assert "Measurable v12.0 exit criteria" in text
    assert "Ubuntu 24.04 LTS amd64" in text
    assert "GNOME X11 and GNOME Wayland" in text
    assert "Update from the previous release" in text
    assert "Rollback is validated" in text


def test_release_policy_is_linked_from_canonical_docs() -> None:
    assert "RELEASE_CHECKLIST.md" in DOCS_INDEX.read_text(encoding="utf-8")
    assert "RELEASE_CHECKLIST.md" in TESTING.read_text(encoding="utf-8")
    assert "RELEASE_CHECKLIST.md" in PLATFORM.read_text(encoding="utf-8")
    assert "RELEASE_CHECKLIST.md" in ROADMAP.read_text(encoding="utf-8")



def test_bug_report_form_points_to_safe_diagnostic_collection() -> None:
    text = BUG_FORM.read_text(encoding="utf-8")

    assert "./run.sh doctor" in text
    assert "runtime-diagnostics.jsonl" in text
    assert "RELEASE_CHECKLIST.md" in text
    assert "secrets.json" in text
    assert "stop-pin.json" in text
    assert "Authorization headers" in text
    assert "captured camera/screen/audio evidence" in text
