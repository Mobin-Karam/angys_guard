# Documentation instructions

These rules apply under `docs/` in addition to the root `AGENTS.md`.

## Navigate documentation with Graphify first

For questions such as "where is this documented?", "which docs mention/own this
concept?", or "what docs/source/tests connect to this behavior?", use Graphify
first following `GRAPHIFY_NAVIGATION.md`. Query/explain/path should narrow the
relevant document sections before broad documentation reads.

Do not load raw `graphify-out/graph.json` into context. If the graph is stale and
can be refreshed, refresh it first. Direct current docs/source remain authoritative
when generated graph output disagrees.

## Documentation rules

- Document current behavior, not planned behavior, unless the section is clearly
  labeled roadmap/proposal.
- Keep commands copy-pasteable and prefer safe, non-destructive examples.
- Never include real credentials, chat IDs, private IPs, captured media, or
  secret-store contents in examples.
- Keep security/privacy limitations explicit, especially for camera, microphone,
  screen/input monitoring, remote unlock/control, and network providers.
- When code changes user-visible setup, CLI commands, dependencies, architecture,
  target-device requirements, or release behavior, update the relevant doc in
  the same change.
- When a release/version or material user-visible/setup/platform/security change
  affects the repository landing page, follow `README_MAINTENANCE.md` and update
  the root `../README.md` / repository profile as required.
- Avoid duplicating long canonical instructions: link to the source-of-truth doc
  instead.
- Keep `ROADMAP.md` focused on planned work and `CHANGELOG.md` focused on shipped
  changes.

## Canonical navigation document

- `GRAPHIFY_NAVIGATION.md` owns graph-first discovery, freshness, token/context
  discipline, source verification, and fallback rules for humans and AI agents.

## Canonical architecture documents

- `ARCHITECTURE.md` owns the architecture contract, target dependency direction,
  layer responsibilities, state/persistence/concurrency rules, and architecture
  review checklist.
- `SYSTEM_AUDIT.md` owns current source-level architecture evidence, current
  behavior, active risks, and evidence limitations. It should not be used as the
  future target design when it describes transitional coupling.
- `architecture/BOUNDARIES.md` owns dependency/import boundary rules.
- `architecture/FLOWS.md` owns canonical runtime/security/delivery flow diagrams.
- `architecture/EVOLUTION_PLAN.md` owns staged behavior-preserving architecture
  migration order.
- `adr/` records accepted/proposed/deprecated/superseded architecture decisions.

When architecture changes, update the smallest canonical set instead of copying
new architecture prose into many files, then refresh Graphify when available.

## Canonical maintenance documents

- `FEATURE_LIFECYCLE.md` owns the process for adding, modifying, fixing, and
  removing features, including config/migration/removal checklists.
- `BUG_TRIAGE_AND_FIXING.md` owns defect investigation, reproduction, root-cause
  repair, issue severity, and bug-fix completion.
- `EXTENDING.md` is the focused feature-module implementation template, not the
  full lifecycle/removal guide.
- `TESTING.md` owns automated and target-device verification requirements.
- `AI_AGENT_WORKFLOW.md` owns agent/skill selection and reusable AI task recipes.
- `README_MAINTENANCE.md` owns root README, GitHub About/profile metadata,
  package/version references, repository visual, and presentation synchronization
  rules for releases and material product changes.
- `FILE_REFERENCE.md` owns the curated file/module responsibility map; Graphify
  remains the first choice for live connection/dependency discovery.

The root `../README.md` is the repository/product landing page. `docs/README.md`
is the detailed task-oriented documentation index. Keep their roles distinct.

When adding a new maintenance or architecture guide, update `docs/README.md` so a
maintainer can reach it by task/goal rather than already knowing its filename. If
the guide materially changes the repository's public/project story, also review
the root README through `README_MAINTENANCE.md`.
