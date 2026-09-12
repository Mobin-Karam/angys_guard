# Codex project workspace

This directory contains project-local Codex configuration for AngysGuard / Laptop Guard.

## Navigation rule

Repository discovery is **Graphify-first**. Read `docs/GRAPHIFY_NAVIGATION.md`. SessionStart reports graph freshness; use `graphify query`, `graphify explain`, or `graphify path` before broad source reads. Never load all of `graphify-out/graph.json` into normal conversation context.

If the graph is stale and Graphify is available, refresh with `graphify update .`. Current source/tests remain authoritative.

## Layout

- `config.toml` — project instruction discovery and custom subagent registry.
- `agents/` — project-scoped custom roles.
- `hooks.json` / `hooks/` — trusted lifecycle guardrails/reminders.

## Trust

Project-local `.codex/` configuration and hooks should run only after trusting the repository/branch. Review hook code before trusting a fork or unfamiliar branch.

## Agent roles

- `navigator` — Graphify-first ownership/dependency/test/doc mapping.
- `architect` — graph-backed architecture/change planning.
- `implementer` — bounded implementation/tests from confirmed scope.
- `reviewer` — correctness/regression/blast-radius review.
- `security_reviewer` — trust-boundary/security/privacy review.
- `tester` — Graphify-guided test discovery/verification/failure triage.
- `release_manager` — release readiness, platform/support/control-mode accuracy, CI/security/checklists.
- `repository_curator` — README/About/profile/version/docs navigation/visual maintenance.
- `product_planner` — AngysGuard current-vs-future OS/app/control-mode planning, issues/milestones, and roadmap consistency.

No project agent pins a model; roles inherit the parent session's model/reasoning/permission mode.

## Product/platform workflow

For a new OS, app, provider/control mode, managed-service plan, or roadmap change:

```text
navigator (current implementation map)
        -> product_planner
        -> architect/security_reviewer when design-sensitive
        -> repository_curator for public presentation
        -> release_manager when a release/support claim changes
```

Canonical product sources:

- `docs/ANGYSGUARD_PRODUCT_VISION.md`
- `docs/PLATFORM_SUPPORT.md`
- `docs/CONTROL_MODES.md`
- `docs/ROADMAP.md`
- `docs/PROJECT_MANAGEMENT.md`

Keep current/shipped, best-effort, planned, research and user-requested states distinct. Managed mode remains optional. Never design or document sending the protected device's OS password through Bale/Telegram/mobile/backend; use device-scoped authorization plus local/native privilege boundaries.

## Hooks

- SessionStart: project/security + Graphify freshness.
- PreToolUse: blocks destructive Git/repository deletion and protected secret-file reads/edits.
- PostToolUse: reminds about tests/security/Graphify refresh and repository-presentation impact after relevant edits.

Hooks do not modify product code, commit/push changes, call external services, or read secrets.

## Primary instructions

`AGENTS.md` remains authoritative. `.codex/` augments it. For substantial discovery use `navigator`; for product/platform planning use `product_planner`; for public presentation use `repository_curator`.
