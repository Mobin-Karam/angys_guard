from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def _markdown_files() -> list[Path]:
    paths = list(ROOT.glob("*.md"))
    paths.extend((ROOT / "docs").rglob("*.md"))
    paths.extend((ROOT / ".github").rglob("*.md"))
    paths.extend((ROOT / ".agents").rglob("*.md"))
    paths.extend((ROOT / ".codex").rglob("*.md"))
    return sorted(set(paths))


def _local_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None

    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None

    return (source.parent / target).resolve()


def test_local_markdown_links_point_to_existing_paths() -> None:
    missing: list[str] = []

    for source in _markdown_files():
        text = source.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = _local_target(source, match.group(1))
            if target is None:
                continue
            if not target.exists():
                missing.append(
                    f"{source.relative_to(ROOT)} -> {match.group(1)}"
                )

    assert missing == [], "Broken local Markdown links:\n" + "\n".join(missing)


def test_docs_index_links_canonical_maintenance_guides() -> None:
    index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for name in (
        "FEATURE_LIFECYCLE.md",
        "BUG_TRIAGE_AND_FIXING.md",
        "AI_AGENT_WORKFLOW.md",
        "FILE_REFERENCE.md",
        "TESTING.md",
    ):
        assert name in index
        assert name in agents
