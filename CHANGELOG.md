# Changelog

All notable changes to Laptop Guard should be recorded here from this point forward.

The project uses semantic-style versioning where practical:

- **Patch**: fixes and compatible hardening.
- **Minor**: compatible features and UX improvements.
- **Major**: breaking behavior, configuration, or compatibility changes.

## Unreleased

### Repository presentation

- Added a full root `README.md` landing page with product overview, capabilities, security boundaries, architecture/flow diagrams, quick start, commands, repository map, testing, docs, roadmap, contributing, and license guidance.
- Added `docs/assets/laptop-guard-overview.svg` as the repository overview visual used by the landing page.
- Added canonical `.github/repository-profile.json` metadata for GitHub About description/topics/social-preview source.
- Updated package metadata so the root README is the package landing document and package description/URLs align with the repository presentation.
- Added `.gitattributes` Linguist rules so generated Graphify HTML/JSON do not dominate GitHub language statistics.
- Added `docs/README_MAINTENANCE.md`, the `repository_curator` Codex role, `$repository-presentation` skill, reusable presentation prompt, PR/maintainer/release workflow integration, and regression tests to keep README/About/version/docs/visuals synchronized with future shipped changes.

### Developer and AI navigation

- Made Graphify the default repository-discovery/navigation layer for humans and AI agents before broad source reads/searches.
- Added canonical Graphify freshness, query/path/explain, source-verification, token/context, and fallback guidance.
- Added a read-only Codex `navigator` role and reusable `graphify-navigation` skill/prompt.
- Updated Codex, Copilot, Claude, Gemini, scoped AGENTS, feature/bug workflows, tests, review/security/release roles, and contribution docs to use Graphify-first discovery.
- Codex SessionStart now reports Graphify freshness and post-edit guidance reminds maintainers to refresh the graph after material relationship changes.
- Added regression tests that protect the cross-tool Graphify navigation policy.

### Planned

See `docs/ROADMAP.md`, `docs/PROJECT_MANAGEMENT.md`, the GitHub project-tracking issue, and `docs/architecture/EVOLUTION_PLAN.md` for the v11.2, v11.3, v12.0, and architecture-evolution work.

## 11.1.0 — 2026-09-12

First formal GitHub release checkpoint for the existing 11.1.0 product baseline.

### Repository and project management

- Added GitHub Actions CI for supported Python versions.
- Added repository safety checks to prevent common local secret files and private keys from being committed.
- Added Dependabot configuration for Python and GitHub Actions dependencies.
- Added issue forms, pull request checklist, CODEOWNERS, security policy, and contribution workflow.
- Removed the tracked `.env` file from the current branch and added ignore rules for local secrets/runtime artifacts.
- Added declarative repository-management configuration for labels, milestones, issue metadata, release notes, and the `v11.1.0` GitHub release/tag bootstrap.
- Defined the GitHub Project v2 fields, views, workflow states, and initial issue mapping.

### AI-assisted engineering

- Added authoritative `AGENTS.md` instructions with scoped runtime/test/docs guidance.
- Added project-local Codex roles, reusable skills, safety hooks, and cross-tool AI compatibility instructions.
- Added an evergreen `.github/prompts/` engineering prompt library.
- Added feature-lifecycle, bug-triage, testing, and AI-agent maintenance playbooks.

### Architecture baseline

- Added the canonical modular-monolith / ports-and-adapters architecture guide.
- Added dependency-boundary rules, security/runtime flow diagrams, staged architecture evolution plan, and ADR framework.
- Added architecture backlog issues for intrusion orchestration, provider consolidation, durable delivery, compatibility-facade convergence, retention policy, and dependency-boundary enforcement.

### Security note

The repository no longer expects a tracked project `.env`, but any real credential that may have existed in historical commits must still be rotated before credential-cleanup work is considered complete.
