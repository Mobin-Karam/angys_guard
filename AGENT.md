# AI agent compatibility note

The authoritative project instructions are in [`AGENTS.md`](./AGENTS.md).

OpenAI Codex reads `AGENTS.md` automatically. This singular `AGENT.md` exists
only for tools or humans that look for the singular filename. Do not duplicate
project rules here; keeping one source of truth prevents instruction drift.

For Codex-specific configuration, subagents, and hooks, see `.codex/`.
For reusable project skills, see `.agents/skills/`.
