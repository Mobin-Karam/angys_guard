# Documentation instructions

These rules apply under `docs/` in addition to the root `AGENTS.md`.

## Navigate documentation with Graphify first

For questions such as "where is this documented?", "which docs own this concept?", or "what docs/source/tests connect to this behavior?", use Graphify first following `GRAPHIFY_NAVIGATION.md`.

Do not load raw `graphify-out/graph.json` into context. If the graph is stale and can be refreshed, refresh it first. Current docs/source remain authoritative when generated graph output disagrees.

## Documentation rules

- Distinguish **current/shipped**, **best-effort**, **planned**, **research**, and **user-requested** behavior explicitly.
- Never present Windows, Android, managed AngysGuard service, official bots, or another future OS as currently supported merely because an issue/milestone exists.
- Keep commands copy-pasteable and prefer safe, non-destructive examples.
- Never include real credentials, chat IDs, OS passwords, private IPs, captured media, or secret-store contents in examples.
- Never document sending the protected device's OS password through Bale, Telegram, a mobile app, or the managed backend as an acceptable design. Normal environment variables are not a password vault.
- Preserve self-hosted/local operation as a first-class product path; managed service remains optional.
- Keep security/privacy limitations explicit, especially for camera, microphone, screen/input monitoring, remote unlock/control, network providers, pairing, and managed-service behavior.
- When code changes user-visible setup, CLI commands, dependencies, architecture, target-device requirements, provider behavior, platform capability, or release behavior, update the relevant canonical doc in the same change.
- When a release/version or material product/platform/control-mode/security change affects the repository landing page, follow `README_MAINTENANCE.md` and update root `../README.md` / repository profile as required.
- Avoid duplicating long canonical instructions: link to the source-of-truth doc instead.
- Keep `ROADMAP.md` focused on planned work and `CHANGELOG.md` focused on shipped changes.

## Canonical product/platform documents

- `ANGYSGUARD_PRODUCT_VISION.md` owns long-term product identity, principles, target experiences, and what AngysGuard should not become.
- `PLATFORM_SUPPORT.md` owns current/best-effort/planned/research/not-targeted OS and device support states plus the user platform-request process.
- `CONTROL_MODES.md` owns local, Bale, Telegram, self-hosted bot, and optional managed-service control models plus credential/pairing rules.
- `ROADMAP.md` owns milestone sequencing and future issue grouping.
- `PROJECT_MANAGEMENT.md` owns Project fields/views/workflow and issue-to-track mapping.
- `README_MAINTENANCE.md` owns synchronization between public presentation and these canonical product/support sources.

For product/platform/control-mode roadmap changes, use `product_planner` / `$product-roadmap-maintenance`. Do not update one of these documents in isolation when the same decision materially changes the others.

## Canonical navigation document

- `GRAPHIFY_NAVIGATION.md` owns graph-first discovery, freshness, token/context discipline, source verification, and fallback rules for humans and AI agents.

## Canonical architecture documents

- `ARCHITECTURE.md` owns the architecture contract, target dependency direction, layer responsibilities, state/persistence/concurrency rules, and architecture review checklist.
- `SYSTEM_AUDIT.md` owns current source-level architecture evidence, behavior, active risks, and evidence limitations. It is not the future target design when describing transitional coupling.
- `architecture/BOUNDARIES.md` owns dependency/import direction.
- `architecture/FLOWS.md` owns canonical runtime/security/delivery flows.
- `architecture/EVOLUTION_PLAN.md` owns staged behavior-preserving architecture migration order.
- `adr/` records accepted/proposed/deprecated/superseded architecture decisions.
- ADR 0007 owns the proposed passwordless device-pairing/local-privilege separation decision.
- ADR 0008 owns the proposed cross-platform capability-adapter decision.

When architecture changes, update the smallest canonical set and refresh Graphify when available.

## Canonical maintenance documents

- `FEATURE_LIFECYCLE.md` owns add/change/fix/remove feature work.
- `BUG_TRIAGE_AND_FIXING.md` owns defect investigation and repair.
- `EXTENDING.md` is the focused feature-module implementation template.
- `TESTING.md` owns automated and target-device verification.
- `AI_AGENT_WORKFLOW.md` owns agent/skill selection and reusable AI task recipes.
- `README_MAINTENANCE.md` owns root README/About/profile/package/version/platform/control presentation synchronization.
- `FILE_REFERENCE.md` owns the curated file/module responsibility map; Graphify remains first choice for live dependency discovery.

The root `../README.md` is the repository/product landing page. `docs/README.md` is the task-oriented documentation index. Keep their roles distinct.

When adding a new product, platform, maintenance or architecture guide, update `docs/README.md`. If it changes the public/project story, also review the root README and product-roadmap sources.
