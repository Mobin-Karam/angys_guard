# ADR 0004 — Layered modular monolith with ports/adapters

Status: **Proposed**

## Context

`LaptopGuard` currently coordinates many responsibilities while newer seams (`RuntimeApi`, features, runtime state, event store) already provide a path toward lower coupling. A rewrite would create unnecessary security/regression risk.

## Decision

Evolve incrementally toward a modular monolith with:

- delivery/entry-point layer;
- application/use-case coordination;
- infrastructure-independent domain decisions where valuable;
- application-owned ports;
- concrete infrastructure adapters;
- one explicit composition root.

Dependencies point inward. Infrastructure technologies do not become dependencies of core decisions merely for convenience.

This decision does not require reorganizing all files into matching folders immediately.

## Consequences

Positive:

- safer incremental extraction;
- easier isolated testing;
- clearer technology/security boundaries;
- fewer duplicate implementations.

Tradeoffs:

- temporary adapters/facades may coexist during migration;
- some code remains structurally mixed until its slice is extracted.

## Migration

Follow `architecture/EVOLUTION_PLAN.md`; extract behavior by flow/use case, not by moving files for appearance.
