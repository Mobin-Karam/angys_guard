# Laptop Guard agent guide

Read only what the task needs:

- Architecture/current risks: `docs/SYSTEM_AUDIT.md`
- Add a feature: `docs/EXTENDING.md`
- Find a file: `docs/FILE_REFERENCE.md`
- Configuration/security: `docs/CONFIGURATION.md`, `docs/SECURITY.md`
- Validation: `docs/TESTING.md`

For cross-file questions, query the existing `graphify-out/graph.json` before
opening broad source ranges; direct current source remains authoritative.

## Runtime path

`run.sh -> laptop_guard.cli -> runtime_config -> guard.LaptopGuard`

`LaptopGuard` uses `runtime_api.build_runtime_api`, `GuardRuntimeState`, and an
explicit `FeatureManager`. New bot commands/callbacks belong in one module under
`laptop_guard/features/`; do not grow the legacy command/callback chains.

## Rules

- Preserve owner authorization and confirmation gates.
- Never add remote shell/eval/exec, hidden capture, credential logging, or
  privacy-light suppression.
- Use argument-list subprocess calls, bounded durations/sizes, loopback defaults,
  atomic writes, and explicit feature registration.
- Do not read or print `.env`, `secrets.json`, stop PIN data, or captured media.
- Keep imports side-effect-light and optional native dependencies lazy.
- Add focused tests for every route and failure mode.
- Before completion: compile, tests, shell syntax, `pip check`, and `git diff --check`.
- Preserve unrelated working-tree changes; never reset or clean the checkout.
