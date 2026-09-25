# Managed pilot privacy, retention, and incident response

This policy applies only to the small managed control-plane pilot deployed at
`api.mahakaram.ir`. It does not change Laptop Guard's local-only or self-hosted
operation, and it is not a public managed-service privacy notice.

## Data the pilot handles

| Data | Purpose | Storage and deletion |
|---|---|---|
| Account email and password verifier | Sign-in | Retained while the pilot account is active; an operator removes the account on a verified owner deletion request. |
| Device ID, owner account ID, display name and credential digest | Pairing, revocation and scoped command delivery | Retained while the device is active; revocation stops future polling immediately. |
| One-time device/bot pairing-code digest | Pairing | 80-bit code digest only; deleted after expiry by the next authenticated service request and unavailable after first use. |
| Provider name and chat ID | Deliver bot responses only to the linked owner chat | Removed with the account or by operator recovery after verified ownership. |
| Fixed command audit | Diagnose the pilot and show `/events` | Action, device ID, timestamps and a local completion value are kept at most 30 days by default. Completed results are deleted by the next authenticated service request after the retention cutoff. Bot output exposes only redacted state labels. |

The control plane never stores protected-device OS passwords, camera/microphone
media, screenshots, typed keys, raw bot content, or a generic remote shell
history. Provider operators may retain messages under their own policies;
that processing is outside this pilot database.

`ANGYSGUARD_COMMAND_AUDIT_RETENTION_SECONDS` can set the command-audit window
between one and ninety days. A pilot operator must choose the shortest window
that supports incident diagnosis. Backups can retain records until their normal
encrypted backup rotation; do not create unmanaged copies of the SQLite file.

## Incident and recovery procedure

1. **Suspected bot-token, webhook-secret, or server-secret exposure:** disable
   the affected webhook, rotate the provider token/secret and
   `ANGYSGUARD_SERVER_SECRET` in the provider secret manager, redeploy, and
   verify `/healthz` and `/readyz`. Do not paste the old or new secret into
   chat, issues, logs, or the repository.
2. **Suspected device compromise or lost device:** revoke the device from the
   owner account or linked bot, then remove the local credential/keyring entry
   from the protected device. Re-enroll only after the owner reauthenticates.
3. **Unexpected command/audit record:** preserve the minimum redacted command
   metadata needed for review, revoke the affected device/chat, and inspect
   provider/web-server access logs without copying tokens or message content.
4. **Database loss/corruption:** stop enrolment, restore the most recent
   encrypted persistent-volume backup, run readiness checks, and require
   re-pairing if an integrity or credential-generation doubt remains. Never
   silently attach a device to a different account after recovery.
5. **Service outage:** keep the local Laptop Guard service running; remote
   controls should report unavailable/expired rather than retrying a completed
   action. Restore the control plane and confirm health/readiness before
   enabling webhooks again.

Any incident affecting a pilot account should be disclosed to that test user
with the scope, action taken, whether re-pairing is required, and a support
contact. Escalate to a proper legal/privacy process before a public managed
service release.
