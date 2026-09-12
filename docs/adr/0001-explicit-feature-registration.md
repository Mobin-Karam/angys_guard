# ADR 0001 — Explicit feature registration

Status: **Accepted**

## Context

Laptop Guard exposes security-sensitive commands/callbacks. Automatic plugin discovery would allow local files/import side effects to become executable extension points and would make ownership/conflicts less predictable.

## Decision

Features are registered explicitly through `FeatureManager`.

- feature names, command aliases, and callback prefixes are unique;
- conflicts fail fast;
- feature start/stop order is deterministic;
- there is no filesystem/module auto-discovery;
- new command/callback functionality should prefer focused feature modules over extending a central legacy dispatcher.

## Consequences

Positive:

- clear ownership;
- deterministic startup;
- easier review/testing;
- smaller attack surface.

Tradeoff:

- adding a feature requires an explicit registration change.

That tradeoff is desirable for a security product.

## Security/privacy

Do not replace explicit registration with arbitrary dynamic imports, runtime-downloaded plugins, remote code modules, or script execution.
