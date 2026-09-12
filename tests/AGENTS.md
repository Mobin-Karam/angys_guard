# Test instructions

These rules apply under `tests/` in addition to the root `AGENTS.md`.

## Find tests with Graphify first

Before scanning the test tree broadly, follow `docs/GRAPHIFY_NAVIGATION.md` and
query the graph for tests connected to the changed/failing symbol or behavior:

```bash
graphify query "what tests cover <symbol or behavior>?"
graphify path "<production symbol>" "<test symbol>"
graphify explain "<test or production symbol>"
```

Use the returned tests as the first focused test set, then inspect nearby tests or
search directly only when Graphify is stale/unavailable/insufficient. Current test
source remains authoritative.

## Test rules

- Keep tests deterministic, offline, and free of real credentials.
- Mock/fake Telegram, Bale, camera, microphone, screen, input, systemd, journal,
  and OS-lock integrations unless a test is explicitly a target-device test.
- Never require a real password, bot token, chat ID, captured image/video, or
  private user data in fixtures.
- Prefer focused regression tests next to the behavior being changed.
- Test authorization denial and unavailable/error paths for security-sensitive
  behavior, not only success paths.
- Avoid sleeps when state/time can be injected or monkeypatched.
- Keep temporary config/state under pytest temporary directories.
- Verify secret-free serialization and restrictive permissions where applicable.

Standard suite:

```bash
.venv/bin/python -m pytest -q
```

When debugging, use Graphify to locate the smallest relevant test/production
neighborhood, run the smallest failing node/file first, then rerun the applicable
broader/full suite before completion.
