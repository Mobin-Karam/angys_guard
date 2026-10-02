"""Contract checks for the static GitHub Pages product website."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_website_has_bilingual_seo_aeo_and_safety_content() -> None:
    page = (ROOT / "site" / "index.html").read_text()

    assert '<html lang="en" dir="ltr">' in page
    assert 'lang=fa' in page
    assert 'rel="canonical" href="https://mobin-karam.github.io/angys_guard/"' in page
    assert '"@type":"SoftwareApplication"' in page
    assert '"@type":"FAQPage"' in page
    assert 'name="description"' in page
    assert "No supported Windows protection release exists today." in page
    assert "No generic remote shell" in page
    assert "./install.sh" in page
    assert "./run.sh doctor" in page
    assert "npm install -g @angysguard/linux-agent" in page
    assert 'data-copy="npm-install-command"' in page
    assert "navigator.clipboard.writeText" in page


def test_pages_workflow_deploys_only_the_single_html_site() -> None:
    workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text()

    assert "actions/configure-pages@v5" in workflow
    assert "actions/upload-pages-artifact@v4" in workflow
    assert "actions/deploy-pages@v4" in workflow
    assert "pages: write" in workflow
    assert "id-token: write" in workflow
    assert "path: site" in workflow


def test_repository_profile_declares_the_pages_homepage() -> None:
    profile = (ROOT / ".github" / "repository-profile.json").read_text()

    assert '"homepage": "https://mobin-karam.github.io/angys_guard/"' in profile
