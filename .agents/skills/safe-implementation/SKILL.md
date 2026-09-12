---
name: safe-implementation
description: Implement or modify Laptop Guard runtime behavior while preserving authorization, privacy, configuration, and architecture boundaries. Use for features, fixes, refactors, CLI/setup behavior, providers, hardware integrations, or service changes.
---

# Safe implementation

Before editing:

1. Read root `AGENTS.md`, the closest nested `AGENTS.md`, and
   `docs/GRAPHIFY_NAVIGATION.md`.
2. Check Graphify freshness. Use `graphify query` / `explain` / `path` to identify
   the existing owner, callers/dependencies, connected tests, config/state/storage,
   and side-effect boundaries. Use a `navigator` handoff when useful.
3. Confirm the graph-identified scope in current source; do not load raw
   `graphify-out/graph.json` into context.
4. Prefer the existing owning abstraction rather than adding a parallel path.
5. Identify whether the change touches authentication, remote control, secrets,
   capture/input monitoring, subprocesses, network exposure, or OS lock/service
   behavior. If yes, include a security review.

Implementation rules:

- Keep changes small and explicit.
- Preserve `RuntimeApi`, explicit feature registration, and shared state patterns.
- Fail closed for authorization ambiguity.
- Make optional hardware/native integrations degradable and actionable.
- Keep time/size/retry/queue work bounded.
- Never add generic remote command execution or hidden capture.
- Never log secrets or private captured evidence.
- Prefer existing dependencies; justify any new production dependency.

Verification:

- Use Graphify to locate the closest relevant tests and impact surface.
- Add success + relevant failure/denial tests.
- Run targeted tests first.
- Invoke/use `test-and-verify` before completion.
- Use `security-review` for sensitive changes.
- Refresh Graphify after material relationship changes when available.
- State graph freshness and any manual target-device checks still required.
