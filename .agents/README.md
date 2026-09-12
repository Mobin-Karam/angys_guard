# Project AI skills

Repository-scoped reusable agent workflows live under `.agents/skills/<name>/SKILL.md`.
Codex discovers these skills from their frontmatter metadata and loads the full
instructions only when selected.

Current skills:

| Skill | Use it for |
| --- | --- |
| `issue-to-pr` | Turning a GitHub issue/roadmap item into a bounded implementation and PR workflow |
| `safe-implementation` | Runtime features, fixes, refactors, setup/CLI/provider/hardware changes |
| `security-review` | Authorization, secrets, remote control, capture/privacy, process/network review |
| `test-and-verify` | Focused tests, full validation, failure triage, manual-check accounting |
| `release-readiness` | Version/changelog/CI/security/release checklist validation |

Keep skill descriptions narrow enough that automatic selection is predictable.
Do not put secrets, machine-specific credentials, or personal paths in skills.
Project policy belongs in `AGENTS.md`; skills should describe repeatable workflows
rather than duplicate all repository instructions.
