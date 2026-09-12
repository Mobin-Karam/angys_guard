---
name: brand-assets
description: Design, review, or refresh AngysGuard logo/brand assets, colors, README hero, app-icon exports, and social-preview sources while keeping product/security claims truthful.
---

# AngysGuard brand assets

Use this skill for logo, icon, wordmark, color, README hero, social preview, and platform app-icon work.

## Canonical sources

Read first:

- `docs/BRAND_GUIDE.md`;
- `docs/assets/brand/README.md`;
- `docs/assets/brand/angysguard-mark.svg`;
- `docs/assets/brand/angysguard-app-icon.svg`;
- `docs/assets/brand/angysguard-mark-monochrome.svg`;
- `docs/README_MAINTENANCE.md`;
- `.github/repository-profile.json`;
- `README.md`.

Use `$repository-presentation` when the change affects the public README/About/profile surface.

## Product/category rule

Use **owner-controlled endpoint security and device protection platform** as the primary category.

Do not market AngysGuard as an antivirus unless a maintained malware-detection engine actually ships and the claim is validated.

## Logo rule

The primary metaphor is:

```text
halo + wings + A + shield/lock
```

Keep it recognizable at small sizes. Do not add extra eyes, cameras, weapons, masks, terminals, or other metaphors to the launcher icon.

## Palette

- Deep Night `#0B1220`
- Deep Navy `#0F172A`
- Blue `#2563EB`
- Guardian Teal `#0F766E`
- Cyan `#22D3EE`
- Success Green `#22C55E`
- Light `#E2E8F0`
- Muted `#94A3B8`
- Warning Amber `#F59E0B` (status only)
- Danger Red `#EF4444` (status only)

## Workflow

1. Confirm the requested identity/product claim against current docs/source.
2. Prefer a simple silhouette that works at 16–32px before adding detail.
3. Keep full-color, dark/light wordmark, and monochrome/symbolic variants.
4. Follow official platform icon constraints rather than copying competitor marks.
5. Keep canonical vector sources under `docs/assets/brand/`.
6. Maintain explicit size exports under `docs/assets/brand/icons/svg/`.
7. Use `scripts/generate_brand_assets.py` for PNG/favicon/social-preview rendering when needed.
8. Update README/profile sources when the public identity changes.
9. Run `tests/test_brand_assets.py` and repository-presentation/link tests.
10. Keep current-vs-future platform claims and security non-goals accurate.

## Review checklist

- recognizable without text;
- legible at 16/24/32px;
- works on dark and light backgrounds;
- monochrome variant remains identifiable;
- no trademark-confusing imitation;
- no surveillance/offensive visual cues;
- colors match `docs/BRAND_GUIDE.md`;
- README/About/social-preview sources remain synchronized;
- Linux/Windows/Android packaging can derive platform-specific assets without redrawing the identity.

## Handoff

Return:

```text
Brand surface changed:
Canonical source assets:
Sizes/variants checked:
Product/category wording:
Platform references checked:
README/About impact:
Tests/checks run:
Manual platform exports still needed:
```
