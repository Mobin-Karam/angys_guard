# Reusable engineering prompt library

These prompts are intentionally **evergreen and repository-aware**. They avoid
pinned model names, versions, framework assumptions, and machine-specific commands.
Project-specific policy stays in `AGENTS.md` and canonical docs.

## How to use

In GitHub Copilot-supported IDEs, invoke a prompt file from `.github/prompts/` by
name. You can also copy/paste a prompt into Codex, Copilot, Claude, Gemini, another
coding agent, or a normal AI chat.

When a prompt contains placeholders such as `<task>`, `<feature>`, `<bug>`,
`<issue>`, `<file>`, or `<goal>`, replace them or add context in the same message.

## Stable baseline used by every prompt

Unless a prompt says otherwise, the agent should:

1. Read repository-wide/nearest scoped instructions and
   `docs/GRAPHIFY_NAVIGATION.md` before repository discovery.
2. Check Graphify freshness and use `graphify query`, `graphify explain`, or
   `graphify path` before broad grep/search or large file reads.
3. Use the graph to select the smallest relevant source/tests/docs, then verify
   important conclusions against those current authoritative files.
4. Never load the complete `graphify-out/graph.json` into conversation context.
5. If Graphify is unavailable/stale-and-unrefreshable/insufficient, use a narrow
   direct fallback and state why.
6. Preserve unrelated working-tree changes and avoid destructive Git operations.
7. Never expose secrets, credentials, private keys, personal data, or captured evidence.
8. Prefer the smallest coherent change that fixes the root cause/acceptance criteria.
9. Reuse existing abstractions before introducing parallel mechanisms.
10. Add/update focused tests for behavior changes and meaningful failure/denial paths.
11. Run targeted verification first, then broader required checks.
12. Refresh Graphify after material code/docs relationship changes when available.
13. Distinguish facts, inferred graph relationships, assumptions, risks, and manual
    validation still required.
14. Do not commit/push/merge/publish/deploy/destructively act unless explicitly requested.

## Prompt index

### Navigate, understand and plan
- `graphify-navigation.prompt.md` — first choice for finding/understanding repository relationships
- `understand-repository.prompt.md`
- `architecture-map.prompt.md`
- `plan-change.prompt.md`
- `risk-assessment.prompt.md`
- `backward-compatibility.prompt.md`

### Feature lifecycle
- `add-feature.prompt.md`
- `modify-feature.prompt.md`
- `remove-feature.prompt.md`
- `minimal-implementation.prompt.md`
- `api-change.prompt.md`
- `config-migration.prompt.md`

### Bugs and incidents
- `debug-unknown-bug.prompt.md`
- `fix-reproducible-bug.prompt.md`
- `root-cause-analysis.prompt.md`
- `triage-issue.prompt.md`
- `incident-analysis.prompt.md`
- `ci-failure.prompt.md`
- `fix-failing-tests.prompt.md`

### Review and quality
- `review-code.prompt.md`
- `review-pr.prompt.md`
- `security-review.prompt.md`
- `privacy-review.prompt.md`
- `reliability-review.prompt.md`
- `performance-investigation.prompt.md`
- `refactor-safely.prompt.md`
- `simplify-code.prompt.md`
- `cleanup-dead-code.prompt.md`
- `technical-debt-plan.prompt.md`

### Testing and dependencies
- `write-tests.prompt.md`
- `verify-change.prompt.md`
- `dependency-upgrade.prompt.md`
- `cross-platform-review.prompt.md`

### Documentation and delivery
- `update-docs.prompt.md`
- `explain-code.prompt.md`
- `onboard-to-repo.prompt.md`
- `draft-issue.prompt.md`
- `pr-description.prompt.md`
- `commit-message.prompt.md`
- `release-readiness.prompt.md`
- `release-notes.prompt.md`

### General-purpose router
- `engineering-task.prompt.md` — use when no specialized prompt clearly fits.

## Maintenance rule

Keep prompt text generic. The Graphify-first rule and project-specific policy live
in `AGENTS.md` and `docs/GRAPHIFY_NAVIGATION.md`; prompts should reference those
rather than copying changing implementation details. Update a prompt only when the
workflow itself changes.
