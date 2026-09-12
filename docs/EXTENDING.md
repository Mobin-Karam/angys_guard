# Extending Laptop Guard

This document is the **implementation template** for adding a feature module. For
the full lifecycle—including deciding where a feature belongs, modifying existing
behavior, fixing defects, safe removal, configuration/migration, and AI-agent
workflows—read `docs/FEATURE_LIFECYCLE.md` first.

For a reported defect, use `docs/BUG_TRIAGE_AND_FIXING.md` before changing code.

The feature system is intentionally explicit: adding a feature should require
one small module, one registration line, and focused tests. No filesystem plugin
auto-discovery is used because silently importing arbitrary local files would
weaken the security boundary.

## Command feature template

Create `laptop_guard/features/example.py`:

```python
from .manager import FeatureManager


class ExampleFeature:
    name = "example"

    def __init__(self, host):
        self.host = host

    def register(self, manager: FeatureManager) -> None:
        manager.add_command(self.name, ("/example",), self.handle)
        manager.add_callback(self.name, "example:", self.callback)

    def handle(self, chat_id: int, argument: str) -> None:
        self.host.feature_reply(chat_id, f"Example: {argument}")

    def callback(self, chat_id: int, message_id: int | None, data: str) -> None:
        self.host.feature_reply(chat_id, f"Callback: {data}")

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None
```

Then explicitly install it beside the existing runtime features in the current
`LaptopGuard` initialization path. Feature names, commands, and callback prefixes
must be unique. The manager fails fast on conflicts and starts/stops features in
deterministic order.

Before registration, inspect `laptop_guard/features/manager.py` and an existing
feature with similar lifecycle/side effects. Do not invent a second dispatcher or
auto-loader.

## Host capabilities

Keep feature dependencies narrow. Extend `FeatureHost` with a named capability
only when several features need it; avoid passing the complete guard into
untrusted/dynamic code. Current capabilities cover reply, status, system info,
and help. For larger features, define a feature-specific protocol and inject the
needed service (camera, events, speech, state, or OS action).

## Transport and state

- Code that talks to the owner depends on `RuntimeApi`, not Requests/httpx.
- Runtime construction belongs in `build_runtime_api()`.
- Local mode uses `LocalRuntimeApi` and requires no token/network.
- Live state goes through `GuardRuntimeState`, backed by `RuntimeStateStore`.
- Timestamps persisted across processes use Unix time (`time.time()`), not
  monotonic process-local clocks.

## Configuration and diagnostics

When a feature needs configuration, keep the model/default/migration/setup paths
consistent. Use `docs/CONFIGURATION.md` and the checklist in
`docs/FEATURE_LIFECYCLE.md`.

If the feature depends on a package, binary, device, permission, compositor, or
system service, add an actionable readiness check to `doctor.py` rather than
letting normal startup fail with an unexplained traceback.

## Test checklist

Add tests for registration, aliases, authorization boundary, valid input,
invalid input, timeout/error behavior, and cleanup. Hardware-facing code must
also have a fake backend test and an explicit target-device checklist.

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q laptop_guard tests
bash -n install.sh run.sh doctor.sh repair-opencv.sh
.venv/bin/python -m pip check
git diff --check
```

Use `docs/TESTING.md` for manual device/session checks and `$test-and-verify` when
working through Codex.

## Changing or removing a feature

Do not use this file as a deletion checklist. Feature removal can affect config
migration, commands/callbacks, setup/doctor/help/menu surfaces, persisted state,
events, tests, and shared security guards. Follow the removal sequence in
`docs/FEATURE_LIFECYCLE.md` and have `architect` map dependencies before a
non-trivial removal.
