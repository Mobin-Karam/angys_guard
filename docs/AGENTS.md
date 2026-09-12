# Documentation instructions

These rules apply under `docs/` in addition to the root `AGENTS.md`.

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
- Avoid duplicating long canonical instructions: link to the source-of-truth doc
  instead.
- Keep `ROADMAP.md` focused on planned work and `CHANGELOG.md` focused on shipped
  changes.

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
new architecture prose into many files.

## Canonical maintenance documents

- `FEATURE_LIFECYCLE.md` owns the process for adding, modifying, fixing, and
  removing features, including config/migration/removal checklists.
- `BUG_TRIAGE_AND_FIXING.md` owns defect investigation, reproduction, root-cause
  repair, issue severity, and bug-fix completion.
- `EXTENDING.md` is the focused feature-module implementation template, not the
  full lifecycle/removal guide.
- `TESTING.md` owns automated and target-device verification requirements.
- `AI_AGENT_WORKFLOW.md` owns agent/skill selection and reusable AI task recipes.
- `FILE_REFERENCE.md` owns file/module responsibility mapping.

When adding a new maintenance or architecture guide, update `README.md` so a
maintainer can reach it by task/goal rather than already knowing its filename.
