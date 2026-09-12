# Runtime code instructions

These rules apply under `laptop_guard/` in addition to the repository root
`AGENTS.md`.

## Navigate before reading broadly

For runtime discovery, follow `docs/GRAPHIFY_NAVIGATION.md` first. Use Graphify to
locate the owning class/function, callers, downstream dependencies, tests, config,
state/storage links, and side-effect adapters before opening broad source ranges.

Typical starting questions:

```bash
graphify query "where is <runtime behavior> implemented?"
graphify query "what depends on <symbol>?"
graphify path "<input/command source>" "<side effect/store>"
graphify explain "<runtime symbol>"
```

Then inspect only the returned runtime paths/tests. For security-sensitive changes
and deletions, confirm graph relationships against current source before editing.
If Graphify is stale/unavailable and cannot be refreshed, use narrow direct search
and state the fallback.

## Design rules

- Keep `guard.LaptopGuard` orchestration-oriented; move new capabilities into
  focused services/features instead of making the guard class larger.
- Bot-facing features belong under `features/` and must be registered explicitly.
- Preserve the `RuntimeApi` abstraction for Telegram/Bale/local transports.
- Use `GuardRuntimeState` / `RuntimeStateStore` for shared runtime state.
- Prefer dataclasses/protocols and narrow dependencies over implicit globals.
- Keep native/hardware imports lazy when they are optional.

## Security-sensitive areas

Treat these as high-risk changes requiring targeted tests and a security review:

- authentication, owner pairing, stop/unlock authorization;
- remote commands/callbacks and local control API;
- camera, microphone, screen capture, input monitoring, and warning surfaces;
- subprocess/process control, autostart/systemd, and OS lock handling;
- secret/config storage and migration;
- network transports, proxy behavior, media transfer, and offline queues.

Never expose a generic command runner, arbitrary filesystem access, secret
contents, or hidden capture through a feature or API.

## Error handling

- Expected dependency/hardware/provider/configuration failures should become
  actionable user-facing errors, not raw tracebacks.
- Fail closed on authorization ambiguity.
- Time-bound network/hardware/process operations.
- Do not silently discard security events; use the existing event/outbox paths.

## Testing expectations

For changed behavior, cover the success path and at least the relevant failure,
authorization, timeout, or unavailable-backend path. Hardware code needs a fake
backend/unit path plus explicit manual target-device validation notes.

After material runtime relationship changes, refresh Graphify when available so
future navigation reflects the new call/dependency graph.
