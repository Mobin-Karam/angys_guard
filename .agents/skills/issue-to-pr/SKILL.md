---
name: issue-to-pr
description: Execute a Laptop Guard GitHub issue as a bounded branch-to-PR workflow. Use when the user asks to work on an issue, implement the next roadmap item, or turn an issue into a reviewed pull request.
---

# Issue to PR

1. Read the target issue completely and extract acceptance criteria, dependencies,
   milestone, labels, and priority.
2. Run `git status --short`. Preserve unrelated changes; do not reset/clean them.
3. Read `AGENTS.md`, applicable nested `AGENTS.md`, and
   `docs/GRAPHIFY_NAVIGATION.md`.
4. Before broad source discovery, use Graphify to map the issue to owning symbols,
   callers/dependencies, tests, config/state/storage, and relevant docs. Check
   freshness and refresh when available. If Graphify cannot be used, keep fallback
   search narrow and state why.
5. Confirm the graph-identified scope in current authoritative source/tests.
6. Confirm/create a focused branch when Git work is in scope; do not work directly
   on `main` unless explicitly requested.
7. For cross-module/security-sensitive work, use `architect`; use `navigator` first
   when the issue's ownership/impact is still unclear. Use `security_reviewer`
   before completion for sensitive trust-boundary changes.
8. Implement the smallest coherent patch. Keep acceptance criteria visible and
   avoid unrelated cleanup.
9. Add focused regression/failure tests; use Graphify to locate connected coverage,
   then run the `test-and-verify` workflow.
10. Review `git diff --check`, changed files, user-visible docs/config, and the
    graph-identified impact surface.
11. Have `reviewer` inspect non-trivial final diffs for correctness/regressions.
12. Refresh Graphify after material code/docs relationship changes when available.
13. If delivery is explicitly in scope, make focused commits, push the branch, and
    open a PR linking the issue with tests/manual checks/graph freshness.
14. Do not merge unless explicitly requested and required checks are green.

Never load raw `graphify-out/graph.json` into context or copy credentials, `.env`,
`secrets.json`, stop PIN material, or captured evidence into issue/PR text.
