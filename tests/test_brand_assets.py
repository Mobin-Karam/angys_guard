from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "docs" / "assets" / "brand"
SIZES = (16, 20, 24, 32, 48, 64, 96, 128, 180, 192, 256, 512, 1024)


def test_canonical_brand_sources_exist() -> None:
    required = (
        BRAND / "angysguard-mark.svg",
        BRAND / "angysguard-app-icon.svg",
        BRAND / "angysguard-mark-monochrome.svg",
        BRAND / "angysguard-wordmark-dark.svg",
        BRAND / "angysguard-wordmark-light.svg",
        BRAND / "angysguard-readme-hero.svg",
        ROOT / "docs" / "BRAND_GUIDE.md",
        ROOT / "scripts" / "generate_brand_assets.py",
        ROOT / ".agents" / "skills" / "brand-assets" / "SKILL.md",
        ROOT / ".github" / "prompts" / "design-or-refresh-brand.prompt.md",
    )
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    assert not missing, f"missing canonical brand files: {missing}"


def test_all_declared_icon_sizes_are_committed() -> None:
    icon_dir = BRAND / "icons" / "svg"
    for size in SIZES:
        path = icon_dir / f"angysguard-{size}.svg"
        assert path.exists(), f"missing {size}px AngysGuard SVG export"
        text = path.read_text(encoding="utf-8")
        assert f'width="{size}"' in text
        assert f'height="{size}"' in text


def test_readme_hero_contains_angysguard_identity() -> None:
    hero = (ROOT / "docs" / "assets" / "laptop-guard-overview.svg").read_text(
        encoding="utf-8"
    )
    assert "AngysGuard" in hero
    assert "ANGEL OF SYSTEM GUARD" in hero
    assert "endpoint security and device protection" in hero


def test_repository_profile_points_at_brand_sources() -> None:
    profile = json.loads(
        (ROOT / ".github" / "repository-profile.json").read_text(encoding="utf-8")
    )
    assert profile["brand_guide"] == "docs/BRAND_GUIDE.md"
    assert profile["social_preview_source"] == "docs/assets/brand/angysguard-readme-hero.svg"
    assert "endpoint security" in profile["description"].lower()


def test_brand_category_does_not_claim_antivirus() -> None:
    guide = (ROOT / "docs" / "BRAND_GUIDE.md").read_text(encoding="utf-8")
    assert "owner-controlled endpoint security and device protection platform" in guide
    assert "Do **not** call AngysGuard an **antivirus**" in guide


def test_brand_generator_keeps_expected_sizes() -> None:
    script = (ROOT / "scripts" / "generate_brand_assets.py").read_text(encoding="utf-8")
    for size in SIZES:
        assert str(size) in script
    assert "favicon.ico" in script
    assert "angysguard-social-preview.png" in script
