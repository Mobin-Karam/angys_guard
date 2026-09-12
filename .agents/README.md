# Project AI skills

Repository-scoped reusable agent workflows live under `.agents/skills/<name>/SKILL.md`.
Codex discovers these skills from their frontmatter metadata and loads the full
instructions only when selected.

## Navigation baseline

Every skill inherits the Graphify-first rule from `AGENTS.md` and
`docs/GRAPHIFY_NAVIGATION.md`. When a workflow needs repository discovery, locate
owners/callers/dependencies/tests/docs with Graphify before broad source reads.
Use current source as final authority and never load all of `graphify-out/graph.json`
into context.

Current skills:

| Skill | Use it for |
| --- | --- |
| `graphify-navigation` | Locating owners, symbols, callers, dependencies, tests/docs, and change impact with minimal context |
| `issue-to-pr` | Turning a GitHub issue/roadmap item into a bounded implementation and PR workflow |
| `safe-implementation` | Runtime features, fixes, refactors, setup/CLI/provider/hardware changes |
| `security-review` | Authorization, secrets, remote control, capture/privacy, process/network review |
| `test-and-verify` | Focused tests, full validation, failure triage, manual-check accounting |
| `release-readiness` | Version/changelog/CI/security/release checklist validation |

Prefer `$graphify-navigation` as the first skill when ownership/scope is unclear.
Other skills should consume its compact path/node handoff instead of repeating
repository-wide discovery.

Keep skill descriptions narrow enough that automatic selection is predictable.
Do not put secrets, machine-specific credentials, or personal paths in skills.
Project policy belongs in `AGENTS.md`; skills describe repeatable workflows rather
than duplicate all repository instructions.
