# Architecture Decision Records (ADRs)

ADRs record architectural decisions that should survive code movement and personnel/tool changes.

## Status values

- **Proposed** — design direction not yet implemented/approved as active architecture.
- **Accepted** — current architecture should follow this decision.
- **Deprecated** — retained for history; new work must not follow it.
- **Superseded** — replaced by another ADR.

## Rules

Create an ADR when a change materially affects dependency direction, security boundaries, persistence ownership, extension mechanisms, provider strategy, concurrency, device/account pairing, local privilege, or a difficult-to-reverse platform choice.

Proposed ADRs are not proof that a feature/platform is shipped. Runtime/product changes still require normal issues, implementation, tests and review.

## Index

- `0001-explicit-feature-registration.md` — **Accepted** — explicit feature registration; no filesystem plugin auto-discovery.
- `0002-runtime-api-port.md` — **Accepted** — runtime owner communication through `RuntimeApi`.
- `0003-shared-runtime-state.md` — **Accepted** — shared persisted runtime control state.
- `0004-layered-modular-monolith.md` — **Proposed** — incremental modular-monolith / ports-and-adapters direction.
- `0005-durable-owner-delivery.md` — **Proposed** — durable outbox-backed important owner delivery.
- `0006-compatibility-facade-consolidation.md` — **Proposed** — converge duplicate/compatibility facades.
- `0007-passwordless-device-pairing.md` — **Accepted** — remote pairing uses device-scoped credentials; protected-device OS passwords never cross bot/backend boundaries and local privilege remains platform-native.
- `0008-cross-platform-capability-adapters.md` — **Proposed** — define narrow platform capability ports/adapters before Windows/Android expansion.
