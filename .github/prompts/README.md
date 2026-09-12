# Reusable engineering prompt library

These prompts are intentionally **evergreen and repository-aware**. They avoid pinned model names, versions, framework assumptions, and machine-specific commands. Each prompt tells the agent to discover and obey the current repository instructions first, so the library should need little maintenance as the project evolves.

## How to use

In GitHub Copilot-supported IDEs, invoke a prompt file from `.github/prompts/` by name. You can also open any file here and copy/paste its text into Codex, Copilot, Claude, Gemini, another coding agent, or a normal AI chat.

When a prompt contains placeholders such as `<task>`, `<feature>`, `<bug>`, `<issue>`, `<file>`, or `<goal>`, replace them or add the missing context in the same chat message.

## Stable baseline used by every prompt

Unless a prompt says otherwise, the agent should:

1. Read repository-wide and nearest scoped instructions (`AGENTS.md`, contributor/security guidance, and relevant docs) before acting.
2. Inspect current source/tests/config rather than assuming architecture or APIs.
3. Preserve unrelated working-tree changes and avoid destructive Git operations.
4. Never expose secrets, credentials, private keys, personal data, or private captured evidence.
5. Prefer the smallest coherent change that fixes the root cause or meets the acceptance criteria.
6. Reuse existing abstractions before introducing new parallel mechanisms.
7. Add/update focused tests for behavior changes and important failure/denial paths.
8. Run targeted verification first, then the repository's broader required checks.
9. Distinguish facts, assumptions, risks, and manual validation still required.
10. Do not commit, push, merge, publish, deploy, or perform destructive actions unless explicitly requested.

## Prompt index

### Understand and plan
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
- `engineering-task.prompt.md` — use when you are not sure which specialized prompt fits.

## Maintenance rule

Keep these prompts generic. Project-specific policy belongs in repository instructions/docs, not duplicated here. Only update a prompt when the **workflow itself** changes, not when implementation details, versions, filenames, or frameworks change.