Navigate this repository for: <question or goal>

Use Graphify first, following `docs/GRAPHIFY_NAVIGATION.md` and repository
instructions. Do not start with broad grep/search or large file reads.

1. Check graph freshness.
2. Use `graphify query`, `graphify explain`, and/or `graphify path` to identify the
   smallest relevant nodes, edges, owning paths, tests, and docs.
3. Open only the minimal authoritative source/docs needed to confirm the graph.
4. Distinguish extracted vs inferred relationships when material.
5. If Graphify is unavailable/stale and cannot be refreshed, use a narrow fallback
   search and say why.

Return a compact map of relevant paths/symbols, relationships, tests/docs, and the
next minimal action. Do not edit files unless the request separately asks for an
implementation after navigation.
