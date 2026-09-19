# Architecture evolution plan

This plan improves structure without a flag-day rewrite. Each phase should be behavior-preserving unless the issue explicitly includes a product change.

## Ground rules

- Do not reorganize the whole package at once.
- Prefer extraction behind tests over renaming/moving files for appearance.
- Keep one source of truth per responsibility.
- New work uses active architecture paths; compatibility paths receive only fixes/migration work.
- Security/privacy behavior is an invariant, not a cleanup task.
- Every architecture phase must have rollback and verification criteria.

## Phase 0 — Architecture contract (documentation)

Status: **in progress / documentation-only**.

Deliverables:

- canonical `ARCHITECTURE.md`;
- dependency/boundary rules;
- runtime/security flow diagrams;
- ADR process;
- staged migration backlog.

Exit criteria:

- contributors/AI agents can identify correct layer/owner before coding;
- architecture decisions distinguish accepted current patterns from proposed target patterns.

## Phase 1 — Reduce `LaptopGuard` orchestration load

Goal: make `LaptopGuard` a composition/runtime shell rather than the owner of every behavior.

Candidate slices, one at a time:

1. owner authorization/command dispatch orchestration;
2. intrusion-response orchestration;
3. protected-stop state machine;
4. evidence/notification orchestration;
5. lifecycle worker ownership.

Approach:

- extract a small application service/use case;
- define only the ports needed by that slice;
- keep old public behavior and entry points;
- route the existing guard method through the extracted service;
- prove parity with focused tests before the next extraction.

Do not move all methods merely to make `guard.py` shorter.

Exit criteria:

- major flows can be tested without constructing all hardware/network adapters;
- `LaptopGuard` primarily wires, starts/stops, and delegates.

## Phase 2 — Consolidate communication/provider adapters

Status: **completed for the active Bale/Telegram/local transport path**.

Goal: one runtime messaging abstraction with provider-specific adapters.

The active setup/Doctor/runtime paths now share `providers.build_provider()` and
`HttpBotProvider`, with provider differences represented by `ProviderProfile`.
The older `BaleApi` module remains a compatibility-only facade and must not gain
new behavior.

Target:

- stable owner messaging/update/file port;
- provider adapters translate errors/payloads;
- proxy/retry/timeout/upload policy has one owner;
- local/offline adapter remains first-class;
- setup validation uses the same provider capability path where practical.

Exit criteria:

- no feature/application code imports Requests/httpx/provider client classes;
- duplicated retry/upload/error mapping is removed or marked compatibility-only.

## Phase 3 — Consolidate system/warning/media facades

Goal: one active semantic interface per side-effect category.

Targets:

- system actions;
- warning presentation;
- audio/capture abstractions where duplicate paths remain.

Process:

1. identify active vs compatibility implementation;
2. move callers to the active port/facade;
3. freeze compatibility surface;
4. remove compatibility code only after import/caller/test/doc verification.

Exit criteria:

- one documented active path for each responsibility;
- compatibility modules have explicit deprecation/removal status.

## Phase 4 — Reliable delivery and storage lifecycle

Goal: make persistence/delivery behavior explicit under network/storage failure.

Work:

- route important failed owner notifications through the durable outbox;
- define retry/backoff/terminal-failure semantics;
- implement evidence/event retention and quotas with safe defaults;
- define evidence metadata ownership and orphan cleanup;
- make disk-pressure behavior observable.

Exit criteria:

- remote outage does not lose security events;
- unbounded evidence growth is prevented;
- retries are bounded and diagnosable.

## Phase 5 — Refine feature/application boundaries

Goal: new commands/callbacks become focused features/use cases instead of extending central dispatch code.

Work:

- continue extraction by cohesive capability, not file size;
- prevent `FeatureHost` from becoming a service locator;
- use feature-specific contexts/ports for richer features;
- centralize shared policy rather than duplicate it across features.

Exit criteria:

- most user-facing command behavior has a clear owner;
- adding a feature normally means one focused module + explicit registration + tests.

## Phase 6 — Boundary enforcement

Goal: prevent architecture drift automatically.

Possible lightweight mechanisms:

- import/dependency tests for forbidden directions;
- static checks that features do not import concrete provider clients;
- checks that compatibility modules are not imported by new active modules;
- architecture review checklist in PRs;
- targeted type checking for port/protocol boundaries.

Avoid heavy architecture frameworks unless drift becomes a real maintenance problem.

Exit criteria:

- CI catches common boundary violations;
- architecture rules are executable enough to prevent accidental regression.

## Phase 7 — Operational maturity

Goal: architecture supports long-running production-like usage.

Work:

- structured/redacted logging;
- stable error taxonomy;
- health/capability reporting by subsystem;
- metrics suitable for local diagnostics without leaking private data;
- clean-install/package matrix and target-device validation evidence.

## Suggested issue order

High value / low behavior risk:

1. define active/compatibility ownership for warning/system/audio paths;
2. design intrusion-response application service boundary;
3. design provider consolidation boundary;
4. design outbox delivery policy;
5. design retention/quota policy;
6. add import-boundary checks after the target dependencies are real.

Do not begin with directory reshuffling.

## Refactor acceptance template

Every architecture refactor issue should state:

- behavior that must remain identical;
- current owner/call path;
- target boundary/port;
- security/privacy invariants;
- config/state migration impact;
- focused regression tests;
- target-device validation affected;
- compatibility path created/removed;
- rollback strategy.
