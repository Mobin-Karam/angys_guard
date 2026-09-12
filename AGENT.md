# AI agent compatibility note

The authoritative project instructions are in [`AGENTS.md`](./AGENTS.md).

OpenAI Codex reads `AGENTS.md` automatically. This singular `AGENT.md` exists
only for tools or humans that look for the singular filename. Do not duplicate
project rules here; keeping one source of truth prevents instruction drift.

Before broad repository discovery, follow the Graphify-first workflow in
[`docs/GRAPHIFY_NAVIGATION.md`](./docs/GRAPHIFY_NAVIGATION.md): check freshness,
query/explain/path first, then read only the minimal authoritative files returned
by the graph.

For Codex-specific configuration, subagents, and hooks, see `.codex/`.
For reusable project skills, see `.agents/skills/`.
