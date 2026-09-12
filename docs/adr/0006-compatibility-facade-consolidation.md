# ADR 0006 — Consolidate compatibility facades before adding new paths

Status: **Proposed**

## Context

The system audit identifies coexistence of old/new warning, system-action, audio, and provider-related paths. Compatibility code is useful during migration but becomes architecture debt when new work continues to depend on it.

## Decision

For each duplicated responsibility:

1. identify the active implementation;
2. document compatibility implementations;
3. prohibit new feature work from extending compatibility paths;
4. migrate callers incrementally;
5. remove the compatibility path only after callers/tests/docs/config migration are complete.

Do not create a third abstraction to bridge two existing abstractions unless there is a concrete migration need.

## Consequences

Positive:

- architecture converges instead of accumulating layers;
- future developers/agents know which path to use;
- deletion becomes evidence-driven.

Tradeoff:

- compatibility modules may remain for several releases while callers migrate.

## Security/privacy

Consolidation must preserve authorization, warning/lock ordering, capture visibility, and fail-closed stop behavior. A cleaner API is not sufficient reason to change these semantics.
