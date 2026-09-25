# Platform client protocol boundary

Issue #65 is delivered incrementally. The implemented protocol primitive accepts
only signed, device-scoped fixed actions and persists consumed request IDs in a
local SQLite cache so a device restart cannot replay a command.

It verifies device/account scope, credential generation, expiry, signature and
the fixed action vocabulary before returning a command to local policy. It does
not execute the command, grant OS privilege, connect to Telegram/Bale, or make
Linux/Windows/Android/iOS clients available.

Remaining work includes credential issuance/rotation/revocation, a real
asymmetric issuer-key lifecycle, local credential-store integration, network
transport, device status/event syncing, offline delivery results and target
device validation.
