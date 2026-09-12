# AI agent workflow

Laptop Guard is configured for repository-aware AI coding with OpenAI Codex as
the primary agent environment. `AGENTS.md` is the single authoritative project
policy; other instruction files are compatibility layers.

This guide explains **which AI role/workflow to use for each maintenance task**.
For the engineering procedure itself, use:

- `docs/FEATURE_LIFECYCLE.md` for adding/changing/fixing/removing features;
- `docs/BUG_TRIAGE_AND_FIXING.md` for defect investigation and repair;
- `docs/TESTING.md` for verification and target-device checks.

## OpenAI Codex / VS Code

Open the repository root in VS Code and use the Codex extension from that
workspace. Project configuration is under `.codex/` and reusable skills are under
`.agents/skills/`.

Project-local Codex hooks/configuration should only be enabled after you trust the
repository/branch. Review `.codex/hooks.json` and `.codex/hooks/` when working from
a fork or external contribution.

Codex instruction scope is hierarchical:

1. root `AGENTS.md` applies repository-wide;
2. `laptop_guard/AGENTS.md` adds runtime rules;
3. `tests/AGENTS.md` adds test/fixture rules;
4. `docs/AGENTS.md` adds documentation rules.

The singular `AGENT.md` is only a compatibility pointer; do not maintain a second
copy of the rules there.

## Custom Codex agents

The project defines these roles under `.codex/agents/`:

| Agent | Best use | Editing |
|---|---|---|
| `architect` | trace architecture, callers, dependencies, migrations, plan a bounded change | read-only |
| `implementer` | make the approved focused code/test change | yes |
| `reviewer` | find correctness, regression, maintainability problems in a final diff | read-only |
| `security_reviewer` | authorization, secrets, capture/privacy, network/process/OS-control review | read-only |
| `tester` | reproduce failures, choose tests, triage CI, verify fixes | as permitted by parent task |
| `release_manager` | version/changelog/CI/security/release readiness | focused release work |

Do not spawn agents for trivial single-file edits when direct work is clearer.
For non-trivial work, separate **investigation**, **implementation**, and
**verification** so the same reasoning path does not silently validate itself.

## Project skills

Skills under `.agents/skills/` describe repeatable workflows. Codex may select
them automatically when the task matches their description, or they can be
invoked explicitly by name.

| Skill | Use it when |
|---|---|
| `$issue-to-pr` | there is a GitHub issue/roadmap item and the requested result is a bounded implementation/PR workflow |
| `$safe-implementation` | changing runtime/setup/provider/hardware/security-sensitive product behavior |
| `$security-review` | reviewing trust boundaries or a sensitive final diff |
| `$test-and-verify` | reproducing/validating a change and deciding what still requires manual testing |
| `$release-readiness` | deciding whether a version is ready for release |

## Task router

Use this table before prompting an agent.

| Task | Start with | Then |
|---|---|---|
| Add new feature | `architect` for non-trivial design, or `$safe-implementation` for small bounded work | `tester`, `reviewer`, security review if sensitive |
| Change existing feature | `architect` to trace callers/compatibility when cross-module | `implementer` -> `tester` -> `reviewer` |
| Remove feature | `architect` to produce dependency/removal map first | `implementer` -> `tester`; verify no references/migrations broken |
| Unknown bug | `architect` + `tester` to classify/reproduce | implement only after root cause is narrowed |
| Known reproducible bug | `implementer` with regression test | `tester` -> `reviewer` |
| Security-sensitive bug | `architect` | `implementer` -> `tester` -> `security_reviewer` |
| CI failure | `tester` | `implementer` only if a repo fix is actually required |
| GitHub issue | `$issue-to-pr` | add architect/security review when appropriate |
| Release | `$release-readiness` / `release_manager` | resolve blockers, rerun checks, target-device validation |

## Feature workflows

### Add a feature

For a non-trivial feature:

```text
Have architect plan <feature> using docs/FEATURE_LIFECYCLE.md,
docs/EXTENDING.md, docs/FILE_REFERENCE.md, and docs/SYSTEM_AUDIT.md.
Do not edit yet. Return owning modules, security/privacy impact, config/migration
impact, tests, target-device checks, and the smallest implementation sequence.
```

After approving the plan:

```text
Have implementer implement the approved feature plan only. Add focused success,
failure, and denial tests. Then have tester run the relevant verification and
reviewer inspect the final diff. Use security_reviewer if any trust boundary is
touched.
```

For a small clear addition:

```text
$safe-implementation add <feature> following docs/FEATURE_LIFECYCLE.md and the
existing feature/runtime boundaries. Then $test-and-verify it.
```

### Modify a feature

```text
Have architect trace every caller, command/callback route, config field,
persisted state/event dependency, test, and documentation impact for <feature>.
Then have implementer make the smallest compatible change. Add regression tests,
then have reviewer inspect the diff.
```

### Remove a feature

Do not ask an implementation agent to immediately delete files. First map the
removal:

```text
Have architect prepare a removal map for <feature> using
FEATURE_LIFECYCLE.md. Include commands/callbacks, registration, imports, config,
migrations, setup/doctor/help/menu paths, tests, docs, events/state, and security
guards. Identify what historical data/config must remain compatible. Do not edit.
```

Then:

```text
Have implementer remove <feature> in the dependency order from the approved map.
Have tester search for stale references and run focused/full applicable checks.
Have security_reviewer confirm no shared authorization/privacy guard was removed
by mistake.
```

## Bug and issue workflows

### Unknown-cause bug

```text
Have architect investigate this bug without editing code. Follow
docs/BUG_TRIAGE_AND_FIXING.md. Use the symptom/error plus FILE_REFERENCE.md,
SYSTEM_AUDIT.md, CONFIGURATION.md, SECURITY.md, and TESTING.md as needed.
Return:
1. classification and likely owning path;
2. evidence supporting/contradicting each likely cause;
3. minimal reproduction;
4. regression test location;
5. smallest safe fix plan;
6. manual target-device evidence still needed.
```

Use `tester` in parallel when reproduction/test triage can be isolated from
architecture tracing.

### Reproducible bug

```text
Have implementer reproduce and fix this defect following
BUG_TRIAGE_AND_FIXING.md. Add or update a failing regression test first where
practical. Fix the root cause in the owning abstraction; do not add a parallel
workaround. Then have tester verify the exact reproduction plus applicable full
checks and have reviewer inspect the final diff.
```

### Security-sensitive bug

```text
Have architect trace the failing trust boundary first. Then have implementer make
the bounded fix and regression tests. Have tester verify success and denial
paths. Finally have security_reviewer review authorization, secret handling,
remote-control surface, capture/privacy, network, subprocess, and OS-control
impact before completion.
```

### Existing GitHub issue

```text
$issue-to-pr implement issue #<number>. Start by classifying it with
BUG_TRIAGE_AND_FIXING.md or FEATURE_LIFECYCLE.md. Preserve the issue acceptance
criteria and do not merge until the required tests/checks are green.
```

### CI failure

```text
Have tester triage the failing CI run. Determine whether it is:
- a product-code regression;
- a test/fixture defect;
- packaging/dependency incompatibility;
- Python-version incompatibility;
- an environment-only/flaky failure.
Return the exact failing step/test, root-cause evidence, and smallest next fix or
diagnostic. Do not change unrelated code.
```

## Agent handoff format

For non-trivial tasks, make agents hand off structured evidence rather than vague
summaries.

Architect should return:

```text
Scope:
Owning paths/symbols:
Current flow:
Root cause or design constraint:
Security/privacy impact:
Config/migration impact:
Implementation sequence:
Tests:
Manual validation:
```

Implementer should return:

```text
Changed files:
Behavior changed:
Tests added/updated:
Checks run:
Known/manual validation remaining:
```

Reviewer/security reviewer should return findings ordered by severity and include
concrete paths/symbols and the smallest remediation.

Tester should return:

```text
Reproduction result:
Targeted tests:
Full checks:
Failures:
Manual target-device checks still required:
```

## Hooks

`.codex/hooks.json` configures three guardrails:

- `SessionStart`: injects a short security/project reminder;
- `PreToolUse`: blocks destructive Git/repository deletion and direct protected
  secret-file reads/edits;
- `PostToolUse`: reminds the agent to run regression/security verification after
  runtime edits.

Hooks are intentionally local and dependency-free. They do not call external
services, commit code, or inspect secrets.

Hooks are guardrails, not proof of correctness. Agents must still follow the
feature/bug/testing playbooks.

## GitHub Copilot and other agents

- GitHub Copilot repository instructions: `.github/copilot-instructions.md`.
- Claude-oriented compatibility entry: `CLAUDE.md`.
- Gemini-oriented compatibility entry: `GEMINI.md`.

These files defer to `AGENTS.md` so security policy does not drift between tools.

## Recommended GitHub issue-to-PR workflow

For planned repository work:

1. Start from the GitHub issue and acceptance criteria.
2. Classify the issue as feature/change/removal/bug/security/docs/release.
3. Read `FEATURE_LIFECYCLE.md` or `BUG_TRIAGE_AND_FIXING.md` as applicable.
4. Use `$issue-to-pr` for non-trivial issues.
5. Use `architect` before cross-module/security-sensitive design changes.
6. Use `implementer` or the main agent for the bounded patch.
7. Use `tester` / `$test-and-verify` before completion.
8. Use `security_reviewer` for authentication, secrets, remote control, capture,
   process, service, network, or OS-control changes.
9. Use `reviewer` on non-trivial final diffs.
10. Open/merge a PR only after checks and documentation are accounted for.

The AI layer is a workflow aid, not a substitute for required target-device
validation listed in `docs/TESTING.md`.
