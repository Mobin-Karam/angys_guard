# AngysGuard / Laptop Guard AI / Codex instructions

These instructions are authoritative for AI-assisted work in this repository.
More specific `AGENTS.md` files under subdirectories add or override rules for that area.

## Mission

AngysGuard (current compatibility package/repository: Laptop Guard) is an owner-controlled device security and monitoring product. Optimize for: **security > privacy > correctness > recoverability > simple UX > feature breadth**.

Do not trade away security/privacy boundaries for convenience.

The current shipped product is Linux-first. Windows, Android, managed-service and other future platform work must remain clearly labeled as planned/research until implementation and target-device validation exist.

## Graphify-first navigation — mandatory default

For repository discovery, use Graphify **before** broad file reads, recursive grep/search, or opening large modules. The canonical procedure is `docs/GRAPHIFY_NAVIGATION.md`.

This applies whenever the task asks what exists, where behavior lives, what calls or depends on something, which tests cover it, what a change affects, or how two parts of the project connect.

Normal order:

```text
check graph freshness
  -> graphify query / explain / path
  -> identify smallest relevant nodes/files/tests/docs
  -> open only those authoritative files/ranges
  -> plan / answer / edit
```

Preferred commands:

```bash
graphify query "<repository question>"
graphify explain "<symbol or concept>"
graphify path "<source node>" "<target node>"
```

Do **not** load the complete `graphify-out/graph.json` into context. Use Graphify's query commands and use `graphify-out/GRAPH_REPORT.md` only for high-level orientation/freshness information.

Before relying on the graph, check the build commit in `GRAPH_REPORT.md` against the current repository. If stale and Graphify is available, run `graphify update .` (or the assistant's Graphify update integration) first. If Graphify is missing, stale and cannot be refreshed, or insufficient for the exact question, use the narrowest direct fallback search and state that fallback.

Graphify narrows context; it is not final authority. Confirm important behavior, security conclusions, deletions, migrations, refactors and support claims in current source/tests. When graph output and current source disagree, current source wins.

Use the repo-local `navigator` agent or `$graphify-navigation` skill when repository mapping itself is substantial. Hand off graph nodes/paths instead of copying large source blocks between agents.

## Read only what the task needs

After Graphify identifies the likely scope, use the canonical document that owns the task:

- Product vision / current-vs-future direction: `docs/ANGYSGUARD_PRODUCT_VISION.md`
- OS/platform support and user platform requests: `docs/PLATFORM_SUPPORT.md`
- Local/Bale/Telegram/self-hosted/managed control modes: `docs/CONTROL_MODES.md`
- Graph navigation/freshness/fallback: `docs/GRAPHIFY_NAVIGATION.md`
- Architecture contract/target boundaries: `docs/ARCHITECTURE.md`
- Current architecture evidence/risks: `docs/SYSTEM_AUDIT.md`
- Dependency rules and staged refactors: `docs/architecture/`
- Architecture decisions: `docs/adr/`
- Add/change/remove/fix a feature: `docs/FEATURE_LIFECYCLE.md`
- Feature module contracts/templates: `docs/EXTENDING.md`
- Find/triage/fix a bug or GitHub issue: `docs/BUG_TRIAGE_AND_FIXING.md`
- Curated ownership map: `docs/FILE_REFERENCE.md`
- Configuration/secrets: `docs/CONFIGURATION.md`, `docs/SECURITY.md`
- Testing/target-device checks: `docs/TESTING.md`
- AI roles/skills/task recipes: `docs/AI_AGENT_WORKFLOW.md`
- Repository README/About/version/visual maintenance: `docs/README_MAINTENANCE.md`
- Current/future execution roadmap: `docs/ROADMAP.md`
- Project/milestones/labels/views: `docs/PROJECT_MANAGEMENT.md`
- GitHub/release process: `CONTRIBUTING.md`, `.github/REPOSITORY_SETTINGS.md`

## Runtime architecture

Primary current path:

`run.sh -> laptop_guard.cli -> runtime_config -> guard.LaptopGuard`

`LaptopGuard` uses `runtime_api.build_runtime_api`, `GuardRuntimeState`, and an explicit `FeatureManager`.

Architecture rules:

- Treat `docs/ARCHITECTURE.md` and Accepted ADRs as the target dependency contract.
- For non-trivial cross-module refactors, use Graphify to map actual current dependencies, then read `docs/architecture/BOUNDARIES.md` and `docs/architecture/EVOLUTION_PLAN.md` before proposing edits.
- For cross-platform work, follow proposed ADR 0008 and design narrow capability adapters rather than scattering platform conditionals or shell commands through policy code.
- Evolve architecture by behavior-preserving slices; do not perform directory/class reshuffles merely to make the tree look cleaner.
- Dependencies should move inward: delivery/infrastructure may depend on application-owned ports, while application/domain decisions should not depend on concrete HTTP, database, hardware, or OS-command implementations.
- New bot commands/callbacks belong in one focused module under `laptop_guard/features/`; do not grow legacy command/callback chains.
- Code that talks to the owner depends on `RuntimeApi`, not directly on Requests/httpx.
- Runtime transport construction belongs in `build_runtime_api()`.
- Shared live state goes through `GuardRuntimeState` / `RuntimeStateStore`.
- Prefer narrow protocols/services over passing the full guard object around.
- Keep imports side-effect-light and optional native dependencies lazy.
- Keep feature registration explicit; do not add filesystem plugin auto-discovery.
- Do not add new behavior to a compatibility facade when an active path exists; use the active path and plan migration/removal instead.
- Avoid service locators/global registries that let features reach arbitrary infrastructure.

## Security and privacy hard gates

Never weaken these without an explicit user decision and a documented security review:

- Preserve owner authorization, pairing, confirmation, and stop/unlock gates.
- Never add remote shell, arbitrary command execution, `eval`, `exec`, or a generic script runner reachable from remote control surfaces.
- Never add hidden capture, stealth recording, credential collection, keylogging, password capture, or suppression of required local privacy indicators.
- **Never design a flow that sends the protected device's OS password through Bale, Telegram, a mobile app, a managed AngysGuard backend, or another network/provider surface.**
- Do not treat normal environment variables as a secure store for reusable OS passwords. If a future platform absolutely requires a reusable local secret, use its credential/keyring facility with explicit lifecycle/revocation rules.
- Remote owner/account authentication and local OS privilege are separate concerns. Prefer revocable device-scoped credentials plus narrow platform-native local privilege mechanisms, per ADR 0007.
- Never read, print, copy into issues, or log `.env`, `secrets.json`, stop PIN material, authentication tokens, private keys, or captured evidence media.
- Keep local control APIs loopback-only by default and authenticated.
- Bound recording durations, payload sizes, retries, queues, and timeouts.
- Prefer argument-list subprocess calls. Avoid `shell=True` and shell string composition for variable input.
- Use atomic writes and restrictive permissions for configuration/secrets.
- Reject ambiguous remote actions rather than guessing.
- Managed AngysGuard service remains optional; self-hosted/local operation is a first-class product path.
- Do not claim Windows, Android, macOS or another OS as supported until implementation + target-device validation justify that support state.

Graphify and fallback search must obey the same secret/privacy boundaries. Repository marketing/documentation must not imply that prohibited behavior or planned features are already supported.

If a requested change conflicts with these rules, stop that part of the change, explain the conflict, and propose the safest compatible design.

## Working procedure

1. Run/inspect `git status --short`. Preserve unrelated changes.
2. Identify the issue/acceptance criteria when the task references GitHub work.
3. Check Graphify freshness and navigate with `query` / `explain` / `path` before broad source discovery.
4. Open only the smallest relevant authoritative source/docs/tests identified by the graph and applicable scoped instructions.
5. For architecture/cross-module work, reconcile the current graph/source with `docs/ARCHITECTURE.md`, `docs/architecture/`, and relevant ADRs.
6. For product/platform/control-mode roadmap work, follow `docs/ANGYSGUARD_PRODUCT_VISION.md`, `docs/PLATFORM_SUPPORT.md`, `docs/CONTROL_MODES.md`, `docs/ROADMAP.md`, and `$product-roadmap-maintenance` / `product_planner`.
7. For feature work, follow `docs/FEATURE_LIFECYCLE.md`; for defects, follow `docs/BUG_TRIAGE_AND_FIXING.md` and reproduce before changing code when practical.
8. For non-trivial changes, state the intended change boundary before editing.
9. Implement the smallest coherent patch; avoid opportunistic rewrites.
10. Add or update focused tests for behavior and failure modes.
11. If a release, version, user-visible feature/command/platform/setup/security boundary, support state, control mode, or repository structure materially changed, follow `docs/README_MAINTENANCE.md` / `$repository-presentation` and `$product-roadmap-maintenance` where applicable in the same change or explicitly record the follow-up.
12. Run targeted checks first, then the broader verification required below.
13. Review the diff for security/privacy regressions, stale support/roadmap/presentation claims, and accidental secrets.
14. Refresh Graphify after material code/docs relationship changes when the tool is available.
15. Report what changed, what was validated, product/support/presentation impact when applicable, graph freshness status, and target-device checks still required.

Do not reset, clean, force checkout, overwrite unrelated work, or use destructive Git recovery commands. Do not commit/push/merge unless the user or task explicitly asks for that Git action.

## Available project agents

Project-scoped Codex subagents live in `.codex/agents/`:

- `navigator` — read-only Graphify-first repository mapping and impact tracing.
- `architect` — read-only architecture and change planning.
- `implementer` — focused implementation work.
- `reviewer` — correctness/regression review.
- `security_reviewer` — authorization, privacy, secrets, and abuse-boundary review.
- `tester` — test strategy, failures, and verification.
- `release_manager` — release readiness, platform/support matrix, and changelog/checklist work.
- `repository_curator` — README, GitHub About/profile, version/release references, docs navigation, and repository visual maintenance.
- `product_planner` — current-vs-future AngysGuard product/platform/control-mode planning, issues/milestones, and roadmap consistency.

For non-trivial work, prefer `navigator` first when scope/ownership is not already known, then hand its compact map to the specialist agent. Use `product_planner` for platform/app/control-mode/milestone changes and `repository_curator` for release/version/presentation refreshes.

## Available project skills

Reusable workflows live in `.agents/skills/`:

- `graphify-navigation` — graph-first repository discovery and dependency tracing.
- `issue-to-pr` — execute a GitHub issue as a bounded implementation workflow.
- `safe-implementation` — implement changes while preserving security boundaries.
- `security-review` — review sensitive code paths and configuration.
- `test-and-verify` — choose and run focused/full verification.
- `release-readiness` — prepare a release without skipping safety checks.
- `repository-presentation` — synchronize README, About/profile metadata, version references, docs navigation, and repository visuals with shipped behavior.
- `product-roadmap-maintenance` — synchronize product vision, OS/app support, control modes, roadmap issues/milestones, and current/planned/research claims.

## Validation

For a normal Python/runtime change, use the relevant subset first and finish with all applicable checks:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q laptop_guard tests
bash -n install.sh run.sh doctor.sh repair-opencv.sh
.venv/bin/python -m pip check
git diff --check
```

For repository presentation/product-roadmap changes, also run the relevant policy/documentation tests, especially:

```bash
.venv/bin/python -m pytest -q tests/test_repository_presentation.py
.venv/bin/python -m pytest -q tests/test_documentation_links.py tests/test_graphify_navigation_policy.py
```

Hardware/session/provider/platform behavior also requires target-device checks in `docs/TESTING.md`; unit tests do not prove camera, microphone, lock, Wayland/X11, systemd, live provider, Windows, Android or other platform behavior.

## Command-output hygiene

- Prefer quiet/concise commands (`pytest -q`, `git status --short`).
- Prefer Graphify relationship results over broad grep dumps.
- Preserve exit codes and actionable errors.
- Do not dump secrets, full environment files, captured media, raw `graph.json`, or large logs into context.
- For noisy failures, inspect only relevant excerpts or delegate analysis using a compact graph/path handoff.

## Completion standard

A task is not complete until behavior, failure handling, security/privacy impact, tests, support/platform/control-mode claims, relevant presentation impact, and graph freshness are accounted for. Final reports should identify any manual target-device validation or GitHub repository-admin setting that remains.
