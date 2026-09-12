# ADR 0007: Passwordless remote device pairing and local privilege separation

- Status: Proposed
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

## Required validation before acceptance

- threat model for self-hosted and managed modes;
- credential issuance/rotation/revocation/recovery design;
- Linux local privilege model;
- Windows local privilege model before Windows support;
- audit/confirmation policy for high-risk actions;
- security reviewer approval.
