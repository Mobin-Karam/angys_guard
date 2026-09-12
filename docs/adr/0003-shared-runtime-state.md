# ADR 0003 — Shared persisted runtime control state

Status: **Accepted**

## Context

CLI actions and the running guard both need to observe owner-controlled state such as armed/disarmed/grace timing. Separate in-memory copies caused drift.

## Decision

Runtime control state uses `RuntimeStateStore`, with `GuardRuntimeState` as the live facade for the running process.

Persisted cross-process timing uses wall-clock Unix timestamps.

## Consequences

Positive:

- CLI and guard share one source of truth;
- state survives process boundaries;
- control updates can be observed without inventing another IPC channel.

Tradeoffs:

- live refresh semantics must remain explicit;
- not every configuration value should be treated as live runtime state.

## Security/privacy

State mutation must preserve authorization at the delivery/application boundary. Sharing storage does not imply every caller is allowed to mutate every field.
