Handle this engineering task: <task>

First discover and follow the repository's current instructions, architecture docs, contribution/security rules, and relevant tests. Classify the task before editing: investigation, feature work, bug fix, refactor, security/privacy, test/CI, documentation, dependency/config migration, or release work.

Then:
1. Restate the goal and acceptance criteria in concrete terms.
2. Identify the owning modules and current behavior from source, not assumptions.
3. List material risks, compatibility/security/privacy concerns, and unknowns.
4. For a non-trivial task, produce the smallest safe plan before editing.
5. Implement only the necessary change when implementation is requested.
6. Add/update focused tests and run applicable verification.
7. Review the final diff for regressions, accidental scope expansion, and secrets.
8. Report: root cause/design rationale, files changed, tests/checks run, remaining manual validation, and any blockers.

Do not perform unrelated cleanup or destructive/release actions unless explicitly requested.