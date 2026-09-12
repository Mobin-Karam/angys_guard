# Project AI skills

Repository-scoped reusable agent workflows live under `.agents/skills/<name>/SKILL.md`. Codex discovers these skills from frontmatter metadata and loads the full instructions only when selected.

## Navigation baseline

Every skill inherits the Graphify-first rule from `AGENTS.md` and `docs/GRAPHIFY_NAVIGATION.md`. Use Graphify to locate owners/callers/dependencies/tests/docs before broad source reads. Current source remains final authority; never load all of `graphify-out/graph.json` into context.

Current skills:

| Skill | Use it for |
| --- | --- |
| `graphify-navigation` | Owners, symbols, callers, dependencies, tests/docs, change impact |
| `issue-to-pr` | GitHub issue -> bounded implementation/PR workflow |
| `safe-implementation` | Runtime/setup/provider/hardware changes with security boundaries |
| `security-review` | Authorization, secrets, remote control, capture/privacy, process/network review |
| `test-and-verify` | Focused/full verification and manual-check accounting |
| `release-readiness` | Version/changelog/CI/security/platform/release readiness |
| `repository-presentation` | README, About/profile, package/version references, docs navigation, visuals |
| `product-roadmap-maintenance` | AngysGuard product vision, OS/app support, Bale/Telegram/self-hosted/managed modes, roadmap issues/milestones, current-vs-future claims |

Prefer `$graphify-navigation` first when ownership/scope is unclear.

Use `$product-roadmap-maintenance` when a release/product decision adds or changes an OS target, app target, bot/control mode, managed-service plan, platform request, milestone, or support state. Use `$repository-presentation` when that change affects public README/About/support copy.

Current product-platform sources of truth:

- `docs/ANGYSGUARD_PRODUCT_VISION.md`;
- `docs/PLATFORM_SUPPORT.md`;
- `docs/CONTROL_MODES.md`;
- `docs/ROADMAP.md`;
- `docs/PROJECT_MANAGEMENT.md`.

Keep skill descriptions narrow enough that automatic selection is predictable. Do not put secrets, credentials, OS passwords, machine-specific paths, or private evidence in skills.
