# Codex project workspace

This directory contains project-local Codex configuration for Laptop Guard.

## Navigation rule

Repository discovery is **Graphify-first**. Read `docs/GRAPHIFY_NAVIGATION.md`.
The SessionStart hook reports graph freshness; use `graphify query`, `graphify
explain`, or `graphify path` before broad source reads. The generated
`graphify-out/graph.json` is machine data and should not be loaded wholesale into
conversation context.

If the graph is stale and Graphify is available, refresh with `graphify update .`.
Current source/tests remain authoritative after Graphify narrows the scope.

## Layout

- `config.toml` — project instruction discovery and custom subagent registry.
- `agents/` — project-scoped custom subagent roles.
- `hooks.json` — trusted lifecycle hooks.
- `hooks/` — small dependency-free Python hook handlers.

## Trust

Project-local `.codex/` configuration and hooks are intended to run only after
you trust this repository in Codex. Review hook code before trusting a fork or
unfamiliar branch.

## Agent roles

- `navigator`: read-only Graphify-first ownership/dependency/test/doc mapping.
- `architect`: read-only graph-backed planning and architecture mapping.
- `implementer`: bounded code changes/tests from a confirmed graph/source scope.
- `reviewer`: read-only correctness/regression and blast-radius review.
- `security_reviewer`: read-only trust-boundary/security impact review.
- `tester`: Graphify-guided test discovery, verification, and failure triage.
- `release_manager`: release readiness, graph freshness, CI/support/checklists,
  including repository-presentation readiness.
- `repository_curator`: root README, GitHub About/profile metadata, version/release
  references, docs navigation, and overview visual maintenance.

No project agent pins a model. Roles inherit the parent session's model/reasoning
and permission mode unless a future task explicitly needs a per-role override.

For releases, version bumps, or material user-visible changes, `release_manager`
should ensure `repository_curator` / `$repository-presentation` has accounted for
`README.md`, `.github/repository-profile.json`, package metadata, and related docs.
The canonical contract is `docs/README_MAINTENANCE.md`.

## Hooks

The hooks are intentionally narrow:

- Session start adds project/security policy plus Graphify freshness status.
- Pre-tool policy blocks destructive Git/repository deletion and direct secret-file
  reads/edits.
- Post-edit review adds verification/security-review context after runtime edits
  and reminds agents to consider repository-presentation impact for material
  user-visible changes.

Hooks do not modify product code, commit/push changes, call external services, or
read secrets. Graphify itself remains developer/agent tooling, not a product
runtime dependency.

## Primary instructions

`AGENTS.md` remains the authoritative project policy. `.codex/` augments it; it
does not replace it. For substantial discovery, delegate to `navigator` and hand
its compact paths/nodes/relationships to the next specialist rather than making
each agent rediscover the repository independently.
