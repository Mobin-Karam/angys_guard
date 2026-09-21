# Platform gateway boundary

Issue #64's managed gateway is being delivered in security-preserving slices.
This document describes the first implemented server-side boundary; it is **not**
a claim that an official Telegram or Bale gateway service is deployed.

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

## Not yet shipped

- a deployed official `@angysguardbot` Telegram or Bale service;
- server-side provider credential configuration and webhook/polling adapters;
- account-link pairing proof, unlink/recovery, or audit logs;
- authenticated command delivery, device replies, or notification routing;
- managed Wake-on-LAN power-on (tracked separately in issue #71).

Provider credentials must remain server-only when those adapters are added.
They must never be distributed to device clients or committed to this repository.
