# GitHub Project management

This document defines the canonical GitHub Project v2 structure for AngysGuard / Laptop Guard.

The repository tracks execution through issues, milestones, labels, roadmap docs, and project issue #9. A native GitHub Project board should visualize that same data rather than create a second planning system.

## Project

**Name:** `AngysGuard — Product, Platform & Architecture Delivery`

**Purpose:** one board for current product-readiness work, architecture evolution, AngysGuard self-hosted UX, optional managed-service work, platform expansion, security and release preparation.

Repository issues remain the source of truth for requirements/acceptance criteria. Milestones group delivery targets. `docs/ROADMAP.md` explains sequencing.

## Fields

| Field | Type | Values / purpose |
|---|---|---|
| Status | Single select | Backlog, Ready, In progress, Review, Validation, Done |
| Priority | Single select | P0, P1, P2, P3 |
| Track | Single select | Product, Architecture, Security, Release, Repository, Platform, Desktop App, Mobile, Managed Service |
| Area | Single select | Setup, Runtime, Provider, Storage, UX, CI, Release, Docs, Platform, Desktop App, Mobile, Managed Service |
| Effort | Single select | XS, S, M, L, XL |
| Target | Text or milestone-derived | v11.2, v11.3, v12.0, v13.0, v14.0, Future Platform Expansion, Architecture Evolution |
| Blocked | Boolean | Whether execution is currently blocked |

Labels remain canonical outside the Project. Avoid duplicating metadata unless a Project field materially improves filtering/grouping.

## Initial/current item mapping

### Current product readiness

- #1, #2, #3 -> v11.2
- #4, #5, #6 -> v11.3
- #7, #8 -> v12.0
- #9 -> project-level tracker

### Architecture evolution

- #19 -> Architecture / Runtime / P1
- #20 -> Architecture / Provider / P1
- #21 -> Architecture / Storage+Provider / P1
- #22 -> Architecture / Runtime / P2
- #23 -> Architecture / Storage / P2
- #24 -> Architecture / CI / P2
- #27 -> Repository/Architecture maintenance / Graphify freshness

### v13.0 — AngysGuard Self-Hosted UX & Linux App

- #30 -> Product/Repository, AngysGuard naming migration
- #31 -> Platform/Product, support matrix + platform-request intake
- #32 -> Desktop App/Product, Linux management UI
- #37 -> Product/Security/Provider, self-hosted bot pairing
- #41 -> Product/Provider/Testing, Bale/Telegram capability parity

### v14.0 — AngysGuard Managed Control

- #38 -> Managed Service/Security/Architecture, onboarding/trust model
- #39 -> Security/Architecture/Platform, passwordless device authorization/local privilege
- #40 -> Managed Service/Product, multi-device account/dashboard
- #42 -> Managed Service/Product/Security, backend + official Bale/Telegram bots

### Future Platform Expansion — Windows & Android

- #33 -> Platform/Architecture, capability adapters
- #34 -> Platform/Desktop App, Windows agent/app
- #35 -> Platform/Mobile, Android companion app
- #36 -> Platform/Mobile/Architecture, Android protected-device research

## Views

### 1. Now

Daily execution.

Filter:

```text
status:Ready,In progress,Review,Validation
```

Group by Status and sort by Priority.

### 2. Current product roadmap

Targets:

```text
v11.2 -> v11.3 -> v12.0
```

This is the release-hardening path and remains higher priority than speculative platform expansion.

### 3. AngysGuard product future

Targets:

```text
v13.0 -> v14.0
```

Show branding, Linux desktop app, self-hosted bot UX, managed-service design, multi-device and official bot work.

### 4. Platform expansion

Filter `Track = Platform`, `Desktop App`, or `Mobile`.

Recommended dependency shape:

```text
#33 platform adapters
  -> #34 Windows
  -> #35 Android companion
       -> #36 Android protected-device research decision
```

Also include platform-request issues (`type:platform-request`) as demand signals, but do not automatically treat them as committed targets.

### 5. Managed service

Filter `Track = Managed Service` or `area:managed-service`.

Recommended order:

```text
#39 + #38 -> #40 -> #42
```

Security/privacy blockers must be visible before implementation or launch.

### 6. Self-hosted bot & providers

Include #37 and #41 plus provider bugs/requests. This view protects self-hosted mode from being neglected after managed mode exists.

### 7. Architecture evolution

Filter `Track = Architecture`.

Current sequence:

```text
#19 -> #20 -> (#21 and #22) -> #23 -> #24
```

Cross-platform #33 should align with the architecture contract rather than introduce a parallel framework.

### 8. Security & hardening

Include `type:security` or Track `Security`. Managed-service credentials/pairing and platform privileged actions belong here too.

### 9. Release readiness

Group by milestone/Target. Include `type:release`, `status:needs-validation`, release milestones, support-matrix work and README/product-presentation drift.

### 10. Platform requests

Filter `type:platform-request`.

Group/sort by requested platform and community demand when useful. A request remains a request until feasibility/security/testing capacity justify promotion into a roadmap issue/milestone.

### 11. Backlog

Filter `Status = Backlog`, group by Track, sort by Priority.

## Umbrella tracker lifecycle

Issue #9 is intentionally a long-lived project tracker, not a single delivery
ticket. Changes to the Project blueprint/bootstrap/docs should reference #9, but
must **not** use `Closes #9` while tracked architecture/product/platform work
remains open.

The tracker is eligible to close only when its completion principles are actually
satisfied, including the repository rename/project setup and the tracked
architecture, self-hosted UX, managed-control, and platform-expansion outcomes.
Closing a milestone issue does not by itself complete #9.

The machine blueprint stores membership/metadata, not a frozen copy of live issue
state. The Project bootstrap safely synchronizes:

- closed issue -> `Status = Done`;
- `status:needs-validation` -> `Status = Validation`;
- `status:blocked` -> `Blocked = Yes`;
- priority/track/area/target from labels and milestone groups.

For other open issues, the bootstrap preserves the existing Project `Status` so
it does not overwrite human-selected Backlog/Ready/In progress/Review states.

## Workflow rules

Recommended automation:

- new repository issue -> Project / Backlog;
- new `type:platform-request` -> Platform Requests view / Backlog;
- assigned/selected work -> Ready;
- linked PR -> In progress or Review;
- merged PR with required manual checks -> Validation;
- issue closed after acceptance criteria -> Done (bootstrap-synchronized);
- `status:blocked` -> Blocked true;
- `status:needs-validation` -> Validation (bootstrap-synchronized).

Do not auto-close an issue merely because a PR merged.

## Planning rules

1. **Security/current product blockers outrank future platform work.** v11.2-v12.0 remains the near-term path.
2. **Future milestones are explicit but not current support claims.** v13/v14 are product targets; Future Platform Expansion is a planning milestone until release-grade support is scheduled.
3. **One issue = one measurable outcome.** Split work when independent acceptance/security/rollback boundaries emerge.
4. **Self-hosted remains first-class.** Managed-service convenience must not make the core agent dependent on startup infrastructure.
5. **No OS passwords through remote services.** #39/ADR 0007 is a hard design constraint.
6. **Platform requests are demand input, not promises.** Promote only after feasibility/security/test capacity review.
7. **Capability differences are honest.** Do not mark Windows/Android/other OS as supported before target-device validation.
8. **Labels classify; Project fields organize; milestones group targets.** Avoid needless duplication.
9. **No hidden work.** Non-trivial work should have an issue.
10. **Validation is a real state.** Hardware/provider/platform checks that CI cannot prove remain visible.

## Native GitHub Project creation/update

GitHub Project v2 write access is user/organization scoped and is not provided by the normal repository-scoped `GITHUB_TOKEN` used by this repository's bootstrap workflow.

When an appropriately scoped token/App is available, use this document as the canonical board specification and add:

- #1-#9;
- #19-#24;
- #27;
- #30-#42;
- future `type:platform-request` issues.

Until then, issues + milestones + labels + project issue #9 + this specification remain the planning source of truth.
