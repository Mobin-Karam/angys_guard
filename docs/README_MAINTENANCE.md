# Repository presentation and README maintenance

This document defines how AngysGuard keeps its **root README, GitHub About metadata, package metadata, brand assets, documentation index, platform/control-mode claims, release/version references, roadmap state, and repository visuals** synchronized with the actual product.

Repository presentation is a maintained product surface, not a one-time marketing file.

## Goals

The repository landing page should let a new user, maintainer or reviewer understand quickly:

- what AngysGuard is and is not;
- that the preferred category is **owner-controlled endpoint security and device protection platform**;
- what the current shipped Linux release can do;
- which OSes/apps/control modes are current, planned, research, or merely requested;
- how to install and run the current supported platform;
- how Bale/Telegram/self-hosted/managed control differs;
- the security/privacy boundaries that must not be weakened;
- where detailed canonical documentation lives;
- what is shipped versus future roadmap work.

## Canonical presentation/product surfaces

| Surface | Purpose |
| --- | --- |
| `README.md` | GitHub/project/package landing page |
| `docs/BRAND_GUIDE.md` | Product category, logo concept, palette, asset rules, platform design references |
| `docs/assets/brand/` | Canonical mark, app icon, wordmarks, hero and size exports |
| `docs/ANGYSGUARD_PRODUCT_VISION.md` | Long-term product identity/principles/current-vs-future experience |
| `docs/PLATFORM_SUPPORT.md` | Canonical OS support/request policy |
| `docs/CONTROL_MODES.md` | Local/Bale/Telegram/self-hosted/managed control model and credential rules |
| `docs/ROADMAP.md` | Sequenced milestones/issues/future work |
| `docs/PROJECT_MANAGEMENT.md` | Project fields/views/mapping/workflow |
| `docs/assets/laptop-guard-overview.svg` | Legacy README image path; now carries the AngysGuard hero identity |
| `.github/repository-profile.json` | Canonical GitHub About description/topics/social-preview source |
| `scripts/generate_brand_assets.py` | PNG/favicon/social-preview brand renderer |
| `scripts/sync_repository_profile.py` | Read-only preview / optional admin-token About sync helper |
| `pyproject.toml` | Package version/description/README/keywords/URLs |
| `docs/README.md` | Task-oriented documentation index |
| `CHANGELOG.md` | Shipped changes only |
| `SECURITY.md` / `docs/SECURITY.md` | Vulnerability reporting and product trust/security boundaries |

Do not duplicate long canonical content. README should summarize and link.

## Graphify first

Before changing presentation because of a feature, release, platform, provider, control mode, refactor, brand update or repository reorganization, use the Graphify-first workflow.

Useful queries:

```bash
graphify query "what user-visible commands and capabilities exist?"
graphify query "what provider/Bale/Telegram paths exist?"
graphify query "what files define setup, doctor, service, and autostart behavior?"
graphify query "what security boundaries connect remote control to system actions?"
graphify explain "LaptopGuard"
```

Then confirm important current facts against source/tests/docs. A roadmap issue is not evidence that a feature is shipped.

## Required current/future vocabulary

Use these states consistently:

- **Current / shipped / supported** — implemented and release-validated to the documented level.
- **Best effort / experimental** — may work but lacks complete release support/validation.
- **Planned** — roadmap target with issue/milestone; not usable today.
- **Research** — feasibility/architecture work; no delivery promise.
- **User-requested** — demand signal only; not yet a roadmap commitment.

Windows, Android, managed AngysGuard service and future requested platforms must remain clearly marked as future until implementation and validation exist.

## When a presentation/product refresh is required

Review README/profile/brand/platform/control/roadmap docs when any of these changes materially:

1. package version/release status;
2. user-visible feature added/changed/deprecated/removed;
3. CLI/setup/doctor/service/autostart/owner commands;
4. supported Python/OS/session/distro/platform state;
5. Linux/Windows/Android/other platform target or capability;
6. Bale/Telegram/provider support or self-hosted pairing;
7. managed AngysGuard account/bot/service behavior;
8. account/device pairing, credential, revocation or privileged-action model;
9. configuration/secret handling/migration/security defaults;
10. authorization/capture/privacy/lock/stop/unlock/network/process trust boundary;
11. major architecture ownership or repository structure;
12. product/repository naming, logo, color system or branding;
13. documentation/AI/Graphify workflow;
14. a release is being prepared.

Small internal refactors that do not affect public/support claims do not require cosmetic churn.

## Hard product/security copy rules

Never write docs/README copy implying AngysGuard supports:

- covert surveillance;
- credential/password collection;
- keylogging typed contents;
- a generic remote shell/Bash/PowerShell executor;
- arbitrary remote filesystem/process control;
- bypassing OS/compositor privacy boundaries;
- sending the protected device's OS password through Bale, Telegram, Android/mobile UI or managed backend;
- storing OS passwords as ordinary environment variables for remote operation;
- Windows/Android/other-platform support that has not been implemented and target-device validated;
- antivirus/malware-engine capabilities that do not actually ship.

Managed service remains optional; self-hosted/local operation stays first-class.

## Brand workflow

Use `$brand-assets` for logo/icon/wordmark/color/social-preview work.

Canonical brand rules:

- primary category: **owner-controlled endpoint security and device protection platform**;
- mark concept: **halo + wings + A + shield/lock**;
- preserve small-size silhouette first;
- use the palette in `docs/BRAND_GUIDE.md`;
- keep full-color, monochrome, dark/light wordmark and launcher-icon variants;
- keep size exports under `docs/assets/brand/icons/svg/`;
- use `scripts/generate_brand_assets.py` for PNG/favicon/social-preview rendering;
- follow official platform icon guidance linked from `docs/BRAND_GUIDE.md` rather than copying other security brands.

## Product roadmap workflow

For platform/app/control-mode/managed-service changes, use `product_planner` or `$product-roadmap-maintenance` and reconcile product vision, platform support, control modes, roadmap, Project mapping, issues/milestones and public presentation.

## Repository presentation workflow

Use `repository_curator` / `$repository-presentation` after a release/version change or material public/support/brand change.

### 1. Establish the current shipped baseline

Read only relevant Graphify-selected authoritative files. Common sources:

```text
pyproject.toml
CHANGELOG.md
docs/PLATFORM_SUPPORT.md
docs/CONTROL_MODES.md
docs/BRAND_GUIDE.md
docs/ROADMAP.md
docs/SECURITY.md
docs/TESTING.md
laptop_guard/cli.py
laptop_guard/setup_wizard.py
laptop_guard/features/
```

### 2. Update the smallest affected set

- `README.md` for public/current/future summary;
- `BRAND_GUIDE.md` / `docs/assets/brand/` for visual identity changes;
- `PLATFORM_SUPPORT.md` for OS support-state changes;
- `CONTROL_MODES.md` for Bale/Telegram/self-hosted/managed changes;
- `ANGYSGUARD_PRODUCT_VISION.md` for long-term direction/principles;
- `ROADMAP.md` / `PROJECT_MANAGEMENT.md` for targets/issues/milestones;
- overview/hero SVG when high-level product direction or identity changes;
- repository profile when About/topics should change;
- `pyproject.toml` when package description/version/keywords change;
- `CHANGELOG.md` for shipped repository/presentation changes.

### 3. Keep GitHub About synchronized

Preview:

```bash
python scripts/sync_repository_profile.py
```

Apply only from a trusted admin-capable environment:

```bash
export GH_TOKEN='<admin-capable token>'
python scripts/sync_repository_profile.py --apply
```

Never commit/log/share that token. Social preview still requires GitHub repository settings upload; render its PNG source with `scripts/generate_brand_assets.py` when needed.

### 4. Verify consistency

At minimum:

```bash
.venv/bin/python -m pytest -q tests/test_repository_presentation.py tests/test_brand_assets.py
.venv/bin/python -m pytest -q tests/test_documentation_links.py tests/test_graphify_navigation_policy.py
python scripts/sync_repository_profile.py
```

For release work, also run `docs/TESTING.md` / `$release-readiness` checks.

### 5. Refresh Graphify when available

```bash
graphify update .
```

Never hand-edit generated graph output to simulate freshness.

## Root README content contract

The root README should retain equivalent coverage for:

```text
hero / AngysGuard identity + compatibility note
what the product is and what category to use
project status
OS/platform support today
Bale / Telegram / local control surfaces
self-hosted bot model
future managed service model
OS-password hard boundary
current capabilities / explicit non-goals
architecture / flow
Linux quick start
configuration
future Linux/Windows/Android app targets
platform request path
repository map
Graphify-first engineering
security/privacy
validation/testing
documentation index
roadmap
AI/contributing/presentation/brand maintenance
license
```

## Version and support rules

`pyproject.toml` is authoritative for the current package version. README current-version status must match. A platform moves to Supported only after implementation, documentation, explicit limitations, target-device validation and release review.

## Pull-request checklist

For product/presentation/brand-affecting work:

- [ ] Graphify used first or fallback documented;
- [ ] current source/tests confirm shipped claims;
- [ ] current/planned/research/requested states are distinct;
- [ ] root README version matches `pyproject.toml`;
- [ ] brand category/logo/palette assets updated together when affected;
- [ ] no unsupported antivirus claim introduced;
- [ ] platform/control-mode docs updated when affected;
- [ ] no OS-password-through-bot/backend design is documented as acceptable;
- [ ] self-hosted/local remains a supported design path;
- [ ] security/non-goal wording remains accurate;
- [ ] commands/install examples are current;
- [ ] documentation links resolve;
- [ ] `.github/repository-profile.json` is current;
- [ ] brand/presentation/policy tests pass;
- [ ] Graphify refresh/follow-up accounted for.
