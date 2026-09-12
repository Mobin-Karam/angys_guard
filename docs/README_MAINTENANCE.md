# Repository presentation and README maintenance

This document defines how Laptop Guard keeps its **root README, GitHub About metadata, package metadata, documentation index, release/version references, and repository visuals** synchronized with the actual product.

Repository presentation is a maintained product surface, not a one-time marketing file.

## Goals

The repository landing page should let a new maintainer, reviewer, or authorized user understand in a few minutes:

- what Laptop Guard is and is not;
- what the current shipped release can do;
- the security/privacy boundaries that must not be weakened;
- how to install, configure, run, test, and contribute;
- how the major runtime pieces connect;
- where canonical detailed documentation lives;
- what is shipped versus planned;
- how AI agents and Graphify are expected to navigate the repository.

The README should be useful without duplicating every detail from the canonical docs.

## Canonical presentation surfaces

| Surface | Purpose |
| --- | --- |
| `README.md` | GitHub repository landing page and primary public/project overview |
| `docs/assets/laptop-guard-overview.svg` | High-level product/flow visual used by the root README |
| `.github/repository-profile.json` | Canonical GitHub About description, topics, social-preview source, and presentation metadata |
| `pyproject.toml` | Package version, Python requirement, dependencies, package description, README source |
| `docs/README.md` | Detailed task-oriented documentation index and maintainer entry point |
| `CHANGELOG.md` | Shipped changes only |
| `docs/ROADMAP.md` | Planned milestones/work only |
| `SECURITY.md` / `docs/SECURITY.md` | Vulnerability reporting and product security/trust boundaries |
| `docs/FILE_REFERENCE.md` | Detailed ownership/file map |

Do not copy large canonical sections between these files. The root README should summarize and link.

## Graphify first

Before changing presentation because of a feature, release, refactor, or repository reorganization, follow the repository Graphify-first rule.

Check freshness, then ask targeted questions such as:

```bash
graphify query "what user-visible commands and capabilities exist?"
graphify query "what files define setup, doctor, service, and autostart behavior?"
graphify query "what security boundaries connect remote control to system actions?"
graphify query "what tests cover RuntimeApi and FeatureManager?"
graphify explain "LaptopGuard"
```

Use Graphify to identify the smallest authoritative files, then confirm the current source/tests/docs before changing README claims.

If Graphify is stale and cannot be refreshed, use the narrowest direct fallback search and record that limitation.

## When a presentation refresh is required

A README/profile review is required when any of these materially changes:

1. package version or release status;
2. user-visible feature added, changed, deprecated, or removed;
3. CLI command, setup flow, doctor check, service/autostart behavior, or owner command changes;
4. supported Python version, OS/session support, required packages, or hardware/backend requirements;
5. provider/transport capabilities or local-only behavior;
6. configuration location, secret handling, migration, or security defaults;
7. authorization, capture/privacy, lock/stop/unlock, network, process, or other trust boundary;
8. architecture ownership important enough to change the README architecture diagram or repository map;
9. documentation files move or canonical docs change;
10. repository AI/Graphify workflow changes;
11. repository name, description, topics, license, or social-preview visual changes;
12. a release is being prepared.

Small internal refactors that do not affect any README statement do not require cosmetic README churn.

## Required workflow

### 1. Establish the shipped baseline

Read only the relevant authoritative sources identified through Graphify. Common sources include:

```text
pyproject.toml
CHANGELOG.md
docs/ROADMAP.md
docs/ARCHITECTURE.md
docs/CONFIGURATION.md
docs/SECURITY.md
docs/TESTING.md
docs/FILE_REFERENCE.md
laptop_guard/cli.py
laptop_guard/models.py
laptop_guard/setup_wizard.py
laptop_guard/doctor.py
laptop_guard/features/
```

Do not describe roadmap work as already available.

### 2. Update the smallest presentation set

Depending on the change, update only what is affected:

- `README.md` for user-facing/project-overview facts;
- `docs/assets/laptop-guard-overview.svg` when the product flow or major capability groups change;
- `.github/repository-profile.json` when description/topics/preview metadata should change;
- `docs/README.md` when the documentation navigation changes;
- `pyproject.toml` when version/package description/readme source changes;
- `CHANGELOG.md` for shipped presentation/repository changes.

### 3. Keep GitHub About synchronized

`.github/repository-profile.json` is the canonical source for the GitHub About panel.

The current GitHub connector/project automation may not have repository-administration permission to mutate About metadata automatically. When automated synchronization is unavailable, a maintainer should apply the file values in GitHub:

```text
Repository → About → gear icon
Description   = repository-profile.json:description
Website       = repository-profile.json:homepage (blank when null)
Topics        = repository-profile.json:topics
```

For social preview, use the repository visual as the source design; GitHub may require a raster upload in the repository settings UI.

Do not invent a website URL solely to fill the About panel.

### 4. Verify consistency

At minimum run:

```bash
.venv/bin/python -m pytest -q tests/test_repository_presentation.py
.venv/bin/python -m pytest -q tests/test_documentation_links.py tests/test_graphify_navigation_policy.py
```

For a release, run the full checks required by `docs/TESTING.md` and `$release-readiness`.

### 5. Refresh Graphify after material documentation relationships change

When Graphify is available:

```bash
graphify update .
```

Generated graph output must be regenerated by Graphify rather than hand-edited to simulate freshness.

## Root README content contract

The root README should retain these high-level sections unless a deliberate redesign replaces them with equivalent coverage:

```text
hero / product identity
what the product is
project status
capabilities
explicit non-goals / safety boundaries
architecture / flow
quick start
operations / controls
configuration
repository map
Graphify-first workflow
security/privacy
validation/testing
documentation index
AI-assisted development
roadmap
contributing
presentation maintenance
license
```

The exact wording can evolve. The coverage should not silently disappear.

## Version rule

The current package version is authoritative in `pyproject.toml`.

The root README should expose the same current version in its status/badge area. `tests/test_repository_presentation.py` verifies this relationship so version bumps cannot silently leave the landing page stale.

Release notes belong in `CHANGELOG.md` / GitHub Releases. Do not turn the README into a complete release log.

## Feature-claim rule

Every concrete capability claimed by the root README must be supported by current source/tests/canonical documentation.

For a new capability:

```text
implementation + tests + detailed docs
        ↓
README summary (if important to users/project identity)
        ↓
About/topic update (only if it changes repository discoverability)
```

For a removed capability, reverse the process and remove stale README/About claims in the same change when practical.

## Security wording rule

Do not use README copy that implies Laptop Guard supports:

- covert surveillance;
- credential theft;
- keylogging typed contents;
- unrestricted command execution;
- arbitrary remote filesystem access;
- bypassing desktop/compositor privacy boundaries.

Security-sensitive descriptions should remain consistent with `docs/SECURITY.md` and the root `AGENTS.md` hard gates.

## Visual maintenance rule

The overview graphic is a documentation artifact, not a product screenshot.

Update it only when the high-level capability flow changes. Keep it:

- readable in GitHub light/dark contexts;
- free of secrets, private screenshots, user names, chat IDs, or device identifiers;
- independent of third-party trademarked UI screenshots;
- descriptive rather than decorative;
- small enough to render quickly in the README.

## Agent and skill support

Use one of these equivalent project workflows:

```text
$repository-presentation
```

```text
Have repository_curator refresh the repository presentation for the current change/release.
```

```text
Use .github/prompts/refresh-repository-presentation.prompt.md
```

The agent/skill must still verify current source and may not invent capabilities from roadmap text.

## Pull-request checklist

For presentation-affecting work:

- [ ] Graphify used first or narrow fallback documented;
- [ ] current source/tests confirm user-facing claims;
- [ ] root README version matches `pyproject.toml`;
- [ ] shipped and planned behavior remain clearly separated;
- [ ] security/non-goal wording remains accurate;
- [ ] commands/install examples are copy-pasteable;
- [ ] documentation links resolve;
- [ ] `.github/repository-profile.json` is current;
- [ ] overview graphic updated only if the product flow changed;
- [ ] presentation regression tests pass;
- [ ] Graphify refreshed after material relationship/doc changes when practical.
