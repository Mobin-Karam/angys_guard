# Planned managed onboarding protocol

Status: **planned architecture; not an implemented managed service**
Tracking issue: #38
Prerequisite decision: [ADR 0007](adr/0007-passwordless-device-pairing.md)

This document defines the minimum safe onboarding contract for the optional AngysGuard-managed control service. It does not change the current local or self-hosted Bale/Telegram runtime, and it does not make the managed service, official bots, Wake-on-LAN, Windows support, or mobile clients available.

## Trust boundaries

```text
owner account/app or official bot
        | account authentication; no OS password
        v
managed account and command service
        | scoped, signed fixed-action request
        v
enrolled protected-device agent
        | local policy and platform privilege check
        v
fixed local platform action
```

- Bale/Telegram transport is a delivery surface, not an authorization or local privilege boundary.
- The service can authorize only a registered owner/account and a specific enrolled device; the device makes the final action/policy decision.
- No actor may send, request, retain, log, or use the protected device's OS password. Account passwords, where used, authenticate the AngysGuard account only and are stored as modern server-side password hashes.
- The service never offers a shell, script, path, process, packet, or opaque command-line interface. It routes a finite action vocabulary only.
- Self-hosted mode retains its own bot token and local pairing path. It neither uploads that token nor requires a managed account.

## Enrollment protocol

Each transition is explicit, rate-limited, auditable, and fails closed.

| State | Initiator | Required proof | Result / invalidation |
| --- | --- | --- | --- |
| `local_pairing_started` | Local protected-device UI | Local user starts a new session | Device creates a high-entropy pairing secret, displays a short code/QR, and retains only a password-hash or verifier plus expiry. |
| `owner_authenticated` | Owner surface | Account sign-in or approved passwordless account authenticator | Account recovery alone does not enroll, replace, or revoke a device. |
| `pairing_submitted` | Owner surface | Account session plus the current pairing code | Service rate-limits attempts and records no plaintext pairing code. |
| `device_confirmed` | Local device and owner | Session-bound code verifier plus explicit owner/device confirmation | Device creates or receives a device-scoped credential generation and an immutable device identifier. The pairing verifier is immediately invalidated. |
| `enrolled` | Device | Credential generation, audience/device match, and expiry | Device accepts only fixed scoped actions and reports a non-sensitive enrollment status. |
| `revoked` / `expired` | Account recovery, owner revoke, or local recovery | Reauthentication plus action-specific confirmation | Service denies future requests; device rejects the revoked/old generation, clears pending high-risk actions, and offers a local recovery/pairing path. |

Pairing codes must be single-use, expire within a short configured window, carry no account/device secret other than an opaque verifier, and be invalidated on success, expiry, cancellation, local setup reset, or an attempt-limit breach. The device must not silently rebind to another owner after restart, token refresh, account recovery, or a provider chat-ID change.

## Device credential and command protocol

The enrollment result is a device-scoped credential with an immutable device ID, credential generation, account/owner scope, allowed capability set, issue/expiry times, and revocation status. It is not an OS credential and does not imply local administrator privileges.

A managed command must carry all of the following before a device may act:

- target device audience and account/owner scope;
- finite action identifier and bounded parameters from an action schema;
- credential generation, issued/expiry time, nonce/request ID, and idempotency policy;
- authorization context required by ADR 0007, including fresh confirmation for high-risk actions;
- an issuer signature that the device can verify against the enrolled service trust root or rotated key set.

The device verifies freshness, audience, credential generation, replay state, action scope, local capability and local confirmation/policy before any side effect. It records a redacted audit outcome and returns a stable success, denial, expired, unavailable, or uncertain-delivery result. A sender must never retry a destructive request after an uncertain delivery result without an idempotency-safe status query.

### Command confidentiality/integrity options evaluated

| Option | Decision |
| --- | --- |
| Provider payload only | Rejected. Provider authentication/delivery does not prove device scope or prevent service/provider confusion. |
| TLS-only service-to-device request | Rejected as sufficient authorization evidence. TLS protects the transport but does not make a request independently verifiable or replay-safe. |
| Service-signed, device-verifiable fixed-action envelope | Required baseline for the managed protocol. It binds issuer, target, scope, expiry, generation, and request ID. It does not give the service a generic shell. |
| End-to-end owner-to-device encrypted command payload | Evaluate for future owner apps. It can reduce service visibility, but key recovery, multi-device UX, bot constraints, abuse handling, and audit semantics need a separate design before adoption. |

The baseline is integrity-first and does not claim end-to-end encryption exists. All service/device traffic still requires modern authenticated transport encryption; logs and diagnostic data must redact credentials, pairing material, full network identifiers, and private evidence references.

## Minimum managed data and retention policy

This is the required data-minimization policy for a future implementation, not a statement that a managed database exists today.

| Data class | Minimum content | Retention / deletion rule |
| --- | --- | --- |
| Account | Stable account ID, authentication verifier/passkey metadata, recovery state | Retain while account is active; delete/anonymize after verified account deletion subject to legal incident hold. Never store a protected-device OS password. |
| Device enrollment | Device ID, owner/account relation, capability summary, credential generation, status/revocation timestamps | Retain while enrolled plus a bounded security-audit period; revoke and remove active credentials immediately on deletion. |
| Pairing attempt | Hash/verifier reference, session ID, rate-limit counters, expiry, outcome | Delete at success/expiry/cancellation; retain only minimum redacted abuse telemetry for a bounded documented period. |
| Command audit | Action type, target ID, request ID, time, policy result, redacted delivery state | Use a documented configurable retention period; do not retain raw bot content, secrets, OS passwords, captured media, or full network identifiers. |
| Evidence/media | None by default in the onboarding/control service | A separate retention/deletion design and explicit owner consent are required before managed evidence storage. |

The implementation must publish exact configurable durations, deletion/export behavior, incident/legal-hold exceptions, backup deletion behavior, and data residency before public managed-service availability. A provider's own message retention does not substitute for AngysGuard's retention policy.

## Revocation and recovery

- An owner can revoke one device without invalidating other devices or the self-hosted/local path.
- Revocation increments or invalidates the credential generation, terminates service sessions, and causes pending high-risk operations to fail closed.
- Rotation is explicit and recorded; bounded overlap is allowed only for a reauthenticated recovery protocol and never for an already revoked device.
- The only-owner and local-privilege-policy changes require recent account reauthentication, action-specific confirmation, and a documented local recovery path.
- Lost-device/owner recovery must not rely on a chat-ID replacement, unattended bot message, OS password, or support-agent bypass.

## Privacy and implementation gates

Before an implementation PR for #40, #42, #64, #65, #66, or #71 can call the managed flow usable, it needs:

1. threat-model and abuse-case review for its deployment topology;
2. protocol tests for expiry, replay, scope, generation rotation, revocation, recovery, idempotency and account/device takeover denial;
3. an independent security/privacy review of account storage, issuer key lifecycle, local agent verification, rate limiting, redaction and retention;
4. a documented incident response and deletion/export policy;
5. target-device/provider validation for any real bot, network relay, local privilege adapter, or Wake-on-LAN path.

Failure to meet a gate leaves the relevant mode **planned**, not supported.
