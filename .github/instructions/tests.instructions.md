---
applyTo: "tests/**/*.py"
---

Follow root `AGENTS.md` and `tests/AGENTS.md`.

Keep tests deterministic/offline and free of real credentials, passwords, chat
IDs, or captured private media. Mock/fake hardware, providers, systemd/journal,
and OS lock behavior. For security-sensitive behavior, cover denial/error/timeout
paths as well as success. Prefer temporary directories for config/state and avoid
unnecessary sleeps.
