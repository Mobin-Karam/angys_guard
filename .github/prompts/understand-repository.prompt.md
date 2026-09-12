Understand this repository before proposing changes.

Follow repository instructions and `docs/GRAPHIFY_NAVIGATION.md`. Do not start by
reading the repository broadly.

1. Check Graphify freshness.
2. Use `graphify query`, `graphify explain`, and `graphify path` to map product
   entry points, major communities, core abstractions, state/config/storage,
   external boundaries, security boundaries, tests, docs, CI/release flow, and
   current hotspots.
3. Open only the minimal authoritative source/docs needed to verify the graph.
4. Distinguish extracted graph relationships from inferred assumptions.
5. If Graphify is unavailable/stale and cannot be refreshed, use narrow fallback
   search and say why.

Return a concise map of product/purpose, primary flows, entry points, module
ownership, data/config/state flow, external dependencies, trust boundaries, test
strategy, known risks, and where a new contributor should start.

Include Graphify freshness and the key queries/nodes/paths used. Do not edit files
or load the complete `graphify-out/graph.json` into context.
