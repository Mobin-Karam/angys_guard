---
name: security-review
description: Review Laptop Guard changes for authorization bypasses, secret leakage, command/path injection, unsafe capture, insecure defaults, and remote-control abuse. Use for security-sensitive changes or before releases.
---

# Security review

Review the actual diff and affected call paths. Do not read real secret files or
captured media.

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
impact, realistic trigger, and smallest remediation/test. Separate vulnerabilities
from optional hardening. Explicitly list the boundaries checked when no blocking
finding exists.
