# ADR 0008: Cross-platform capability adapters before OS expansion

- Status: Accepted
- Date: 2026-09-12
- Related issues: #31, #32, #33, #34, #35, #36

## Context

The current product is Linux-first and several capabilities depend on Linux-specific service, session, input, lock, notification and capture mechanisms. Windows and Android expose materially different security and lifecycle APIs.

Porting by scattering `if platform == ...` branches through the existing runtime or by calling generic shell/PowerShell commands would increase coupling and weaken reviewability/security.

## Decision

Before first-class Windows/Android expansion, AngysGuard will define **narrow platform capability ports** owned by the application/security layer and implement platform-specific adapters behind them.

Candidate capability families include:

- lock/session and safe system actions;
- service/autostart lifecycle;
- notifications;
- input-activity signals;
- camera/media capture;
- screen capture/recording;
- secure credential storage;
- local privileged action execution;
- platform/session capability detection.

The application/security policy decides *what* action is allowed. The platform adapter decides *how* the supported OS safely performs it.

## Capability-first behavior

Each platform exposes an explicit capability set. If a capability is unavailable or unsafe, AngysGuard reports that limitation instead of silently substituting an insecure implementation.

```text
security/use-case layer
        |
        v
capability protocol
    /      |      \
 Linux   Windows   future
```

## Consequences

### Positive

- Linux remains the reference implementation without becoming the architecture itself;
- Windows adapters can use Windows-native APIs/services;
- Android can expose a reduced companion/protected-device capability set honestly;
- tests can validate common policy separately from platform adapters;
- support matrices can map directly to explicit capabilities;
- generic remote shell execution is not needed for portability.

### Cost

- some existing Linux-specific logic must gradually move behind ports;
- platform adapters require real-device testing;
- feature availability may differ by OS/session;
- documentation and UI must surface capability differences.

## Rejected alternatives

### One runtime full of platform conditionals

Rejected as the long-term target because it spreads platform knowledge into security/application logic and becomes difficult to audit.

### Shell-command abstraction for every platform

Rejected. Shell/PowerShell strings are not a safe universal OS API and would encourage arbitrary execution surfaces.

### Claim identical features on every OS

Rejected. Platform privacy/security APIs differ; unsupported capabilities must remain explicit.

## Required validation before an OS is supported

- Graphify/source map of current Linux-specific boundaries;
- initial capability matrix for Linux/Windows/Android;
- migration plan compatible with existing architecture ADRs;
- target-device testing strategy;
- security review of privileged action and credential adapters.
