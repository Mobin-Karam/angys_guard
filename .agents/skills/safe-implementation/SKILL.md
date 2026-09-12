---
name: safe-implementation
description: Implement or modify Laptop Guard runtime behavior while preserving authorization, privacy, configuration, and architecture boundaries. Use for features, fixes, refactors, CLI/setup behavior, providers, hardware integrations, or service changes.
---

# Safe implementation

Before editing:

1. Read root `AGENTS.md` and the closest nested `AGENTS.md`.
2. Identify the existing abstraction that owns the behavior. Prefer extending it
   instead of adding a parallel path.
3. Identify whether the change touches authentication, remote control, secrets,
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

- Add success + relevant failure/denial tests.
- Run targeted tests first.
- Invoke/use `test-and-verify` before completion.
- Use `security-review` for sensitive changes.
- State any manual target-device checks still required.
