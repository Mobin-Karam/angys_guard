# Codex project workspace

This directory contains project-local Codex configuration for Laptop Guard.

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

- `architect`: read-only planning and architecture mapping.
- `implementer`: bounded code changes and tests.
- `reviewer`: read-only correctness/regression review.
- `security_reviewer`: read-only trust-boundary/security review.
- `tester`: verification and failure triage.
- `release_manager`: release-readiness checks.

No project agent pins a model. Roles inherit the model/reasoning and permission
mode selected by the parent Codex session unless a future task explicitly needs a
per-role override.

## Hooks

The hooks are intentionally narrow:

- Session start adds a short reminder of the repository guardrails.
- Pre-tool policy blocks destructive Git/repository deletion and direct secret-file
  reads/edits.
- Post-edit review adds verification/security-review context after runtime edits.

Hooks do not modify product code, commit/push changes, call external services, or
read secrets.

## Primary instructions

`AGENTS.md` remains the authoritative project policy. `.codex/` augments it; it
does not replace it.
