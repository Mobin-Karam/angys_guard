# Architecture Decision Records (ADRs)

ADRs record architectural decisions that should survive code movement and personnel/tool changes.

## Status values

- **Proposed** — design direction not yet implemented/approved as the active architecture.
- **Accepted** — current architecture should follow this decision.
- **Deprecated** — retained for historical context; new work must not follow it.
- **Superseded** — replaced by another ADR.

## Rules

Create an ADR when a change materially affects dependency direction, security boundaries, persistence ownership, extension mechanism, transport/provider strategy, concurrency model, or a difficult-to-reverse platform choice.

Do not create ADRs for ordinary implementation details.

An ADR contains:

- context/problem;
- decision;
- consequences/tradeoffs;
- security/privacy implications;
- migration/compatibility notes;
- status.

Accepted ADRs describe constraints for new work. Proposed ADRs are not permission to change runtime behavior without a normal issue/PR/review.

## Index

- `0001-explicit-feature-registration.md` — Accepted
- `0002-runtime-api-port.md` — Accepted
- `0003-shared-runtime-state.md` — Accepted
- `0004-layered-modular-monolith.md` — Proposed
- `0005-durable-owner-delivery.md` — Proposed
- `0006-compatibility-facade-consolidation.md` — Proposed
