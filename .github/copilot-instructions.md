# Laptop Guard AI instructions

`AGENTS.md` is the authoritative repository guide. Follow it before proposing or
editing code. Also follow the closest nested `AGENTS.md` for runtime/tests/docs.

## Graphify-first repository discovery

Before broad grep/search or opening large source ranges, follow
`docs/GRAPHIFY_NAVIGATION.md`:

1. check graph freshness in `graphify-out/GRAPH_REPORT.md`;
2. use `graphify query`, `graphify explain`, or `graphify path` to find the
   smallest relevant nodes/files/tests/docs;
3. open only those authoritative files/ranges;
4. verify important conclusions against current source.

Do not load the complete `graphify-out/graph.json` into chat context. If the graph
is stale and can be refreshed, run `graphify update .` first. Use narrow direct
search only when Graphify is unavailable/stale-and-unrefreshable/insufficient,
and state the fallback.

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
- Before completion run the applicable checks from `docs/TESTING.md`, refresh the
  graph after material relationship changes when possible, and identify any manual
  target-device validation still required.

Useful project workflows are documented in `.agents/skills/`; use
`$graphify-navigation` when discovery/impact mapping is the main task.
Codex-specific subagents/hooks live under `.codex/`.

Reusable task prompts live under `.github/prompts/`, including
`graphify-navigation.prompt.md`. Prompt files remain generic; project-specific
navigation/security policy stays in `AGENTS.md` and canonical docs.
