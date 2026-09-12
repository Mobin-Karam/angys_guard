# Repository presentation and README maintenance

This document defines how AngysGuard / Laptop Guard keeps its **root README, GitHub About metadata, package metadata, documentation index, platform/control-mode claims, release/version references, roadmap state, and repository visuals** synchronized with the actual product.

Repository presentation is a maintained product surface, not a one-time marketing file.

## Goals

The repository landing page should let a new user, maintainer or reviewer understand quickly:

- what AngysGuard is and is not;
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
| `docs/ANGYSGUARD_PRODUCT_VISION.md` | Long-term product identity/principles/current-vs-future experience |
| `docs/PLATFORM_SUPPORT.md` | Canonical current/best-effort/planned/research/not-targeted OS matrix and request policy |
| `docs/CONTROL_MODES.md` | Local/Bale/Telegram/self-hosted/managed control model and credential rules |
| `docs/ROADMAP.md` | Sequenced milestones/issues/future work |
| `docs/PROJECT_MANAGEMENT.md` | Project fields/views/mapping/workflow |
| `docs/assets/laptop-guard-overview.svg` | High-level AngysGuard product/flow visual |
| `.github/repository-profile.json` | Canonical GitHub About description/topics/social-preview source |
| `scripts/sync_repository_profile.py` | Read-only preview / optional admin-token About sync helper |
| `pyproject.toml` | Package version/description/README/keywords/URLs |
| `docs/README.md` | Task-oriented documentation index |
| `CHANGELOG.md` | Shipped changes only |
| `SECURITY.md` / `docs/SECURITY.md` | Vulnerability reporting and product trust/security boundaries |

Do not duplicate long canonical content. README should summarize and link.

## Graphify first

Before changing presentation because of a feature, release, platform, provider, control mode, refactor or repository reorganization, use the Graphify-first workflow.

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

Review README/profile/platform/control/roadmap docs when any of these changes materially:

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
12. product/repository naming or branding;
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
- Windows/Android/other-platform support that has not been implemented and target-device validated.

Managed service remains optional; self-hosted/local operation stays first-class.

## Product roadmap workflow

For platform/app/control-mode/managed-service changes, use:

```text
product_planner
```

or:

```text
$product-roadmap-maintenance
```

The workflow should reconcile:

- `ANGYSGUARD_PRODUCT_VISION.md`;
- `PLATFORM_SUPPORT.md`;
- `CONTROL_MODES.md`;
- `ROADMAP.md`;
- `PROJECT_MANAGEMENT.md`;
- issues/milestones/labels;
- root README and repository profile where public claims changed.

Substantial roadmap work belongs in focused GitHub issues rather than prose only.

## Repository presentation workflow

Use `repository_curator` / `$repository-presentation` after a release/version change or material public/support change.

### 1. Establish the current shipped baseline

Read only relevant Graphify-selected authoritative files. Common sources:

```text
pyproject.toml
CHANGELOG.md
docs/PLATFORM_SUPPORT.md
docs/CONTROL_MODES.md
docs/ROADMAP.md
docs/SECURITY.md
docs/TESTING.md
laptop_guard/cli.py
laptop_guard/setup_wizard.py
laptop_guard/features/
```

### 2. Update the smallest affected set

- `README.md` for public/current/future summary;
- `PLATFORM_SUPPORT.md` for OS support-state changes;
- `CONTROL_MODES.md` for Bale/Telegram/self-hosted/managed changes;
- `ANGYSGUARD_PRODUCT_VISION.md` for long-term direction/principles;
- `ROADMAP.md` / `PROJECT_MANAGEMENT.md` for targets/issues/milestones;
- overview SVG when high-level product direction changes;
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

Never commit/log/share that token. Social preview still requires GitHub repository settings upload.

### 4. Verify consistency

At minimum:

```bash
.venv/bin/python -m pytest -q tests/test_repository_presentation.py
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
what the product is
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
AI/contributing/presentation maintenance
license
```

## Version rule

`pyproject.toml` is authoritative for the current package version. README current-version status must match. Releases should not silently move planned platform/control capabilities into shipped copy.

## Platform support promotion rule

A platform moves from Planned/Best effort to Supported only after:

- implementation exists;
- installation/update steps are documented;
- required capability limitations are explicit;
- target-device testing exists;
- provider/security behavior is validated where relevant;
- release manager/product planner/repository curator agree that the support claim is accurate.

## Pull-request checklist

For product/presentation-affecting work:

- [ ] Graphify used first or fallback documented;
- [ ] current source/tests confirm shipped claims;
- [ ] current/planned/research/requested states are distinct;
- [ ] root README version matches `pyproject.toml`;
- [ ] platform/control-mode docs updated when affected;
- [ ] no OS-password-through-bot/backend design is documented as acceptable;
- [ ] self-hosted/local remains a supported design path;
- [ ] security/non-goal wording remains accurate;
- [ ] commands/install examples are current;
- [ ] documentation links resolve;
- [ ] `.github/repository-profile.json` is current;
- [ ] overview graphic updated only if product direction changed;
- [ ] presentation/policy tests pass;
- [ ] Graphify refresh/follow-up accounted for.
