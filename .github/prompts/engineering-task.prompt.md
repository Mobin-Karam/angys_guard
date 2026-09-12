Handle this engineering task: <task>

First follow repository instructions and `docs/GRAPHIFY_NAVIGATION.md`. Classify
the task before editing: investigation, feature work, bug fix, refactor,
security/privacy, test/CI, documentation, dependency/config migration, or release.

Then:
1. Restate the goal and acceptance criteria.
2. Check Graphify freshness and use query/explain/path to find owning modules,
   callers/dependencies, tests/docs, state/config/storage, and trust boundaries.
3. Open only the minimal current source/tests/docs needed to verify that graph map.
4. List material risks, compatibility/security/privacy concerns, inferred edges,
   and unknowns.
5. For non-trivial work, produce the smallest safe plan before editing.
6. Implement only the necessary change when implementation is requested.
7. Add/update focused graph-connected tests and run applicable verification.
8. Review the final diff plus graph-identified impact surface for regressions,
   accidental scope expansion, and secrets.
9. Refresh Graphify after material relationship changes when available.
10. Report rationale/root cause, files changed, Graphify freshness/queries, tests,
    manual validation, and blockers.

Do not load the complete graph.json into context or perform unrelated cleanup,
destructive Git, release, or deployment actions unless explicitly requested.
