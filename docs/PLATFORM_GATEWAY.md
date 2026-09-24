# Platform gateway boundary

Issue #64's managed gateway is being delivered in security-preserving slices.
This document describes the first implemented server-side boundary; it is **not**
a claim that an official Telegram or Bale gateway service is deployed.

The selected product direction is one shared official bot per provider, not a
separate bot username/token per installed device. The server is therefore the
only location for official provider credentials, and devices receive only
scoped enrollment credentials.

## Implemented routing boundary

`angys_platform.gateway.GatewayRouter` accepts only `telegram` and `bale`
provider identities that have already been linked to an AngysGuard account. It
then authorizes only a fixed command vocabulary for an active device owned by
that account:

```text
provider update -> persisted provider/account link -> active device ownership
                -> fixed routed command
```

The routed value is intentionally inert: it cannot run a shell command, hold a
bot credential, contact a protected device, or invoke an OS power operation.
Those functions need a separately authenticated device-delivery protocol and
local confirmation/policy enforcement. The existing device agent retains the
owner authorization and power-action safeguards.

The gateway also has a pure provider-update adapter. It accepts only an explicit
`/device <device-id> <fixed-action>` message shape, then delegates identity and
ownership enforcement to `GatewayRouter`. HTTP/webhook polling, credentials and
reply delivery remain separate server-adapter work.

An authorized route can be converted into a short-lived signed device envelope.
The device protocol independently validates its account/device scope, credential
generation, signature, expiry and replay state before local policy considers it.

## Not yet shipped

- a deployed official `@angysguardbot` Telegram or Bale service;
- server-side provider credential configuration and webhook/polling adapters;
- account-link pairing proof, unlink/recovery, or audit logs;
- authenticated command delivery, device replies, or notification routing;
- managed Wake-on-LAN power-on (tracked separately in issue #71).

## Wake-on-LAN power-on slice

The gateway recognizes the fixed `wake` action. A `/device <device-id> wake`
request uses the same linked-provider and device-owner authorization as other
fixed actions, but is handled by the always-on gateway rather than queued to an
offline device. Targets are explicit per-device records: owner account, MAC,
IPv4 broadcast address and UDP port. Arbitrary packet destinations, malformed
addresses and revoked targets are rejected.

This is a protocol/code slice, not a production hosting claim. Real use requires
an always-on gateway with LAN access, compatible firmware/NIC configuration and
target-network validation. It never sends or stores the protected device's OS
password and cannot send arbitrary UDP payloads.

Provider credentials must remain server-only when those adapters are added.
They must never be distributed to device clients or committed to this repository.
