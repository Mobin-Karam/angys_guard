Explain this code/component: <file/symbol>

Follow repository instructions and `docs/GRAPHIFY_NAVIGATION.md`. First check
Graphify freshness and use `graphify explain` plus targeted `query`/`path` calls to
identify callers, callees, dependencies, state/config/storage, tests, and security
boundaries. Then read only the minimal current source/docs needed to verify the
graph.

Cover:
- purpose and responsibility;
- inputs/outputs and important state;
- call flow and dependencies;
- error/failure behavior;
- security/privacy constraints;
- tests that demonstrate behavior;
- common modification points and risks.

Use concrete paths/symbols and mention important inferred graph relationships as
inferred until source-confirmed. Separate current behavior from improvement
suggestions. Do not edit files or load the whole `graphify-out/graph.json`.
