# Design or refresh AngysGuard brand assets

Use the repository's canonical brand workflow rather than inventing a disconnected logo.

1. Read `AGENTS.md`, `docs/GRAPHIFY_NAVIGATION.md`, `docs/BRAND_GUIDE.md`, `docs/assets/brand/README.md`, and `.agents/skills/brand-assets/SKILL.md`.
2. Confirm the current product category and support claims from canonical docs/source before writing marketing copy.
3. Treat AngysGuard as an **owner-controlled endpoint security and device protection platform**. Do not call it antivirus unless a validated malware-detection engine actually ships.
4. Preserve the core mark concept: halo + wings + A + shield/lock.
5. Prefer simple geometry and a strong small-size silhouette over added detail.
6. Use the canonical palette from `docs/BRAND_GUIDE.md`.
7. Keep or update full-color, monochrome/symbolic, dark/light wordmark, README hero, and app-icon variants together.
8. Maintain explicit icon exports at the sizes documented in `docs/BRAND_GUIDE.md` and regenerate raster assets with `scripts/generate_brand_assets.py` when needed.
9. Check official GNOME/freedesktop, Windows, Android/Google Play, and GitHub social-preview guidance linked from the brand guide.
10. Do not imitate another security vendor's trademark/logo, imply official platform affiliation, or add covert-surveillance/offensive imagery.
11. Use `$repository-presentation` if README/About/profile/social-preview surfaces change.
12. Run `tests/test_brand_assets.py` plus relevant repository-presentation and documentation-link tests.

Return a compact report with the changed brand assets, product wording, palette/variant decisions, sizes verified, platform-specific follow-ups, and checks run.
