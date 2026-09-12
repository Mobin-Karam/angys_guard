---
name: graphify-navigation
description: Navigate Laptop Guard with Graphify before broad source reads. Use when locating files, tracing callers/dependencies, understanding architecture, estimating change impact, finding tests, or answering repository-structure questions.
---

# Graphify navigation

Use `docs/GRAPHIFY_NAVIGATION.md` as the canonical procedure.

1. Check `graphify-out/GRAPH_REPORT.md` for the graph build commit and compare it
   with the working repository.
2. If the graph is stale and Graphify is available, refresh it with
   `graphify update .` (or the assistant's `/graphify . --update` integration).
3. Ask the smallest useful graph question first:
   - `graphify query "<question>"`
   - `graphify explain "<symbol/concept>"`
   - `graphify path "<A>" "<B>"`
4. Use returned nodes/edges to select only the minimal source/docs/tests needed.
5. Confirm important behavior in current source; Graphify is navigation evidence,
   not final authority.
6. For change-impact/removal/security work, verify relevant callers/dependencies
   in source/tests before editing.
7. Do not load the full `graphify-out/graph.json` into the conversation.
8. If Graphify is missing/stale and cannot be refreshed, fall back to narrow
   direct search and state that fallback explicitly.

Return a compact navigation handoff:

```text
Graph freshness:
Query/explain/path used:
Relevant nodes/edges:
Owning paths/symbols:
Tests/docs to inspect:
Uncertain/inferred relationships:
Next minimal read/action:
```

Never query/read secret stores, captured evidence, credentials, or protected
private data while navigating.
