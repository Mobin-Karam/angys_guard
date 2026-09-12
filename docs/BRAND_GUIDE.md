# AngysGuard brand guide

## Product category

Use **owner-controlled endpoint security and device protection platform** as the primary category for AngysGuard.

Shorter alternatives:

- **endpoint security platform**;
- **device protection platform**;
- **Linux-first endpoint security agent** when describing the current installed runtime specifically.

Avoid calling AngysGuard an **antivirus** unless the product later ships a real malware-detection engine with malware scanning/detection claims that are validated and maintained. The current product is broader in owner-control, intrusion response, evidence, alerts and device protection, but it is not positioned as a conventional antivirus engine.

Avoid positioning it as spyware, a generic remote-administration tool, or a remote shell. Those descriptions conflict with the project's explicit security boundaries.

## Brand idea

**AngysGuard = Angel of System Guard.**

The mark combines four ideas:

1. **Halo** — guardian/angel identity, ethical intent and visible protection.
2. **Wings** — guardian presence and fast response.
3. **Letter A** — distinctive AngysGuard identity.
4. **Shield + lock** — security, owner authorization and protected actions.

The logo should feel **protective, technical, calm and trustworthy**, not aggressive, militarized or covert.

## Primary logo direction

Use the winged-A mark as the product icon. The horizontal wordmark pairs the mark with `AngysGuard` and the descriptor `Angel of System Guard`.

At small sizes, prioritize the silhouette. Fine details may disappear, so the halo + A + wing silhouette must remain recognizable without relying on text.

Do not add additional metaphors to the icon. The shield/lock already supplies the security cue; adding eyes, cameras, weapons, masks or code symbols would make the mark too busy and can imply surveillance or offensive tooling.

## Color system

| Role | Hex | Use |
|---|---|---|
| Deep Night | `#0B1220` | Primary dark background, app icon base |
| Deep Navy | `#0F172A` | Dark surfaces and high-contrast structure |
| Primary Blue | `#2563EB` | Trust, security, technology |
| Guardian Teal | `#0F766E` | Primary brand/guardian color |
| Accent Cyan | `#22D3EE` | Highlights, halo, active states |
| Success Green | `#22C55E` | Protected/safe/healthy states |
| Light | `#E2E8F0` | Text/shape contrast on dark surfaces |
| Muted | `#94A3B8` | Secondary text |
| Warning Amber | `#F59E0B` | Warnings only, not core branding |
| Danger Red | `#EF4444` | Critical/security danger only |

### Color rules

- The core brand should be **Deep Night + Blue/Teal/Cyan + white/light**.
- Green is a supporting state color, not the main identity color.
- Amber and red are reserved for warning/danger UI; they should not dominate the logo.
- Provide monochrome black and white variants for high-contrast contexts.
- Never rely on color alone to communicate security state.

## Logo usage

### Preferred

- dark app icon for launchers/docks/taskbars;
- transparent vector mark for documents and UI;
- horizontal wordmark on README/site headers;
- monochrome mark where color is unavailable;
- sufficient clear space around the mark.

### Avoid

- stretching or rotating the mark;
- recoloring each element independently without a brand need;
- placing detailed text inside launcher icons;
- adding glow/shadow so strong that the silhouette disappears;
- using the logo to imply official affiliation with Linux, Telegram, Bale, Microsoft, Google or another platform.

## Asset folder

Canonical brand assets live in `docs/assets/brand/`.

- `angysguard-mark.svg` — scalable primary mark;
- `angysguard-app-icon.svg` — dark app icon source;
- `angysguard-mark-monochrome.svg` — symbolic/monochrome mark;
- `angysguard-wordmark-dark.svg` / `angysguard-wordmark-light.svg` — horizontal wordmarks;
- `angysguard-readme-hero.svg` — repository README hero;
- `angysguard-social-preview.png` — GitHub/social preview;
- `icons/angysguard-*.png` — raster icon sizes;
- `icons/favicon.ico` — multi-size favicon;
- `reference/angysguard-brand-board.png` — generated visual concept/reference board.

## Raster sizes

The repository exports PNG icons at:

`16, 20, 24, 32, 48, 64, 96, 128, 180, 192, 256, 512, 1024` pixels.

These cover common favicon, Linux desktop, Windows shell, web/PWA, Apple-touch-style, Android/web preview and high-resolution source use. Platform packaging should still follow that platform's exact current requirements.

## Platform reference guidance

Use official platform design documentation as implementation references rather than copying another security company's logo.

- GNOME app icons: https://developer.gnome.org/hig/guidelines/app-icons
- freedesktop icon-theme specification: https://specifications.freedesktop.org/icon-theme/latest/
- Windows app icons: https://learn.microsoft.com/windows/apps/design/iconography/app-icons
- Windows icon design: https://learn.microsoft.com/windows/apps/design/iconography/app-icon-design
- Android adaptive icons: https://developer.android.com/develop/ui/compose/system/icon_design_adaptive
- Google Play icon specifications: https://developer.android.com/distribute/google-play/resources/icon-design-specifications
- GitHub social preview: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview

Key shared lessons from these references: keep the metaphor simple, preserve a distinctive silhouette, test small sizes, provide monochrome/symbolic variants, respect platform safe areas/masks, and test the mark on both light and dark backgrounds.

## Brand maintenance

For a product rename, major app launch, new platform family, or major visual identity change:

1. use the repository-presentation workflow;
2. update this guide and `docs/assets/brand/` together;
3. keep README/About/social preview synchronized;
4. verify small-size icons and light/dark variants;
5. do not change current/future platform claims just for marketing presentation;
6. keep security wording aligned with `SECURITY.md` and the project architecture.
