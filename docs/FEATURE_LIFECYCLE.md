# Feature lifecycle: add, change, fix, and remove features

Use this guide when a Laptop Guard capability needs to be added, modified,
deprecated, or removed. It is deliberately tied to the current architecture so a
maintainer or AI agent does not create a second parallel implementation by
accident.

Start with the repository-wide rules in `AGENTS.md`. When editing runtime code,
`laptop_guard/AGENTS.md` also applies. For tests, read `tests/AGENTS.md`.

## 1. Decide what kind of feature this is

Before editing code, classify the request. This determines where the change
belongs.

| Feature type | First places to inspect |
|---|---|
| Bot command/callback feature | `laptop_guard/features/`, `FeatureManager`, `LaptopGuard` installation point |
| CLI command | `laptop_guard/cli.py` plus the service/module it calls |
| Setup/configuration option | `models.py`, `config.py`, `setup_wizard.py`, `runtime_config.py` |
| Provider/API behavior | `runtime_api.py`, `bale_api.py`, `providers/` |
| Camera/input/audio/screen capability | corresponding module plus `tests_manual.py` and `doctor.py` |
| Intrusion/warning/lock behavior | `guard.py`, `warning_sequence.py`, `system_actions.py`, state/events |
| Service/autostart behavior | `service.py`, CLI commands, config startup/security settings |
| Local control API | `control_api.py`, configuration, authorization/token storage |
| UI/chat behavior | `chat_surface.py`, `chat_window.py`, `text_direction.py` |

Use `docs/FILE_REFERENCE.md` when the owning module is unclear. Use
`docs/SYSTEM_AUDIT.md` for the current runtime flow and known architectural
boundaries.

## 2. Trace the existing path before adding code

Do not start by creating a new module. First trace how the closest existing
behavior works.

For a bot feature, the normal path is approximately:

```text
provider message/callback
        |
        v
LaptopGuard authorization/dispatch
        |
        v
FeatureManager
        |
        v
feature handler
        |
        v
narrow host/service capability
```

`FeatureManager` owns command names, callback-prefix conflicts, installation
order, and start/stop lifecycle. Feature command names and callback prefixes must
remain unique.

For non-command capabilities, find the existing boundary instead of routing
around it:

- owner/provider communication: `RuntimeApi` / existing provider layer;
- persistent live state: `GuardRuntimeState` / `RuntimeStateStore`;
- events/history: event/storage modules;
- configuration: dataclass model + config persistence/migration;
- OS actions: fixed functions in `system_actions.py` / `system.py`;
- app execution: existing allowlisted app manager, never arbitrary shell.

## 3. Adding a feature

### Step A — define behavior and safety rules

Write down:

1. who can invoke it;
2. what input it accepts;
3. what side effects it can cause;
4. what configuration it needs;
5. how it fails safely;
6. what data it reads, records, sends, or stores;
7. how it can be disabled/rolled back.

If the feature touches authentication, remote control, secrets, camera,
microphone, screen/input capture, subprocesses, networking, service/autostart,
or OS locking, plan a security review before implementation.

### Step B — extend the narrowest existing abstraction

For a new bot feature, prefer one module under `laptop_guard/features/`. Follow
`docs/EXTENDING.md` and existing features such as `system_info.py`,
`failed_login.py`, or `sound_detection.py`.

Do not add generic filesystem, shell, `eval`, `exec`, or arbitrary command
surfaces. Remote actions must be fixed, explicit, authorization-gated, and
bounded.

### Step C — add configuration only when necessary

If configuration is needed:

1. add the field to the appropriate dataclass in `models.py`;
2. choose a safe default;
3. preserve older configurations through `config.py` migration/loading;
4. expose it through guided setup/reconfiguration when ordinary users need it;
5. update `doctor.py` if readiness depends on an external package, binary,
   permission, or device;
6. never put secrets into normal TOML/log output when they belong in protected
   secret storage.

### Step D — register the feature explicitly

Laptop Guard intentionally avoids filesystem auto-discovery of runtime plugins.
Install/register the feature explicitly beside the other runtime features.

This prevents an unexpected local file from silently becoming executable product
behavior.

### Step E — add tests before calling it complete

At minimum test:

- registration and conflicts;
- authorized success behavior;
- invalid/empty/bounded input;
- authorization denial when applicable;
- timeout/dependency/provider failure;
- cleanup/start/stop if the feature owns a thread/process/resource;
- configuration migration/defaults if config changed.

Hardware-facing features should have fake/mocked backend tests and a separate
manual target-device checklist.

Use `docs/TESTING.md` and the `$test-and-verify` skill.

## 4. Changing an existing feature

Treat a modification as a compatibility change, not just an edit.

Before changing behavior, answer:

- Does another command/callback/service call this path?
- Is persisted configuration/state/event data involved?
- Does a test encode the old expected behavior?
- Does the user-visible command/setup/doctor text need updating?
- Will an older config still start safely?
- Does the change alter authorization, privacy, or remote-control behavior?

Prefer changing the owner module rather than adding a special case in
`guard.py` or another caller.

For larger changes, keep the old and new behavior behind an explicit migration or
configuration transition only when backward compatibility genuinely requires it.
Do not keep dead duplicate implementations indefinitely.

## 5. Fixing a feature

For a defect, use `docs/BUG_TRIAGE_AND_FIXING.md` first. A safe feature fix should
normally follow this order:

```text
reproduce -> identify owner -> write failing regression test -> smallest fix
-> targeted tests -> security/review if needed -> full verification
```

A bug fix is not complete if it only suppresses the visible error while leaving
the incorrect state, authorization path, retry loop, or resource leak in place.

## 6. Removing a feature safely

Removal is more than deleting one Python file.

### Inventory every reference

Search for the feature name, command names, callback prefixes, configuration
fields, docs, tests, setup prompts, doctor checks, menu buttons/text, imports,
service hooks, event kinds, and migrations.

`docs/FILE_REFERENCE.md` and the repository search/index are useful here.

### Decide migration behavior

For each removed configuration field:

- harmless unknown legacy value: ignore/drop safely during load;
- field affects a replacement behavior: add an explicit migration;
- secret field: remove references but do not expose/echo the old value;
- database/event history: normally preserve historical rows even when no new
  events are produced.

### Remove in dependency order

A typical order is:

1. stop exposing the command/menu/setup option;
2. remove runtime registration/startup;
3. remove callers and implementation;
4. remove unused config/model fields with migration handling;
5. remove obsolete doctor/manual-test paths;
6. delete or rewrite tests;
7. update user/security docs and `FILE_REFERENCE.md`;
8. run the full verification suite.

Never remove an authorization/privacy guard because the feature using it was
removed until you have proven no other capability depends on that guard.

## 7. AI-agent workflow for feature work

Use the repo-local Codex roles and skills instead of asking one agent to do a
large opaque rewrite.

### Add a feature

```text
Have architect map the smallest implementation for <feature>. Use
FEATURE_LIFECYCLE.md, EXTENDING.md, FILE_REFERENCE.md, and SYSTEM_AUDIT.md.
Then implement it with safe-implementation, have tester verify it, and have
reviewer plus security_reviewer review the final diff if it touches a trust
boundary.
```

Or:

```text
$safe-implementation add <feature> using the existing feature/runtime boundaries.
Then $test-and-verify the change.
```

### Modify a feature

```text
Have architect trace every caller and persisted/config compatibility impact of
<feature>. Then have implementer make only the bounded change and add regression
tests. Have reviewer inspect the final diff.
```

### Remove a feature

```text
Have architect produce a removal dependency map for <feature>, including config,
commands, callbacks, tests, docs, migrations, and security guards. Do not edit
anything yet. After I review the map, have implementer remove it in dependency
order and tester verify no references remain.
```

### Feature work from a GitHub issue

```text
$issue-to-pr implement issue #<number>. Follow docs/FEATURE_LIFECYCLE.md and use
security_reviewer for any authorization, secret, capture, network, process, or
OS-control change.
```

## 8. Completion checklist

A feature change is complete only when all applicable items are true:

- [ ] correct owner module/abstraction used;
- [ ] no parallel/duplicate execution path was introduced;
- [ ] authorization/privacy boundaries preserved;
- [ ] configuration has safe defaults and migration behavior;
- [ ] setup/doctor/help/menu text matches the new behavior;
- [ ] focused success/failure tests exist;
- [ ] target-device checks are identified when hardware/session dependent;
- [ ] docs and `FILE_REFERENCE.md` are updated;
- [ ] `pytest`, compile checks, shell syntax, `pip check`, and `git diff --check`
      pass as applicable;
- [ ] final reviewer/security review completed for non-trivial sensitive changes.
