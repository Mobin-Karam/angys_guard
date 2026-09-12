# GitHub Project management

This document defines the canonical GitHub Project v2 structure for Laptop Guard.

The repository already tracks execution through issues, milestones, labels, roadmap docs, and issue #9. A GitHub Project board should visualize that same data rather than invent a second planning system.

## Project

**Name:** `Laptop Guard — Product & Architecture Delivery`

**Purpose:** one board for product-readiness work, architecture evolution, security/hardening, and release preparation.

Repository issues remain the source of truth for requirements and acceptance criteria. Milestones remain the source of truth for release grouping.

## Fields

Use these Project fields:

| Field | Type | Values / purpose |
|---|---|---|
| Status | Single select | Backlog, Ready, In progress, Review, Validation, Done |
| Priority | Single select | P0, P1, P2, P3 |
| Track | Single select | Product, Architecture, Security, Release, Repository |
| Area | Single select | Setup, Runtime, Provider, Storage, UX, CI, Release, Docs |
| Effort | Single select | XS, S, M, L, XL |
| Target | Text or milestone-derived | v11.2, v11.3, v12.0, Architecture Evolution |
| Blocked | Boolean | Whether execution is currently blocked |

Do not duplicate issue labels into every custom field unless the Project view benefits from filtering/grouping by that field. Labels remain useful outside Projects and should stay canonical for issue taxonomy.

## Initial item mapping

### Product readiness

- #1, #2, #3 -> Track: Product/Security, Target: v11.2
- #4, #5, #6 -> Track: Product, Target: v11.3
- #7, #8 -> Track: Release/Product, Target: v12.0
- #9 -> Track: Repository, project-level tracker

### Architecture evolution

- #19 -> Track: Architecture, Priority P1, Runtime
- #20 -> Track: Architecture, Priority P1, Provider
- #21 -> Track: Architecture, Priority P1, Storage/Provider
- #22 -> Track: Architecture, Priority P2, Runtime
- #23 -> Track: Architecture, Priority P2, Storage
- #24 -> Track: Architecture, Priority P2, CI

## Views

Create these views.

### 1. Now

Purpose: daily execution.

Filter:

```text
status:Ready,In progress,Review,Validation
```

Group by `Status`, sort by `Priority`.

### 2. Product roadmap

Show product issues only. Group by milestone/Target, then sort by Priority.

Expected sequence:

```text
v11.2 -> v11.3 -> v12.0
```

### 3. Architecture evolution

Filter `Track = Architecture`.

Recommended sequence:

```text
#19 -> #20 -> (#21 and #22) -> #23 -> #24
```

Use the dependency notes in the issues and `docs/architecture/EVOLUTION_PLAN.md`; the board order is visual guidance, not a replacement for those constraints.

### 4. Security & hardening

Filter issues carrying `type:security` or Track `Security`.

Use this view for credential cleanup, authorization/privacy changes, provider security, and release-blocking security work.

### 5. Release readiness

Group by Target/milestone. Include issues with `type:release`, `status:needs-validation`, or release milestones.

This view should make unresolved blockers visible before tagging a new release.

### 6. Backlog

Filter `Status = Backlog`. Group by Track, sort by Priority.

## Workflow rules

Recommended automation:

- new repository issue -> add to Project with Status `Backlog`;
- issue assigned / explicitly selected for work -> `Ready`;
- linked PR opened -> `In progress` or `Review` depending on team preference;
- PR merged but manual target-device checks remain -> `Validation`;
- issue closed -> `Done`;
- `status:blocked` label -> set Blocked true;
- `status:needs-validation` -> Status `Validation`.

Do not auto-close issues merely because a PR merged unless the issue's acceptance criteria are actually complete.

## Planning rules

1. **Product/security blockers outrank architecture cleanup.** Architecture work may proceed in parallel only when it does not destabilize the active release milestone.
2. **One issue = one measurable outcome.** Split work when independent acceptance criteria or rollback boundaries emerge.
3. **Milestones are release commitments, not general categories.** The architecture milestone is intentionally separate because it spans releases.
4. **Labels classify; Project fields organize execution; milestones group release targets.** Avoid using all three for the same purpose unless it materially improves visibility.
5. **No hidden work.** Non-trivial work should have an issue before implementation unless it is an immediate small fix discovered inside an existing issue/PR.
6. **Validation is a real state.** Hardware/session/provider checks that cannot run in CI should prevent premature completion when they are part of acceptance criteria.

## Creating the native Project

GitHub Project v2 creation requires user/organization-level Projects write permission. The normal repository-scoped `GITHUB_TOKEN` cannot create/manage the Project.

When an appropriately scoped token or GitHub App is available, create the project using this document exactly as the board specification and add issues #1-#9 and #19-#24 as the initial items.
