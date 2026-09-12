Map the architecture relevant to this goal: <goal>

Do not edit files. Follow repository instructions and
`docs/GRAPHIFY_NAVIGATION.md`.

Check Graphify freshness, then use `graphify query`, `graphify explain`, and
`graphify path` to trace the smallest relevant architecture neighborhood before
opening broad source.

Identify and then confirm in current source/docs:
- entry points and execution path;
- owning modules/classes/functions;
- interfaces/protocols/extension points;
- state/config/storage boundaries;
- external/network/OS/hardware boundaries;
- callers and downstream dependents;
- authorization/security/privacy checks;
- tests and docs connected to the path;
- likely change points and areas that should not be touched.

Report the key Graphify nodes/edges/paths and whether relationships are extracted
or inferred when material. End with the smallest safe implementation boundary and
required verification. Do not load raw `graphify-out/graph.json` into context.
