---
name: product-roadmap-maintenance
description: Keep AngysGuard product vision, OS/platform support, Bale/Telegram/self-hosted/managed control modes, roadmap milestones/issues, and repository presentation synchronized after releases or product-direction changes.
---

# Product roadmap maintenance

Use this workflow when a release, product decision, new OS/app target, bot/control mode, managed-service decision, or platform request changes AngysGuard's future/current product story.

1. Follow `AGENTS.md` and `docs/GRAPHIFY_NAVIGATION.md`.
2. Check Graphify freshness and use it to verify the current product implementation/support surface before changing claims.
3. Read the smallest relevant current docs:
   - `README.md`;
   - `docs/ANGYSGUARD_PRODUCT_VISION.md`;
   - `docs/PLATFORM_SUPPORT.md`;
   - `docs/CONTROL_MODES.md`;
   - `docs/ROADMAP.md`;
   - `docs/PROJECT_MANAGEMENT.md`;
   - `docs/README_MAINTENANCE.md`;
   - relevant ADRs/issues/milestones.
4. Classify each statement as **current**, **planned**, **research**, or **user-requested**. Do not collapse these states.
5. For a new platform/app/control mode, define:
   - target users/use case;
   - security/privacy constraints;
   - dependencies/prerequisites;
   - capability/support state;
   - issue/milestone/priority;
   - validation required before promotion to Supported.
6. Preserve the product boundaries:
   - self-hosted/local modes remain first-class;
   - managed mode remains optional;
   - no OS password over bot/backend/mobile surfaces;
   - no generic remote shell;
   - no stealth capture/keylogging;
   - device credentials are scoped/revocable;
   - platform privileged actions remain local/native.
7. Update the smallest coherent set of roadmap/support/control/README/project-management files.
8. Update `.github/repository-management/` when labels/milestones/issue mapping change.
9. Use `$repository-presentation` when user-facing landing/About/version/support claims changed.
10. For release work, make `release_manager` verify support/platform/control claims before release.
11. Refresh Graphify after material doc/relationship changes when available.

Return a compact report:

```text
Current verified state:
Roadmap/product change:
State: current | planned | research | requested
Issues/milestones affected:
Docs/presentation affected:
Security constraints:
Validation required before support claim:
Graph freshness:
```

Never mark Windows, Android, managed service, official AngysGuard bots, or another requested platform as shipped merely because a roadmap issue exists.
