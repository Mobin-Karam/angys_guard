# Security and privacy

## Trust model

Laptop Guard assumes the Linux user account and its configuration directory are
trusted. Remote commands are accepted only when the incoming chat ID exactly
matches the paired owner ID. The main v11 runtime uses Bale long polling, so it
does not require a public inbound webhook.

Bot tokens live in an owner-readable secrets file. The stop PIN is validated as
4–10 digits and stored only as a salted scrypt digest. Sensitive PIN messages are
deleted from Bale on a best-effort basis after processing.

## Protected termination

Ctrl+C starts this flow:

```text
local hidden PIN (15s)
  -> correct PIN
  -> Bale owner confirmation (10s)
  -> one-time safe-exit token
  -> watchdog permits clean exit
```

Wrong PIN, timeout, or denial requests a desktop lock and leaves the guard
running. SIGHUP, SIGTERM, terminal loss, crash, and SIGKILL do not receive the
interactive exception; the guard or detached watchdog requests a lock.

This mechanism is fail-closed protection against accidental or ordinary local
termination. It is not a privilege boundary against an attacker who already
fully controls the same Unix account, process table, Python environment, or
configuration directory.

## Remote controls

- All Bale handlers check the owner chat before privileged actions.
- Unlock and power actions are separately opt-in and confirmation-gated.
- The local HTTP API is bearer-authenticated and defaults to `127.0.0.1`.
- GUI application control uses a configured `.desktop` allowlist.
- There is no arbitrary remote command or shell execution endpoint.
- Both runtime HTTP paths disable ambient proxy inheritance and use only the
  proxy explicitly saved by the owner.

## Capture and privacy

- Input monitoring records categories of activity, not typed key identities.
- Microphone capture is explicit and can show a local notification.
- Optional sound detection calculates volume from transient PCM only. It does
  not retain idle audio or transcribe speech; after a configured trigger it
  records one bounded clip and sends it to the owner. Detection pauses while an
  owner voice message plays, preventing that playback from being echoed back.
- Camera privacy-light suppression is intentionally unsupported.
- Screen and global-input behavior is capability-dependent under Wayland.
- Media and failed outbound work remain in the user's local data directory.
- Failed-login monitoring extracts only authentication source, username, and
  remote address from readable journal entries; it never handles passwords.
- Deployments must comply with local recording, consent, and monitoring laws.

## Residual risks

1. Bale and Telegram share a Telegram-style runtime adapter; provider-specific
   API differences still require integration tests against each live service.
2. Local API error bodies can contain raw exception text. Keep the API on
   loopback and do not reuse its bearer token elsewhere.
3. Event and media retention has no automatic quota/expiry policy.
4. The exit watchdog can request a lock but cannot prove the desktop session
   manager honored it.
5. Hardware capture and fullscreen focus require target-desktop validation.
6. Failed-login coverage depends on distribution-specific PAM journal messages
   and journal permissions; `doctor` reports whether journal access works.
7. A user service begins with the graphical session. It can observe lock-screen
   and SSH failures while running, but cannot report a wrong password entered at
   the first boot login screen before that service has started. Covering that
   phase requires a separately reviewed privileged system service or PAM hook.

When armed, the first keyboard press, mouse button, wheel event, or pointer
movement queues a Bale notification and starts the bundled five-second video in
VLC. The lock deadline is independent of Bale, camera, screenshot, and VLC
success, so slow networking or closing the player cannot postpone the lock.
