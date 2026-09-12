# Laptop Guard AI instructions

`AGENTS.md` is the authoritative repository guide. Follow it before proposing or
editing code. Also follow the closest nested `AGENTS.md` for runtime/tests/docs.

Core rules for this security project:

- Security and privacy take precedence over convenience or feature breadth.
- Preserve owner authorization, pairing, confirmation, stop, and unlock gates.
- Never add arbitrary remote shell/exec/eval/filesystem control or hidden capture.
- Never read/log/print `.env`, `secrets.json`, credentials, stop PIN material, or
  captured evidence.
- Keep local control APIs authenticated and loopback-only by default.
- Prefer existing `RuntimeApi`, `FeatureManager`, `GuardRuntimeState`, and narrow
  services instead of parallel mechanisms.
- Keep optional hardware/native integrations lazy and degradable.
- Add focused success/failure/authorization tests for changed behavior.
- Preserve unrelated working-tree changes; never use destructive Git recovery.
- Before completion run the applicable checks from `docs/TESTING.md` and identify
  any manual target-device validation still required.

Useful project workflows are documented in `.agents/skills/`. Codex-specific
subagents/hooks live under `.codex/`.
