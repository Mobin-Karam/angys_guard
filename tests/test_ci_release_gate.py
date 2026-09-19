from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_runs_for_pushes_and_pull_requests_on_supported_python_versions() -> None:
    text = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "  push:" in text
    assert "  pull_request:" in text
    assert 'python-version: ["3.11", "3.12", "3.13"]' in text
    assert "python -m compileall -q laptop_guard tests" in text
    assert "python -m pytest -q" in text


def test_ci_has_single_release_gate_that_depends_on_full_matrix() -> None:
    text = CI_WORKFLOW.read_text(encoding="utf-8")

    assert "release-gate:" in text
    assert "name: Release gate" in text
    assert "needs: test" in text
    assert "needs.test.result" in text
    assert 'test "$TEST_RESULT" = "success"' in text
