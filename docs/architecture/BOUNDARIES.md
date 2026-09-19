# Architecture boundaries and dependency rules

This file defines the dependency rules future code changes should move toward. These are design constraints, not a claim that every current module already complies.

## Dependency direction

```text
Delivery  ---> Application ---> Domain
                 |
                 v
               Ports <--- Infrastructure adapters
```

The composition root may depend on all layers only to construct and wire objects.

## Boundary table

| Area | May depend on | Must avoid depending on directly |
|---|---|---|
| Domain decisions/models | stdlib, domain types | Requests/httpx, SQLite, OpenCV, subprocess, desktop/session APIs, bot payload formats |
| Application/use cases | domain, ports, small shared types | concrete HTTP clients, concrete databases, native tools |
| Feature modules | feature contracts, application ports/capabilities | `BaleApi`, Requests/httpx, unrestricted `LaptopGuard` internals, shell commands |
| Delivery/CLI/API/update parsing | application interfaces, validation types | raw storage schema, hardware implementation details |
| Infrastructure adapters | port interfaces, config needed to construct adapter | unrelated application orchestration |
| Composition | all concrete implementations needed for wiring | business decisions beyond selecting/wiring components |

## Current architectural seams to preserve

- `RuntimeApi` is the runtime owner-transport abstraction.
- `FeatureManager` is the explicit command/callback registry.
- `FeatureHost` is a constrained capability boundary.
- `GuardRuntimeState` is the live facade over persisted runtime control state.
- `EventStore` is the durable SQLite event/outbox primitive.

New work should strengthen these seams instead of bypassing them.

## Current exceptions / migration areas

The current codebase still contains intentional transitional coupling:

- `LaptopGuard` owns many application and infrastructure responsibilities;
- warning and system-action compatibility layers coexist;
- some direct media/system helpers are constructed inside the guard;
- event persistence exists beside delivery logic rather than as a unified event/outbox workflow.

Treat these as migration targets, not examples to copy.

## Feature boundary rules

A feature may:

- register explicit commands/callback prefixes;
- use a narrow host/context capability;
- emit events through an event capability;
- request owner replies/files through a messaging capability;
- use feature-specific ports that are explicitly injected.

A feature must not:

- obtain the raw bot token;
- instantiate HTTP clients;
- execute arbitrary command strings;
- inspect unrelated config/secrets;
- directly mutate another feature's internal state;
- import a compatibility facade merely because it is convenient;
- use global service lookup/discovery.

## State boundary rules

Every mutable value should have one authoritative owner.

Before adding state, classify it as:

- durable configuration;
- durable runtime control state;
- volatile process state;
- event history;
- delivery/outbox state;
- evidence/media metadata.

Do not add a second persistence representation without documenting synchronization and failure behavior.

## Time boundary

Persisted/cross-process timestamps use wall-clock Unix time. Process-local durations may use a monotonic clock.

Future extraction of cooldown/grace/timeout decisions should prefer an injectable clock abstraction when doing so materially improves deterministic tests.

## System action boundary

Lock/unlock/power/suspend actions are security-sensitive infrastructure operations.

Application code should request a fixed semantic action, not build command strings. Adapters choose safe platform commands. Failure should return a stable result that includes enough detail for diagnostics without exposing secrets.

## Capture boundary

Camera/screen/audio capture must be explicit, bounded, and privacy-aware.

Application/domain logic decides **whether** capture is permitted/requested. Infrastructure decides **how** to capture on the current environment. Capability detection and actionable failure belong near the adapter/doctor boundary.

## Transport boundary

Application/features should depend on a stable messaging interface. Provider-specific update/file formats are parsed at adapter/delivery edges.

Retries, backoff, provider errors, upload behavior, and proxy handling converge
behind `HttpBotProvider`. Bale/Telegram request differences live in
`ProviderProfile`; application/features continue to depend only on `RuntimeApi`.

## Persistence boundary

Repositories expose semantic operations, not SQL/file-layout details. Configuration migrations remain deterministic/idempotent. Security events must not be lost merely because remote delivery fails.

## Import review heuristic

When reviewing a new import, ask:

- Does this import cross from core/application into infrastructure?
- Is a third-party/native library leaking into a core decision module?
- Is a feature reaching around a port to a concrete implementation?
- Is a compatibility module becoming a new dependency?

If yes, introduce or reuse a narrow boundary instead of accepting the dependency by default.

## Architecture exceptions

Temporary exceptions are allowed during incremental migration if they are:

1. documented in the PR;
2. narrower than the existing coupling;
3. covered by tests;
4. associated with a migration/removal follow-up;
5. not security-boundary regressions.

An exception should not become the new preferred pattern simply because it exists in `main`.
