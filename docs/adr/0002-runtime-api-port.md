# ADR 0002 — Runtime owner-transport port

Status: **Accepted**

## Context

Owner communication needs to support provider/network variation and a local/offline runtime without spreading concrete HTTP/provider clients through feature/application code.

## Decision

Runtime owner communication depends on the `RuntimeApi` contract. Concrete provider/local implementations are selected at construction time.

Application/feature code should not instantiate Requests/httpx/provider clients directly.

## Consequences

Positive:

- local/no-network operation is possible;
- provider behavior is substitutable/testable;
- proxy/base URL/provider selection has a clear construction boundary.

Current state:

- setup validation, Doctor and runtime construct Bale/Telegram through the same
  provider factory and `HttpBotProvider`;
- provider-specific payload differences are represented by provider profiles;
- `BaleApi` is compatibility-only.

Future work should extend this boundary rather than create another client
abstraction.

## Security/privacy

Provider data is untrusted input. Tokens remain configuration/secrets concerns and must not be exposed through general feature interfaces.
