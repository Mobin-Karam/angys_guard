# Laptop Guard AI / Codex instructions

These instructions are authoritative for AI-assisted work in this repository.
More specific `AGENTS.md` files under subdirectories add or override rules for
that area.

## Mission

Laptop Guard is an owner-controlled laptop security and monitoring application.
Optimize for: **security > privacy > correctness > recoverability > simple UX >
feature breadth**.

Do not trade away security/privacy boundaries for convenience.

## Read only what the task needs

- Architecture/current risks: `docs/SYSTEM_AUDIT.md`
- Add/change/remove/fix a feature: `docs/FEATURE_LIFECYCLE.md`
- Feature module contracts/templates: `docs/EXTENDING.md`
- Find/triage/fix a bug or GitHub issue: `docs/BUG_TRIAGE_AND_FIXING.md`
- Find a file/module: `docs/FILE_REFERENCE.md`
- Configuration/secrets: `docs/CONFIGURATION.md`, `docs/SECURITY.md`
- Testing/target-device checks: `docs/TESTING.md`
- AI roles/skills/task recipes: `docs/AI_AGENT_WORKFLOW.md`
- Current execution roadmap: `docs/ROADMAP.md`
- GitHub/release process: `CONTRIBUTING.md`, `.github/REPOSITORY_SETTINGS.md`

For cross-file questions, query `graphify-out/graph.json` before opening broad
source ranges. Direct current source is always authoritative when generated
artifacts disagree.

## Runtime architecture

Primary path:

`run.sh -> laptop_guard.cli -> runtime_config -> guard.LaptopGuard`

`LaptopGuard` uses `runtime_api.build_runtime_api`, `GuardRuntimeState`, and an
explicit `FeatureManager`.

Architecture rules:

- New bot commands/callbacks belong in one focused module under
  `laptop_guard/features/`; do not grow legacy command/callback chains.
- Code that talks to the owner depends on `RuntimeApi`, not directly on
  Requests/httpx.
- Runtime transport construction belongs in `build_runtime_api()`.
- Shared live state goes through `GuardRuntimeState` / `RuntimeStateStore`.
- Prefer narrow protocols/services over passing the full guard object around.
- Keep imports side-effect-light and optional native dependencies lazy.
- Keep feature registration explicit; do not add filesystem plugin auto-discovery.

## Security and privacy hard gates

Never weaken these without an explicit user decision and a documented security
review:

- Preserve owner authorization, pairing, confirmation, and stop/unlock gates.
- Never add remote shell, arbitrary command execution, `eval`, `exec`, or a
  generic script runner reachable from remote control surfaces.
- Never add hidden capture, stealth recording, credential collection, keylogging,
  password capture, or suppression of required local privacy indicators.
- Never read, print, copy into issues, or log `.env`, `secrets.json`, stop PIN
  material, authentication tokens, private keys, or captured evidence media.
- Keep local control APIs loopback-only by default and authenticated.
- Bound recording durations, payload sizes, retries, queues, and timeouts.
- Prefer argument-list subprocess calls. Avoid `shell=True` and shell string
  composition for variable input.
- Use atomic writes and restrictive permissions for configuration/secrets.
- Reject ambiguous remote actions rather than guessing.

If a requested change conflicts with these rules, stop that part of the change,
explain the conflict, and propose the safest compatible design.

## Working procedure

1. Run/inspect `git status --short` before editing. Preserve unrelated changes.
2. Identify the issue/acceptance criteria when the task references GitHub work.
3. Read the smallest relevant source/document set.
4. For feature work, follow `docs/FEATURE_LIFECYCLE.md`; for defects, follow
   `docs/BUG_TRIAGE_AND_FIXING.md` and reproduce before changing code when practical.
5. For non-trivial changes, state the intended change boundary before editing.
6. Implement the smallest coherent patch; avoid opportunistic rewrites.
7. Add or update focused tests for behavior and failure modes.
8. Run targeted checks first, then the broader verification required below.
9. Review the diff for security/privacy regressions and accidental secrets.
10. Report what changed, what was validated, and any target-device checks still
    required.

Do not reset, clean, force checkout, overwrite unrelated work, or use destructive
Git recovery commands. Do not commit/push/merge unless the user or task explicitly
asks for that Git action.

## Available project agents

Project-scoped Codex subagents live in `.codex/agents/`:

- `architect` — read-only architecture and change planning.
- `implementer` — focused implementation work.
- `reviewer` — correctness/regression review.
- `security_reviewer` — authorization, privacy, secrets, and abuse-boundary review.
- `tester` — test strategy, failures, and verification.
- `release_manager` — release readiness and changelog/checklist work.

Use subagents when parallel specialization materially improves the result. Keep
small tasks in the main thread. The parent agent remains responsible for
reconciling findings and verifying the final patch.

## Available project skills

Reusable workflows live in `.agents/skills/` and may be invoked explicitly or
selected automatically when their descriptions match:

- `issue-to-pr` — execute a GitHub issue as a bounded implementation workflow.
- `safe-implementation` — implement changes while preserving security boundaries.
- `security-review` — review sensitive code paths and configuration.
- `test-and-verify` — choose and run focused/full verification.
- `release-readiness` — prepare a release without skipping safety checks.

## Validation

For a normal Python/runtime change, use the relevant subset first and finish with
all applicable checks:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q laptop_guard tests
bash -n install.sh run.sh doctor.sh repair-opencv.sh
.venv/bin/python -m pip check
git diff --check
```

Hardware/session/provider behavior also requires the target-device checks in
`docs/TESTING.md`; unit tests do not prove camera, microphone, lock, Wayland/X11,
systemd, or live provider behavior.

## Command-output hygiene

- Prefer quiet/concise commands (`pytest -q`, `git status --short`).
- Preserve exit codes and actionable errors.
- Do not dump secrets, full environment files, captured media, or large logs.
- For noisy failures, inspect only the relevant excerpts or delegate analysis to
  a subagent.

## Completion standard

A task is not complete until behavior, failure handling, security/privacy impact,
and tests are accounted for. Final reports should be concise and identify any
manual target-device validation that remains.