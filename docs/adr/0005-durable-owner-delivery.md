# ADR 0005 — Durable owner delivery for important notifications

Status: **Proposed**

## Context

Local security response and event persistence must remain correct when the remote provider/network is unavailable. The repository already has an SQLite outbox primitive, but current sends are not uniformly routed through it.

## Decision

Important owner notifications should conceptually follow:

```text
application event -> durable outbox -> delivery worker -> RuntimeApi -> ack/retry/fail state
```

Not every low-value UI message must be durable. The application should classify which messages require durable delivery.

## Consequences

Positive:

- transient provider outages do not silently lose important notifications;
- retry behavior becomes bounded and observable;
- security events remain independent from provider availability.

Tradeoffs:

- queue lifecycle/retry policy requires explicit ownership;
- stale media/evidence references must be handled safely.

## Security/privacy

Outbox payloads can contain sensitive captions/media references. Storage permissions, retention, redaction, and terminal-failure handling must be part of the design.
