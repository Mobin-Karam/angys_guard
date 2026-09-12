# AngysGuard brand guide

## Product category

Use **owner-controlled endpoint security and device protection platform** as the primary category for AngysGuard.

Shorter alternatives:

- **endpoint security platform**;
- **device protection platform**;
- **Linux-first endpoint security agent** when describing the installed runtime specifically.

Do **not** call AngysGuard an **antivirus** unless the project later ships and maintains a real malware-detection engine with validated malware-scanning/detection claims. AngysGuard currently focuses on owner-controlled monitoring, intrusion response, bounded evidence, alerting, safe device actions, and constrained remote control.

Avoid positioning it as spyware, a generic remote-administration tool, or a remote shell. Those descriptions conflict with the project's explicit security boundaries.

## Brand idea

**AngysGuard = Angel of System Guard.**

The mark combines four ideas:

1. **Halo** — guardian/angel identity, ethical intent, visible protection.
2. **Wings** — guardian presence and fast response.
3. **Letter A** — distinctive AngysGuard identity.
4. **Shield + lock** — security, owner authorization, and protected actions.

The identity should feel **protective, technical, calm, and trustworthy**, not aggressive, militarized, or covert.

## Logo direction

Use the **winged A** as the primary product mark. The horizontal wordmark pairs the mark with `AngysGuard` and `Angel of System Guard`.

At small sizes, prioritize the silhouette. Fine details disappear quickly, so the halo + A + wing shape must remain recognizable without relying on text.

Do not add more metaphors to the launcher icon. The shield/lock already supplies the security cue; eyes, cameras, weapons, masks, terminals, or code symbols would make the mark too busy and can imply surveillance/offensive tooling.

## Color system

| Role | Hex | Use |
|---|---|---|
| Deep Night | `#0B1220` | Primary dark background, app icon base |
| Deep Navy | `#0F172A` | Dark surfaces and high-contrast structure |
| Primary Blue | `#2563EB` | Trust, security, technology |
| Guardian Teal | `#0F766E` | Primary guardian/security brand color |
| Accent Cyan | `#22D3EE` | Highlights, halo, active states |
| Success Green | `#22C55E` | Protected/safe/healthy states |
| Light | `#E2E8F0` | Text/shape contrast on dark surfaces |
| Muted | `#94A3B8` | Secondary text |
| Warning Amber | `#F59E0B` | Warnings only, not core branding |
| Danger Red | `#EF4444` | Critical/security-danger states only |

### Color rules

- Core identity: **Deep Night + Blue/Teal/Cyan + white/light**.
- Green is a supporting state color, not the main identity color.
- Amber and red are reserved for warning/danger UI and should not dominate the logo.
- Keep a monochrome/symbolic variant for high-contrast and platform-theming contexts.
- Never rely on color alone to communicate a security state.

## Logo usage

### Preferred

- dark app icon for launchers/docks/taskbars;
- transparent vector mark for documents and UI;
- horizontal wordmark for README/site/product headers;
- monochrome mark where color is unavailable;
- generous clear space around the mark.

### Avoid

- stretching, skewing, or rotating the mark;
- arbitrary per-element recoloring;
- detailed text inside launcher icons;
- excessive glow/shadow that damages the silhouette;
- implying official affiliation with Linux, Telegram, Bale, Microsoft, Google, GNOME, or another platform/provider.

## Asset folder

Canonical brand assets live in `docs/assets/brand/`.

- `angysguard-mark.svg` — scalable primary mark;
- `angysguard-app-icon.svg` — square app icon source;
- `angysguard-mark-monochrome.svg` — symbolic/monochrome mark;
- `angysguard-wordmark-dark.svg` / `angysguard-wordmark-light.svg` — horizontal wordmarks;
- `angysguard-readme-hero.svg` — repository README hero;
- `icons/svg/angysguard-*.svg` — explicit size exports;
- `README.md` — asset inventory and generation instructions.

## Sizes

Committed SVG size exports cover:

`16, 20, 24, 32, 48, 64, 96, 128, 180, 192, 256, 512, 1024` pixels.

Generate matching PNG exports, a multi-size favicon, and a GitHub social-preview PNG with:

```bash
python -m pip install cairosvg pillow
python scripts/generate_brand_assets.py
```

These sizes cover common favicon, Linux desktop, Windows shell, web/PWA, touch-icon, Android/web preview, and high-resolution source use. Platform packaging must still follow each platform's current requirements.

## Platform reference guidance

Use official platform design documentation as implementation references rather than copying another security company's logo.

- GNOME app icons: https://developer.gnome.org/hig/guidelines/app-icons
- freedesktop icon-theme specification: https://specifications.freedesktop.org/icon-theme-spec/latest/
- Windows app icons: https://learn.microsoft.com/windows/apps/design/iconography/app-icons
- Windows icon design: https://learn.microsoft.com/windows/apps/design/iconography/app-icon-design
- Android adaptive icons: https://developer.android.com/develop/ui/compose/system/icon_design_adaptive
- Google Play icon specifications: https://developer.android.com/distribute/google-play/resources/icon-design-specifications
- GitHub social preview: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview

Shared lessons: keep the metaphor simple, preserve a distinctive silhouette, test small sizes, provide monochrome/symbolic variants, respect platform safe areas and masks, and test the mark on light and dark backgrounds.

## Brand maintenance

For a product rename, major app launch, new platform family, or major visual-identity change:

1. use the repository-presentation workflow;
2. update this guide and `docs/assets/brand/` together;
3. keep README/About/social-preview sources synchronized;
4. verify small-size and light/dark variants;
5. keep current-vs-future platform claims truthful;
6. keep security wording aligned with `SECURITY.md`, `AGENTS.md`, and architecture decisions.
