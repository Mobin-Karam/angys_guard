---
name: security-review
description: Review Laptop Guard changes for authorization bypasses, secret leakage, command/path injection, unsafe capture, insecure defaults, and remote-control abuse. Use for security-sensitive changes or before releases.
---

# Security review

Follow `AGENTS.md`, `docs/SECURITY.md`, and `docs/GRAPHIFY_NAVIGATION.md`.
Do not read real secret files or captured media.

Before broad source review, check Graphify freshness and trace the changed symbol
or entry point to relevant trust boundaries with `graphify query`, `explain`, and
`path`. Map authorization, provider/network, secret/config, state/storage,
capture/evidence, subprocess/OS, local API, and stop/unlock relationships. Confirm
important/inferred graph edges in current source/tests before declaring a finding.

Check these trust boundaries:

1. **Identity and authorization** — owner pairing, chat/user identity, callbacks,
   stop/unlock confirmation, replay/confusion behavior.
2. **Remote control** — reject arbitrary shell/exec/eval, generic filesystem
   actions, unsafe app launching, and ambiguous commands.
3. **Secrets/config** — permissions, atomic writes, migration, logs/errors/tests,
   token redaction, default values.
4. **Capture/privacy** — camera/microphone/screen/input collection is explicit,
   bounded, locally visible where required, and sent only to an authorized owner.
5. **Network/API** — authenticated control, loopback defaults, proxy/provider
   validation, bounded requests and media.
6. **OS/process** — argument-list subprocesses, no variable shell interpolation,
   safe lock/service/autostart handling, cleanup on error.
7. **Resource abuse** — bounds on recordings, queues, retries, file sizes, loops,
   and concurrency.

Return findings sorted by severity. For each finding give a concrete path/symbol,
the relevant graph/trust-boundary path, impact, realistic trigger, and smallest
remediation/test. Separate confirmed vulnerabilities from inferred relationships
or optional hardening. Report Graphify freshness/fallback status.
