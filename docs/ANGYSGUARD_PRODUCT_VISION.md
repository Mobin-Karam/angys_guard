# AngysGuard product vision

**AngysGuard** is the planned public product identity for this project. The name expands to **Angel of System Guard**: a security assistant that watches the owner's device, records bounded evidence when policy requires it, warns/responds locally, and lets the authorized owner review and control a small set of safe actions.

The current repository/package/CLI still use compatibility identifiers such as `laptop_guard_v3`, `laptop_guard`, and `laptop-guard`. Issue #30 tracks a compatibility-safe naming migration rather than a sudden breaking rename.

## Product promise

AngysGuard should make personal-device security understandable to a non-technical owner without turning the device into a remotely operated shell.

The long-term product should combine:

- a local security agent on protected devices;
- guided desktop/mobile apps;
- optional Bale and Telegram owner interfaces;
- a fully self-hosted bot mode;
- an optional managed AngysGuard service for simpler pairing and multi-device use;
- bounded evidence/event history;
- explicit, narrow, auditable device actions;
- platform-native security integration on Linux, Windows, Android companion surfaces and future requested platforms.

## Current product baseline

Today the project is **Linux-first**. The current release baseline includes the Python agent, guided setup/doctor/CLI, Linux service/autostart support, camera/input/screen/audio/security features, event history, Bale/Telegram-style bot/provider integration, local chat/UI surfaces and constrained owner controls.

See:

- `README.md` for the user-facing overview;
- `docs/PLATFORM_SUPPORT.md` for current/planned OS support;
- `docs/CONTROL_MODES.md` for local/self-hosted/managed control modes;
- `docs/ROADMAP.md` for milestone sequencing.

## Product principles

### 1. Owner-controlled by default

Only the authorized owner/device account should be able to trigger privileged actions. Pairing, revocation, confirmation and recovery must be explicit.

### 2. No generic remote shell

AngysGuard provides a defined set of security/device actions. It does not turn Bale, Telegram, the managed service or the mobile app into arbitrary Bash/PowerShell/command execution.

### 3. OS passwords remain local

A computer's operating-system password must never be requested through Bale/Telegram, transmitted to the AngysGuard managed backend, stored in bot messages, or treated as a normal environment variable.

Remote authentication should authorize an AngysGuard action; local platform-native policy should decide whether/how that action can run.

### 4. Self-hosted remains a first-class mode

Users who prefer control/privacy should be able to create their own Bale/Telegram bot, keep the bot token on their own device and pair their owner account without depending on the AngysGuard managed service.

### 5. Managed mode is optional

The future startup-operated service should make onboarding easier, especially for non-technical and multi-device users, but it should not become mandatory for the core security agent.

### 6. Platform differences are explicit

Linux, Windows and Android do not expose the same lock/capture/input/service APIs. AngysGuard should report capability differences honestly rather than emulate missing behavior unsafely.

### 7. Users can influence platform targets

Users may request any OS, Linux distribution, desktop environment, mobile platform or device class. Requests inform prioritization but do not automatically become support promises.

## Target experiences

### A. Linux today

```text
Install -> guided setup -> doctor -> run/service
                      |
                      +-> local CLI/UI
                      +-> user's Bale bot
                      +-> user's Telegram bot/provider
```

Linux remains the reference platform while the cross-platform capability boundary is designed.

### B. Self-hosted bot future

```text
Create your own Bale/Telegram bot
        |
enter token locally in AngysGuard
        |
receive one-time device pairing code
        |
confirm code in your own bot
        |
authorized fixed device controls
```

No AngysGuard startup backend is required for this mode.

### C. Managed AngysGuard future

```text
Install AngysGuard
      |
app shows one-time pairing code / QR
      |
open official AngysGuard bot or app
      |
sign in to AngysGuard account
      |
confirm device code
      |
receive revocable device-scoped access
```

The managed service stores account/device data required for the service, but must never request or retain the protected computer's OS password.

### D. Linux desktop app

A friendly local desktop/tray UI should make setup, doctor, provider pairing, status, events, evidence and service controls usable without terminal commands. Tracked by #32.

### E. Windows desktop agent/app

Windows should become a real native target, not a Linux port wrapped in shell commands. Platform abstraction is tracked by #33 and the Windows product target by #34.

### F. Android companion app

Android should first become a secure companion/controller for enrolled Linux/Windows devices: device list, alerts, events, evidence, pairing, arm/disarm and confirmation-gated actions. Tracked by #35.

A protected-device Android agent is separate research (#36) because Android security/platform rules differ substantially from desktop OSes.

## Roadmap horizons

### Horizon 1 — current release hardening

v11.2 -> v11.3 -> v12.0 remains the immediate priority: safe installation, diagnostics, non-technical UX and production readiness.

### Horizon 2 — AngysGuard self-hosted UX and Linux app

Targets include:

- public AngysGuard identity/migration plan (#30);
- platform support/request system (#31);
- Linux desktop app (#32);
- self-hosted Bale/Telegram pairing (#37);
- provider parity/capability guidance (#41).

### Horizon 3 — optional managed AngysGuard control

Targets include:

- managed account/device pairing architecture (#38);
- passwordless device authorization/local privilege model (#39);
- multi-device dashboard (#40);
- managed backend + official Bale/Telegram bots (#42).

### Horizon 4 — cross-platform expansion

Targets include:

- platform capability adapters (#33);
- Windows agent/app (#34);
- Android companion app (#35);
- Android protected-device feasibility (#36);
- future OS targets promoted from user requests when justified.

## What AngysGuard should not become

The project should not evolve into:

- spyware or covert surveillance;
- credential/password collection infrastructure;
- a remote administration shell hidden behind bot commands;
- an unrestricted file/process execution service;
- a platform-support marketing list that is not validated;
- a cloud-only product that removes the self-hosted option;
- a backend that can silently take over a user's device after one server compromise.

## Product success criteria

Long-term success means a user can:

1. install the app on a supported device;
2. understand the device's available security capabilities;
3. choose local-only, self-hosted bot or optional managed control;
4. pair an owner securely without editing source/config files;
5. see security state and events clearly;
6. use safe fixed controls from Linux/Windows/Android/Bale/Telegram surfaces;
7. revoke/recover access without reinstalling the OS;
8. trust that their OS password and private credentials are not being sent to a bot/startup backend;
9. request another platform and see its status transparently.
