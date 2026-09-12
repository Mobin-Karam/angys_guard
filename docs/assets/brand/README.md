# AngysGuard brand assets

See [`docs/BRAND_GUIDE.md`](../../BRAND_GUIDE.md) for product category, logo meaning, color rules, official reference links, and usage guidance.

This folder contains the canonical AngysGuard identity assets used by the repository and intended for future desktop/mobile apps and product presentation.

## Primary files

- `angysguard-mark.svg` — scalable transparent logo mark.
- `angysguard-app-icon.svg` — canonical square app-icon source.
- `angysguard-mark-monochrome.svg` — single-color/symbolic version.
- `angysguard-wordmark-dark.svg` — horizontal wordmark for dark surfaces.
- `angysguard-wordmark-light.svg` — horizontal wordmark for light surfaces.
- `angysguard-readme-hero.svg` — GitHub README hero.

## Size exports

`icons/svg/` contains explicit SVG exports at:

`16, 20, 24, 32, 48, 64, 96, 128, 180, 192, 256, 512, 1024` pixels.

The SVGs are committed because they remain sharp and reviewable in Git. Raster PNG/ICO files can be regenerated from the canonical sources with:

```bash
python -m pip install cairosvg pillow
python scripts/generate_brand_assets.py
```

That command generates matching PNG sizes under `docs/assets/brand/icons/png/`, a multi-size `favicon.ico`, and a `1280×640` `angysguard-social-preview.png` suitable as a GitHub social-preview upload source.

Treat the SVG sources as canonical. Do not repeatedly rescale a small raster file to create new platform assets.
