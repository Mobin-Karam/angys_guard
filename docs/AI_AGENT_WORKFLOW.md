# AI agent workflow

Laptop Guard is configured for repository-aware AI coding with OpenAI Codex as
the primary agent environment. `AGENTS.md` is the single authoritative project
policy; other instruction files are compatibility layers.

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

- `architect` — architecture mapping/planning, read-only;
- `implementer` — focused implementation;
- `reviewer` — correctness/regression review, read-only;
- `security_reviewer` — security/privacy review, read-only;
- `tester` — tests/checks/failure triage;
- `release_manager` — release readiness.

Example requests:

```text
Have architect map the smallest change for issue #2, then give me the plan.

Implement issue #2. Use reviewer and security_reviewer before completion.

Have tester verify the current diff and return only failures plus required manual checks.
```

Do not spawn agents for trivial single-file edits when direct work is clearer.

## Project skills

Skills under `.agents/skills/` describe repeatable workflows. Codex may select
them automatically when the task matches their description, or they can be
invoked explicitly by name.

Examples:

```text
$issue-to-pr implement GitHub issue #2

$safe-implementation add the requested doctor check

$security-review review the current branch against main

$test-and-verify verify this fix

$release-readiness assess v11.2
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

## GitHub Copilot and other agents

- GitHub Copilot repository instructions: `.github/copilot-instructions.md`.
- Claude-oriented compatibility entry: `CLAUDE.md`.
- Gemini-oriented compatibility entry: `GEMINI.md`.

These files defer to `AGENTS.md` so security policy does not drift between tools.

## Recommended issue workflow

For planned repository work:

1. Start from the GitHub issue and acceptance criteria.
2. Use `issue-to-pr` for non-trivial issues.
3. Use `architect` before cross-module/security-sensitive design changes.
4. Use `implementer` or the main agent for the bounded patch.
5. Use `tester` / `test-and-verify` before completion.
6. Use `security_reviewer` for authentication, secrets, remote control, capture,
   process, service, or network-boundary changes.
7. Use `reviewer` on non-trivial final diffs.
8. Open a PR only after checks and documentation are accounted for.

The AI layer is a workflow aid, not a substitute for required target-device
validation listed in `docs/TESTING.md`.
