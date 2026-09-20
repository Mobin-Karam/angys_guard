# ADR 0007: Passwordless remote device pairing and local privilege separation

- Status: Accepted
- Date: 2026-09-12
- Related issues: #37, #38, #39, #40, #42

## Context

Future AngysGuard control modes include self-hosted Bale/Telegram bots, an optional managed AngysGuard bot/service, and mobile/desktop owner apps.

A tempting onboarding design is to ask the user for the protected computer's operating-system password and keep it in the bot/backend/environment so remote actions can elevate privileges. That creates an unacceptable trust expansion: chat/provider/backend compromise could expose a reusable OS credential, environment variables are not a secure credential store, and the design would conflate remote account authentication with local OS privilege.

## Decision

AngysGuard remote pairing and privileged actions will use **passwordless remote device authorization with local privilege separation**.

1. The remote owner authenticates to a self-hosted bot identity or AngysGuard account.
2. Device enrollment uses a short-lived, single-use pairing code/QR.
3. Successful enrollment establishes a revocable, rotatable, device-scoped credential.
4. Remote messages request only predefined AngysGuard actions.
5. The local device verifies owner/device authorization and action policy.
6. Privileged work is performed through a narrow platform-native local mechanism.
7. The protected device's OS password is never transmitted through Bale/Telegram, sent to the managed backend, or stored as an environment variable for normal operation.

If a reusable local secret is unavoidable on a future platform, it must use that platform's credential/keyring facility with explicit lifecycle and revocation rules.

## Credential model and lifecycle

The following credential classes have separate purposes and must not be
interchangeable:

| Credential | Scope and storage | Lifetime / recovery |
| --- | --- | --- |
| Owner account credential | Managed-service account only; server-side password hash or passkey verifier | Account recovery must re-authenticate the owner and must not silently enroll a device. It never authorizes local OS privilege by itself. |
| One-time pairing code | Bound to one local enrollment session and intended owner; never logged | Short-lived, single-use, rate-limited, and invalidated on success, expiry, cancellation, or local setup reset. |
| Device credential | One enrolled device, one account/owner relationship, explicit action/capability scope | Rotatable and individually revocable. The device must reject it after expiry/revocation and surface a local recovery/pairing path. |
| Action authorization | A signed, short-lived request for one fixed action and target device | Single use for destructive actions; includes audience, action, expiry, credential generation, and nonce/request identifier. |
| Local platform grant | Narrow, platform-native permission held only on the protected device | Installed/revoked locally. It is never exported to a provider, mobile app, bot, or managed service. |

Credential rotation creates a new generation and invalidates the old one after a
bounded overlap only when an authenticated recovery flow requires it. Revocation
is device-specific: it must terminate that device's sessions and pending action
requests without disabling unrelated devices or the self-hosted/local mode.

Lost-owner recovery requires an explicit local recovery ceremony or a
pre-established account recovery process with reauthentication. It must not use
an unattended bot message, a replacement chat ID, or knowledge of an OS password
as proof of ownership.

## Local privilege model

Remote authorization grants permission to request a fixed AngysGuard action; it
does not grant administrator/root access. The local client remains the policy
enforcement point and invokes only a narrowly defined platform adapter.

| Platform state | Local privilege rule |
| --- | --- |
| Linux current runtime | Existing actions stay within the unprivileged user/session where possible. A future privileged action must use a reviewed, fixed-action system service or polkit policy with explicit action identifiers and no argument pass-through. |
| Windows planned | A future native client must use a Windows-native service/API permission boundary with fixed operations and explicit service ACLs. It must not call arbitrary PowerShell or reuse Linux command strings. |
| Android/iOS planned or research | Companion clients authorize remote requests but do not receive desktop OS privileges. Any protected-device capability requires a separately reviewed platform-native design. |

The local adapter validates its input against a finite action vocabulary and
returns an actionable capability/policy failure when the platform grant is
missing. It never accepts a shell command, path, script, or opaque command-line
fragment from a remote surface.

## High-risk action policy

The device must evaluate owner authorization, device scope, action scope,
credential generation, freshness, replay protection, and local policy **before**
the side effect. A provider/backend may route a request but cannot bypass that
decision.

| Action class | Minimum extra protection |
| --- | --- |
| Read-only status/events | Paired owner and device/action scope. |
| Capture or local-user-impacting actions | Paired owner, explicit capability, local privacy/policy gate, bounded payload/duration. |
| Lock, unlock, arm/disarm, configuration/profile change | Paired owner, action-specific confirmation where policy requires it, audit event. |
| Suspend, restart, shutdown, Wake-on-LAN | Explicit opt-in, fresh action-bound single-use confirmation, short expiry, audit event. Wake-on-LAN also requires an authorized always-on relay and strictly configured target. |
| Credential rotation, revoke, enroll/recover device, local privilege-policy change | Recent owner reauthentication plus action-specific confirmation; local presence/recovery policy when it affects the only owner or local privilege grant. |

All denied, expired, replayed, or scope-mismatched high-risk requests fail closed
and must not be retried as an uncertain side effect. Audit records identify the
action, device, credential generation and result without recording secret
material, pairing codes, OS passwords, or full network identifiers.

## Consequences

### Positive

- backend/provider compromise does not directly reveal an OS login password;
- individual device credentials can be revoked/rotated;
- self-hosted and managed modes share one security model;
- local privilege policy can differ correctly between Linux, Windows and future platforms;
- remote commands remain narrow and auditable.

### Cost

- each platform needs an explicit local privilege/action adapter;
- pairing/revocation/recovery protocols require additional design and tests;
- some privileged actions may require initial local setup/consent;
- the managed service cannot use a simplistic password-forwarding implementation.

## Rejected alternatives

### Store the OS password in the managed service

Rejected. It turns the service into a high-value credential vault and makes server/provider compromise much more damaging.

### Send the OS password through the bot only when needed

Rejected. Chat/provider transport, logs, message history and account compromise become credential exposure paths.

### Store the OS password in an environment variable

Rejected as a normal credential-storage design. Environment values can leak through diagnostics, child processes, crash tools and process inspection.

### Add a generic remote shell and let the user run privilege commands

Rejected. It violates the project's fixed-action remote-control boundary and dramatically expands abuse impact.

## Validation and implementation constraints

This decision is accepted as the architecture/security contract. It does not
implement managed control, Windows support, or a privileged service. Before a
mode or platform can claim support, its implementation must provide:

- a concrete threat model for the applicable self-hosted or managed deployment;
- protocol tests for issuance, expiry, replay rejection, rotation, revocation,
  recovery, action scope and device scope;
- a security review of the local platform adapter and its installation/removal
  lifecycle;
- Linux target-device validation for any polkit/system-service action;
- Windows target-device validation before Windows is described as supported;
- provider/live-service validation without putting credentials or OS passwords in
  test fixtures, logs, issues, or pull requests.
