# Feature lifecycle: add, change, fix, and remove features

Use this guide when a Laptop Guard capability needs to be added, modified,
deprecated, or removed. It is tied to the current architecture so maintainers and
AI agents do not create a second parallel implementation by accident.

Start with `AGENTS.md` and `docs/GRAPHIFY_NAVIGATION.md`. Runtime edits also
inherit `laptop_guard/AGENTS.md`; tests inherit `tests/AGENTS.md`.

## 1. Map the existing feature neighborhood with Graphify

Before creating/editing/removing a module, check Graphify freshness and map the
current feature surface:

```bash
graphify query "where is <feature/behavior> implemented?"
graphify explain "<feature/class/function>"
graphify query "what depends on <feature/symbol>?"
graphify query "what tests cover <feature/symbol>?"
graphify path "<command/input>" "<state/store/side effect>"
```

Use the result to identify:

- owning module/class/function;
- registration/entry points;
- callers/downstream dependents;
- commands/callbacks/UI/help/setup surfaces;
- configuration/migrations;
- state/events/storage/outbox/evidence;
- provider/network/hardware/OS adapters;
- authorization/privacy/security guards;
- tests and canonical docs.

Then open only those current files/ranges and confirm the relationships. Do not
load the complete `graphify-out/graph.json` into context. If the graph is stale and
can be refreshed, run `graphify update .`; otherwise document the narrow fallback.

For removals and security-sensitive changes, graph output alone is insufficient:
confirm every important caller/guard/migration in current source/tests.

## 2. Decide what kind of feature this is

Graphify should normally identify the owner; this table is a fallback/curated
orientation map:

| Feature type | Typical owner area |
|---|---|
| Bot command/callback feature | `laptop_guard/features/`, `FeatureManager`, runtime installation point |
| CLI command | `laptop_guard/cli.py` plus called service/module |
| Setup/configuration option | `models.py`, `config.py`, `setup_wizard.py`, `runtime_config.py` |
| Provider/API behavior | `runtime_api.py`, provider adapters |
| Camera/input/audio/screen | subsystem module + `tests_manual.py` + `doctor.py` |
| Intrusion/warning/lock | runtime orchestration, warning/system-action/state/event boundaries |
| Service/autostart | `service.py`, CLI, startup/security config |
| Local control API | `control_api.py`, configuration, auth/token storage |
| UI/chat behavior | chat/UI/text-direction modules |

Use `docs/FILE_REFERENCE.md` for curated ownership context and
`docs/ARCHITECTURE.md` / `docs/SYSTEM_AUDIT.md` for intended/current boundaries.

## 3. Adding a feature

### A. Define behavior and safety rules

Write down:

1. who can invoke it;
2. accepted inputs;
3. side effects;
4. required configuration;
5. safe failure behavior;
6. data read/recorded/sent/stored;
7. disable/rollback behavior.

If it touches authentication, remote control, secrets, capture/input, subprocess,
networking, service/autostart, or OS locking, plan a security review.

### B. Extend the narrowest existing abstraction

Use the Graphify map to find the current extension point. For bot features,
prefer one focused module under `laptop_guard/features/` and follow
`docs/EXTENDING.md`.

Do not add generic filesystem/shell/`eval`/`exec`/arbitrary command surfaces.
Remote actions must be fixed, explicit, authorization-gated, and bounded.

### C. Add configuration only when necessary

When configuration is required:

1. add the field to the owning dataclass;
2. choose a safe default;
3. preserve older configs through migration/loading;
4. expose guided setup/reconfiguration when ordinary users need it;
5. update doctor/readiness checks for external dependencies/capabilities;
6. keep secrets in protected secret storage, never normal logs/TOML.

### D. Register explicitly

Laptop Guard intentionally avoids filesystem auto-discovery of runtime plugins.
Install/register features explicitly beside existing runtime features.

### E. Add tests

Use Graphify to locate nearby/connected tests, then cover:

- registration/conflicts;
- authorized success;
- invalid/bounded input;
- authorization denial;
- dependency/provider timeout/failure;
- cleanup/start/stop for owned resources;
- config migration/defaults when changed.

Hardware-facing features need fake/mocked backend coverage plus manual target-device
checks. Use `docs/TESTING.md` and `$test-and-verify`.

## 4. Changing an existing feature

Treat a modification as a compatibility change. Use Graphify to map all dependents
before editing, then confirm them in source/tests.

Answer:

- which commands/callbacks/services call this path;
- what persisted config/state/event data is involved;
- which tests encode existing behavior;
- which user-visible setup/doctor/help/menu/docs need updating;
- whether old configs/data still load safely;
- whether authorization/privacy/remote-control behavior changes.

Prefer changing the owner abstraction instead of adding special cases in callers.
Use explicit migration/compatibility only when genuinely required; do not leave
permanent duplicate implementations.

## 5. Fixing a feature

Use `docs/BUG_TRIAGE_AND_FIXING.md` first.

```text
Graphify map -> reproduce -> confirm owner -> failing regression test
-> smallest root-cause fix -> targeted tests -> review/security review
-> broader verification -> graph refresh
```

Do not merely suppress a visible error while incorrect state, authorization,
retry, persistence, or resource behavior remains.

## 6. Removing a feature safely

Removal is more than deleting one file.

### Inventory every reference with Graphify first

Use `query`, `explain`, and `path` to build a removal map covering feature names,
commands, callbacks, registration, imports/callers, config, migration, docs, tests,
setup/doctor/help/menu, event kinds, state/storage, provider/hardware adapters, and
security guards.

Then verify all important edges with source search/current files. This is one of
the cases where inferred/missing graph edges must not be trusted blindly.

### Decide migration behavior

For removed configuration/data:

- harmless legacy values may be ignored/dropped safely during load;
- replacement behavior needs explicit migration;
- secret fields may have references removed but values must never be exposed;
- historical database/events should normally remain readable unless a deliberate
  retention/migration decision says otherwise.

### Remove in dependency order

Typical order:

1. stop exposing command/menu/setup surfaces;
2. remove registration/startup;
3. remove callers and implementation;
4. migrate/remove config/model fields safely;
5. remove obsolete doctor/manual-test paths;
6. delete/rewrite tests;
7. update docs/file ownership;
8. run Graphify again to detect remaining structural references;
9. run full verification.

Never remove a shared authorization/privacy guard until all graph/source evidence
confirms no other capability depends on it.

## 7. AI-agent workflow

When scope is unclear:

```text
navigator -> architect -> implementer -> tester -> reviewer
                                   \-> security_reviewer when sensitive
```

Navigator handoff should include graph freshness, queries/paths, owners,
dependencies, tests/docs, and inferred/uncertain edges. Downstream agents should
consume that handoff rather than rediscovering the whole repository.

### Add/change

```text
Have navigator Graphify-map <feature>. Have architect plan from that map and the
feature/architecture docs. Have implementer change only the approved scope. Have
tester verify graph-connected coverage and reviewer inspect final blast radius.
```

### Remove

```text
Have navigator and architect produce a Graphify + source-confirmed removal map for
<feature>. Do not edit until commands/callbacks/config/migrations/state/events/
tests/docs/security guards are accounted for. Then remove in dependency order and
use Graphify again to look for structural leftovers.
```

### GitHub issue

```text
$issue-to-pr implement issue #<number>. It must map the issue to code/tests/docs
with Graphify before implementation and preserve the acceptance criteria.
```

## 8. Completion checklist

- [ ] Graphify freshness checked and feature neighborhood mapped, or fallback reason recorded;
- [ ] correct owner abstraction confirmed in current source;
- [ ] no parallel/duplicate execution path introduced;
- [ ] authorization/privacy boundaries preserved;
- [ ] config has safe defaults/migration behavior;
- [ ] setup/doctor/help/menu/docs match behavior;
- [ ] focused success/failure/denial tests exist;
- [ ] target-device checks identified for hardware/session behavior;
- [ ] `docs/FILE_REFERENCE.md` updated when ownership changed;
- [ ] Graphify refreshed after material relationship changes when available;
- [ ] applicable pytest/compile/shell/pip/diff checks pass;
- [ ] reviewer/security review completed for non-trivial sensitive changes.
