# Reusable engineering prompt library

These prompts are intentionally **evergreen and repository-aware**. They avoid pinned model names, versions, framework assumptions, and machine-specific commands. Project-specific policy stays in `AGENTS.md` and canonical docs.

## How to use

Invoke a prompt file from `.github/prompts/` in a supported IDE, or copy/paste it into Codex, Copilot, Claude, Gemini, another coding agent, or a normal AI chat.

## Stable baseline used by every prompt

Unless a prompt says otherwise, the agent should:

1. Read repository-wide/nearest scoped instructions and `docs/GRAPHIFY_NAVIGATION.md`.
2. Check Graphify freshness and use `query` / `explain` / `path` before broad search/reads.
3. Verify important conclusions against current source/tests/docs.
4. Never load all of `graphify-out/graph.json` into context.
5. Use the narrowest fallback if Graphify cannot answer the question.
6. Preserve unrelated changes and avoid destructive Git.
7. Never expose secrets, credentials, OS passwords, private keys, private evidence, or personal data.
8. Prefer the smallest coherent change and reuse existing abstractions.
9. Add/update focused tests for behavior changes.
10. Run targeted verification before broader checks.
11. For release/version/user-visible/setup/platform/security/brand changes, account for repository presentation and current-vs-future product/support claims.
12. Refresh Graphify after material relationship changes when available.
13. Distinguish facts, inferred relationships, current support, planned/research targets, risks and manual validation.
14. Do not commit/push/merge/publish/deploy unless explicitly requested.

## Prompt index

### Navigate, understand and plan
- `graphify-navigation.prompt.md`
- `understand-repository.prompt.md`
- `architecture-map.prompt.md`
- `plan-change.prompt.md`
- `risk-assessment.prompt.md`
- `backward-compatibility.prompt.md`

### Product/platform planning
- `update-product-roadmap.prompt.md` — keep AngysGuard product vision, OS/app targets, Bale/Telegram/self-hosted/managed modes, issues/milestones and current-vs-future claims synchronized
- `cross-platform-review.prompt.md`

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

### Documentation, brand, presentation and delivery
- `design-or-refresh-brand.prompt.md` — logo/icon/wordmark/color/hero/social-preview workflow using `docs/BRAND_GUIDE.md` and `$brand-assets`
- `refresh-repository-presentation.prompt.md` — README/About/version/docs/visual synchronization
- `update-docs.prompt.md`
- `explain-code.prompt.md`
- `onboard-to-repo.prompt.md`
- `draft-issue.prompt.md`
- `pr-description.prompt.md`
- `commit-message.prompt.md`
- `release-readiness.prompt.md`
- `release-notes.prompt.md`

### General-purpose router
- `engineering-task.prompt.md`

## Maintenance rule

Keep prompt text generic. Project-specific policy and changing product facts live in `AGENTS.md`, `docs/GRAPHIFY_NAVIGATION.md`, `docs/README_MAINTENANCE.md`, `docs/BRAND_GUIDE.md`, `docs/ANGYSGUARD_PRODUCT_VISION.md`, `docs/PLATFORM_SUPPORT.md`, and `docs/CONTROL_MODES.md`.
