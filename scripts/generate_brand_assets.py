#!/usr/bin/env python3
"""Render AngysGuard SVG brand sources to common raster icon sizes.

This is a maintainer/design helper. It is not part of the AngysGuard runtime.
Requires Pillow (already used by the project) and CairoSVG (`python -m pip install cairosvg`).
"""
from __future__ import annotations

from pathlib import Path

SIZES = (16, 20, 24, 32, 48, 64, 96, 128, 180, 192, 256, 512, 1024)
ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "docs" / "assets" / "brand"
SOURCE = BRAND / "angysguard-app-icon.svg"
HERO = BRAND / "angysguard-readme-hero.svg"
OUT = BRAND / "icons" / "png"


def main() -> int:
    try:
        import cairosvg
        from PIL import Image
    except ImportError as exc:
        raise SystemExit(
            "Brand rendering requires CairoSVG and Pillow. Install with: "
            "python -m pip install cairosvg pillow"
        ) from exc

    OUT.mkdir(parents=True, exist_ok=True)

    for size in SIZES:
        target = OUT / f"angysguard-{size}.png"
        cairosvg.svg2png(
            url=str(SOURCE),
            write_to=str(target),
            output_width=size,
            output_height=size,
        )

    source_1024 = Image.open(OUT / "angysguard-1024.png").convert("RGBA")
    source_1024.save(
        OUT / "favicon.ico",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )

    cairosvg.svg2png(
        url=str(HERO),
        write_to=str(BRAND / "angysguard-social-preview.png"),
        output_width=1280,
        output_height=640,
    )

    print(f"Rendered AngysGuard brand assets to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
