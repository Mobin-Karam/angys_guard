# Laptop Guard agent instructions

Use [`AGENTS.md`](./AGENTS.md) as the authoritative project instruction file.
Also follow the nearest nested `AGENTS.md` for the area being changed.

For repository discovery, follow [`docs/GRAPHIFY_NAVIGATION.md`](./docs/GRAPHIFY_NAVIGATION.md)
first: check graph freshness, use `graphify query`, `graphify explain`, or
`graphify path`, then inspect only the minimal source/docs/tests returned by the
graph. Do not load the full `graphify-out/graph.json` into context. Use narrow
direct search only when Graphify is unavailable, stale and cannot be refreshed,
or insufficient for the exact question.

Do not duplicate project policy here. Preserve owner authorization, privacy,
secret handling, bounded capture/control behavior, explicit feature registration,
and the existing runtime abstractions.

Reusable workflows: `.agents/skills/`
Graph navigation: `docs/GRAPHIFY_NAVIGATION.md`
Verification: `docs/TESTING.md`
Architecture: `docs/ARCHITECTURE.md`, `docs/architecture/`
