from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_canonical_graphify_navigation_guide_exists_and_documents_commands() -> None:
    text = _text("docs/GRAPHIFY_NAVIGATION.md")
    assert "Graphify-first" in text
    assert "graphify query" in text
    assert "graphify explain" in text
    assert "graphify path" in text
    assert "graphify update ." in text
    assert "graph.json" in text
    assert "final authority" in text


def test_authoritative_and_scoped_agent_instructions_are_graphify_first() -> None:
    for path in (
        "AGENTS.md",
        "AGENT.md",
        "laptop_guard/AGENTS.md",
        "tests/AGENTS.md",
        "docs/AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        ".github/copilot-instructions.md",
        ".github/instructions/runtime.instructions.md",
        ".github/instructions/tests.instructions.md",
    ):
        text = _text(path)
        assert "Graphify" in text, path
        assert "GRAPHIFY_NAVIGATION.md" in text, path


def test_codex_has_graphify_navigator_and_session_freshness_context() -> None:
    config = _text(".codex/config.toml")
    navigator = _text(".codex/agents/navigator.toml")
    hook = _text(".codex/hooks/session_start.py")

    assert "[agents.navigator]" in config
    assert 'config_file = "agents/navigator.toml"' in config
    assert "docs/GRAPHIFY_NAVIGATION.md" in navigator
    assert "graphify query" in navigator
    assert "Graphify" in hook
    assert "Built from commit" in hook
    assert "graphify update ." in hook


def test_every_codex_specialist_mentions_graphify_navigation() -> None:
    for name in (
        "architect",
        "implementer",
        "reviewer",
        "security_reviewer",
        "tester",
        "release_manager",
    ):
        text = _text(f".codex/agents/{name}.toml")
        assert "Graphify" in text, name
        assert "GRAPHIFY_NAVIGATION.md" in text, name


def test_graphify_skill_and_prompt_are_registered() -> None:
    skill = _text(".agents/skills/graphify-navigation/SKILL.md")
    skills_readme = _text(".agents/README.md")
    prompt = _text(".github/prompts/graphify-navigation.prompt.md")
    prompt_readme = _text(".github/prompts/README.md")

    assert "name: graphify-navigation" in skill
    assert "graphify-navigation" in skills_readme
    assert "GRAPHIFY_NAVIGATION.md" in prompt
    assert "graphify-navigation.prompt.md" in prompt_readme


def test_human_maintenance_guides_start_from_graph_navigation() -> None:
    for path in (
        "CONTRIBUTING.md",
        "docs/README.md",
        "docs/FEATURE_LIFECYCLE.md",
        "docs/BUG_TRIAGE_AND_FIXING.md",
        "docs/AI_AGENT_WORKFLOW.md",
    ):
        text = _text(path)
        assert "Graphify" in text, path
        assert "GRAPHIFY_NAVIGATION.md" in text, path


def test_checked_in_graph_report_records_build_commit() -> None:
    # Freshness itself is operational: SessionStart and the canonical guide compare
    # this recorded commit with the working tree. This test only ensures the metadata
    # required for that check is still present in generated output.
    report = _text("graphify-out/GRAPH_REPORT.md")
    assert "## Graph Freshness" in report
    assert "Built from commit:" in report
