Investigate this bug without guessing or immediately patching: <symptom>

Follow repository instructions, `docs/GRAPHIFY_NAVIGATION.md`, and relevant
bug/testing guidance. Do not request or expose secrets/private data.

Workflow:
1. Restate observed vs expected behavior and material environment/preconditions.
2. Check Graphify freshness.
3. Use Graphify to connect the symptom/error/entry point to likely owning symbols,
   callers/dependencies, state/config/storage, side effects, and connected tests.
4. Open only the minimal current source/tests needed to verify those graph paths.
5. Reproduce with the smallest deterministic case when possible.
6. Narrow competing hypotheses using evidence/logs/tests/state rather than broad edits.
7. Identify the root cause or clearly state missing evidence.
8. Propose the smallest safe fix and regression test.

Report the Graphify queries/nodes/paths used and mark inferred relationships until
source-confirmed. If Graphify cannot be used, state the narrow fallback. Do not edit
code until the root cause is sufficiently narrowed unless instrumentation itself is
the necessary next step. Do not load raw graph.json into context.
