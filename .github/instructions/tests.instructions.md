---
applyTo: "tests/**/*.py"
---

Follow `AGENTS.md`, `tests/AGENTS.md`, and `docs/GRAPHIFY_NAVIGATION.md`.
Use Graphify first to locate tests connected to the changed/failing production
symbol or behavior instead of scanning the entire test suite. Then inspect/run
the smallest relevant tests before broader verification.

Keep tests deterministic, offline, secret-free, and based on fakes/mocks for
provider/hardware/OS boundaries. Cover denial/error paths for security-sensitive
behavior and use temporary config/state locations.
