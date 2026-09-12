# AI agent workflow

Laptop Guard is configured for repository-aware AI coding with OpenAI Codex as
the primary agent environment. `AGENTS.md` is the authoritative project policy;
other instruction files are compatibility layers.

## First step for every repository-knowledge task: Graphify

Before an agent broadly reads/searches source, tests, or docs, follow
`docs/GRAPHIFY_NAVIGATION.md`.

```text
request / issue / bug / question
        |
        v
Graphify freshness check
        |
        v
graphify query / explain / path
        |
        v
small graph handoff: nodes + edges + paths + tests/docs
        |
        v
specialist agent opens only minimal authoritative files
```

Use `navigator` or `$graphify-navigation` when ownership/scope is unclear or
cross-file discovery is substantial. The goal is that architect/implementer/tester/
reviewers receive a compact map rather than each independently loading the same
repository context.

Do not load all of `graphify-out/graph.json` into an AI conversation. Check the
build commit in `GRAPH_REPORT.md`; refresh stale graphs with `graphify update .`
when available. Current source/tests remain final authority.

For the engineering procedure itself, use:

- `docs/GRAPHIFY_NAVIGATION.md` for discovery/freshness/fallback/token discipline;
- `docs/FEATURE_LIFECYCLE.md` for adding/changing/fixing/removing features;
- `docs/BUG_TRIAGE_AND_FIXING.md` for defect investigation and repair;
- `docs/TESTING.md` for verification and target-device checks.

## OpenAI Codex / VS Code

Open the repository root in VS Code and use the Codex extension from that
workspace. Project configuration is under `.codex/` and reusable skills are under
`.agents/skills/`.

Project-local hooks/configuration should only be enabled after trusting the
repository/branch. `SessionStart` reports the Graphify build/freshness state and
reminds the session to navigate with Graphify before broad reads.

Codex instruction scope is hierarchical:

1. root `AGENTS.md` applies repository-wide;
2. `laptop_guard/AGENTS.md` adds runtime rules;
3. `tests/AGENTS.md` adds test/fixture rules;
4. `docs/AGENTS.md` adds documentation rules.

`AGENT.md` is only a compatibility pointer.

## Custom Codex agents

| Agent | Best use | Editing |
|---|---|---|
| `navigator` | Graphify-first ownership, callers, dependencies, tests/docs, change-impact map | read-only |
| `architect` | graph-backed architecture, compatibility, migration, bounded change plan | read-only |
| `implementer` | approved focused code/test change from confirmed scope | yes |
| `reviewer` | correctness/regression/blast-radius review | read-only |
| `security_reviewer` | Graphify-backed trust-boundary/security/privacy review | read-only |
| `tester` | graph-guided test discovery, reproduction, CI/failure triage | as permitted by parent task |
| `release_manager` | release impact/freshness/version/CI/security/readiness | focused release work |

For non-trivial work, separate discovery, implementation, and verification:

```text
navigator -> architect (when design needed) -> implementer -> tester -> reviewer
                                                    \-> security_reviewer
```

Skip `navigator` only when the exact owner/files/tests are already known and no
repository discovery is required.

## Project skills

| Skill | Use it when |
|---|---|
| `$graphify-navigation` | locating owners/files/symbols/callers/tests/docs or estimating impact |
| `$issue-to-pr` | executing a GitHub issue/roadmap item through a bounded PR workflow |
| `$safe-implementation` | changing runtime/setup/provider/hardware/security-sensitive behavior |
| `$security-review` | reviewing trust boundaries or a sensitive final diff |
| `$test-and-verify` | selecting/validating tests and accounting for manual checks |
| `$release-readiness` | deciding whether a version is ready for release |

Every workflow skill inherits the Graphify-first discovery policy.

## Task router

| Task | Graphify step | Specialist flow |
|---|---|---|
| Understand repository/component | `navigator` / `$graphify-navigation` | open only returned authoritative paths |
| Find owner/file/symbol | `query` / `explain` | confirm in source |
| Trace A to B | `path` | inspect returned call/dependency chain |
| Add feature | map extension point/callers/config/tests | architect when non-trivial -> implementer -> tester -> reviewer |
| Modify feature | map current owner/dependents/tests | architect for cross-module -> implementer -> tester -> reviewer |
| Remove feature | map every caller/config/state/test/doc edge | architect removal map -> implementer -> tester -> security review if sensitive |
| Unknown bug | connect symptom/entry point to owner/tests | navigator + tester/architect -> implement after root cause |
| Reproducible bug | map owner + regression coverage | implementer -> tester -> reviewer |
| Security bug | trace entry to trust boundaries | architect -> implementer -> tester -> security_reviewer |
| CI failure | map failing test/module/dependency | tester -> implementation only if repo fix needed |
| GitHub issue | map issue concepts to code/test/docs | `$issue-to-pr` |
| Release | map changed communities/surfaces/tests/docs | `$release-readiness` / release_manager |

## Feature workflow

For a non-trivial feature:

```text
Have navigator map <feature> using Graphify first. Return graph freshness,
owning symbols, callers/dependencies, config/state/storage, tests/docs, and trust
boundaries. Do not edit.

Then have architect plan the smallest change using that map plus
FEATURE_LIFECYCLE.md / ARCHITECTURE.md as applicable.
```

After approval:

```text
Have implementer implement only the approved scope. Use the navigator/architect
handoff rather than rediscovering the repository broadly. Add focused success,
failure, and denial tests. Then have tester verify and reviewer inspect the final
diff. Use security_reviewer for sensitive boundaries.
```

For feature removal, require Graphify impact mapping plus source confirmation for
registration, imports/callers, commands/callbacks, config/migrations, state/events,
setup/doctor/help/menu, tests, docs, and shared security guards before deletion.

## Bug workflow

For unknown cause:

```text
Have navigator connect this symptom/error to likely owners and tests with Graphify.
Have tester reproduce the smallest case. Have architect reason about root cause
only after that graph/source evidence is available. Do not edit until the cause is
sufficiently narrowed.
```

For a known reproducible bug, use Graphify to confirm the owning abstraction and
connected regression test surface, then make the smallest root-cause fix.

## Review workflow

Reviewer/security reviewer should not scan the entire repository by default.
Start from changed symbols/files, use Graphify to find callers/downstream effects,
then inspect only relevant current source/tests.

Security review should use graph paths to connect the changed surface to:

- owner authorization/pairing/confirmation;
- secrets/config;
- provider/network/local API;
- state/storage/outbox/evidence;
- camera/microphone/screen/input;
- subprocess/OS lock/power/service;
- stop/unlock behavior.

All important/inferred relationships must be confirmed in current source before a
security finding is treated as fact.

## Test workflow

Tester should ask Graphify what tests cover the changed/failing symbols before
searching the entire suite. Run the smallest connected tests first, then broader
applicable/full checks from `docs/TESTING.md`.

## Agent handoff format

Navigator:

```text
Graph freshness:
Graphify query/explain/path used:
Relevant nodes/edges:
Owning paths/symbols:
Connected tests/docs:
Inferred/uncertain relationships:
Next minimal read:
```

Architect:

```text
Graph/source scope:
Current flow:
Design/root-cause constraint:
Security/privacy impact:
Config/migration impact:
Implementation sequence:
Tests/manual validation:
```

Implementer:

```text
Changed files:
Behavior changed:
Tests added/updated:
Checks run:
Graph refresh/freshness:
Manual validation remaining:
```

Reviewer/security reviewer returns findings by severity with concrete paths/symbols
and relevant graph impact/trust paths.

Tester:

```text
Graph-to-test mapping:
Reproduction result:
Targeted tests:
Full checks:
Failures:
Manual target-device checks:
```

## Hooks

`.codex/hooks.json` configures:

- `SessionStart`: project/security reminder plus Graphify freshness status;
- `PreToolUse`: blocks destructive Git/repository deletion and protected secret
  reads/edits;
- `PostToolUse`: reminds agents about regression/security verification after edits.

Hooks do not call Graphify automatically or modify generated graph files. They
report navigation state; the agent/human decides when to refresh Graphify.

## GitHub Copilot and other agents

- GitHub Copilot: `.github/copilot-instructions.md` plus path-scoped instructions.
- Claude compatibility: `CLAUDE.md`.
- Gemini compatibility: `GEMINI.md`.
- Reusable prompt: `.github/prompts/graphify-navigation.prompt.md`.

All defer to `AGENTS.md` and `docs/GRAPHIFY_NAVIGATION.md`, so switching tools does
not change repository navigation policy.

## Recommended issue-to-PR workflow

1. Read issue/acceptance criteria.
2. Check Graphify freshness.
3. Use Graphify to map issue -> owner/callers/dependencies/tests/docs.
4. Confirm map in minimal source/tests.
5. Classify via feature/bug/architecture/security docs.
6. Use `$issue-to-pr`; add architect/security review when appropriate.
7. Implement bounded patch.
8. Use tester / `$test-and-verify`.
9. Use reviewer/security_reviewer on non-trivial/sensitive diffs.
10. Refresh Graphify after material relationship changes when available.
11. Open/merge only after required checks/docs/manual validation are accounted for.

The AI layer and Graphify are navigation/workflow aids, not substitutes for
required target-device validation or direct source verification.
