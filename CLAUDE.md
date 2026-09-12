# Laptop Guard agent instructions

The authoritative repository instructions are in [`AGENTS.md`](./AGENTS.md).
Read and follow that file before changing the project, plus any nested
`AGENTS.md` that applies to the files being edited.

For repository discovery, use Graphify first as defined in
[`docs/GRAPHIFY_NAVIGATION.md`](./docs/GRAPHIFY_NAVIGATION.md). Check graph
freshness, use `graphify query` / `graphify explain` / `graphify path`, then open
only the minimal authoritative files identified by the graph. Do not load the
complete `graphify-out/graph.json` into context. If Graphify cannot be used, make
the fallback search narrow and state why.

Do not duplicate or weaken the security rules in `AGENTS.md`. Preserve owner
authorization/privacy boundaries and never read or expose project/user secrets or
captured evidence.

Reusable workflows: `.agents/skills/`
Graph navigation: `docs/GRAPHIFY_NAVIGATION.md`
Testing guidance: `docs/TESTING.md`
Architecture guidance: `docs/ARCHITECTURE.md`, `docs/architecture/`
