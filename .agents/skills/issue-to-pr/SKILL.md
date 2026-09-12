---
name: issue-to-pr
description: Execute a Laptop Guard GitHub issue as a bounded branch-to-PR workflow. Use when the user asks to work on an issue, implement the next roadmap item, or turn an issue into a reviewed pull request.
---

# Issue to PR

1. Read the target issue completely and extract acceptance criteria, dependencies,
   and milestone/priority.
2. Run `git status --short`. Preserve unrelated changes; do not reset/clean them.
3. Confirm the current branch. Create/use a focused branch when Git work is in
   scope; do not work directly on `main` unless explicitly requested.
4. Read `AGENTS.md`, applicable nested `AGENTS.md`, and only the docs/source needed
   for the issue.
5. For cross-module or security-sensitive work, ask the `architect` agent for a
   bounded implementation plan. For sensitive trust-boundary changes also use
   `security_reviewer` before completion.
6. Implement the smallest coherent patch. Keep acceptance criteria visible while
   working; avoid unrelated cleanup.
7. Add focused regression/failure tests and run the `test-and-verify` workflow.
8. Review `git diff --check`, changed files, and any user-visible docs/config.
9. Have `reviewer` inspect the final diff for correctness/regressions on non-trivial
   changes.
10. If the task explicitly includes GitHub delivery, make focused commits, push the
    branch, and open a PR that links the issue and states tests/manual checks.
11. Do not merge unless explicitly requested and required checks are green.

Never copy credentials, `.env` contents, `secrets.json`, stop PIN material, or
captured evidence into issue/PR text.
