# AngysGuard control modes: local, self-hosted bot, and managed service

This document explains **how an owner can interact with AngysGuard today and how future self-hosted/managed control modes are intended to work**.

The core rule is the same in every mode: **remote identity is not the same thing as local operating-system privilege**. A Bale/Telegram bot, mobile app or managed backend must never become a generic shell and must never require a user's computer password to be sent through a chat service.

## Current owner interfaces

### 1. Guided local menu, CLI and setup — available now

Running `./run.sh` in an interactive terminal opens a simple local menu for Setup,
Start Guard, Arm, Disarm, Status, hardware tests, Doctor, Autostart and Events. It
shows setup, protection and provider state before each choice.

The existing direct CLI remains available for advanced use and scripting:

```bash
./run.sh setup
./run.sh doctor
./run.sh status
./run.sh arm
./run.sh disarm
./run.sh profile away
./run.sh events --limit 20
./run.sh service status
```

Guided setup stores normal configuration and protected secrets in the user's AngysGuard/Laptop Guard configuration area. A tracked project `.env` is not required.

### 2. Bale bot — current bot-style owner UI

Bale is an Iranian messaging service with a Telegram-style bot API model. The current project contains Bale-specific bot support and owner controls.

Typical owner actions include status, arm/disarm, evidence requests, events, chat/audio/TTS, lock/unlock and explicitly enabled confirmation-gated system actions.

### 3. Telegram-style provider — current provider architecture, release validation required

The current provider layer supports Telegram-style HTTP bot behavior and the setup/roadmap treats Telegram as a provider option. Exact media/button/proxy behavior should be validated against the live provider before a release claims complete parity with Bale.

Issue #41 tracks provider-specific capability documentation and validation.

### 4. Local desktop/chat surfaces — available in current runtime where applicable

The runtime also contains visible local chat/notepad and warning/UI processes for the protected Linux desktop. These are not a full management desktop app yet; issue #32 tracks the future Linux app/tray experience.

## Current safety model for bot control

Remote bot commands are **fixed AngysGuard actions**, not shell commands.

Examples:

```text
/status
/arm
/disarm
/photo
/screen
/events
/chat
/say
/lock
/unlock
```

The runtime must verify the authorized owner before privileged behavior. High-risk operations can require extra confirmation or local policy.

AngysGuard deliberately does not translate arbitrary chat messages into Bash, PowerShell, Python, `eval`, `exec` or filesystem-control operations.

---

# Future mode A — self-hosted Bale/Telegram bot

Issue #37 tracks a simpler self-hosted onboarding flow.

The goal is that a user who wants full provider ownership can create their own Bale or Telegram bot and connect it without manually editing configuration files.

## Target self-hosted setup

```text
1. Install AngysGuard on your device
             |
             v
2. Choose Bale or Telegram
             |
             v
3. Create your own bot using that provider's official bot-management flow
             |
             v
4. Enter the bot token locally into AngysGuard setup/app
             |
             v
5. AngysGuard validates the token and generates a short-lived pairing code
             |
             v
6. Open your bot and submit/confirm that pairing code as the owner
             |
             v
7. AngysGuard binds the authorized owner and enables fixed controls
```

### Where the token belongs

The bot token is a secret and should be stored **only on the protected device** in AngysGuard's protected secret store.

Do not:

- commit it to Git;
- paste it into issues/PRs;
- include it in screenshots or logs;
- store it in a tracked `.env`;
- send it through another chat just to configure the app.

### Pairing-code requirements

The planned pairing code should be:

- short-lived;
- single-use;
- rate-limited;
- bound to the intended local device/setup session;
- invalid after successful pairing;
- revocable/recoverable without silently replacing the existing owner.

---

# Future mode B — AngysGuard managed bot/service

Issues #38, #39, #40 and #42 define the optional startup-hosted mode.

This mode is for users who do **not** want to create/maintain their own Bale or Telegram bot.

## Selected official-bot direction

AngysGuard's intended non-technical onboarding is the shared official-bot
model: the user installs an OS agent, opens the official `@angysguardbot` on
their selected provider, and pairs that specific device with a one-time code.
The official bot/server owns its provider credentials; no device client asks a
user to paste a Telegram/Bale bot token.

```text
Install AngysGuard agent -> display one-time pairing code
       -> open official @angysguardbot -> sign in / identify account
       -> submit pairing code -> device becomes a scoped bot target
```

This is the chosen architecture direction, not a statement that the official
service is deployed. The current Linux local/self-hosted provider setup remains
available until the managed path is implemented and validated.

The planned service may provide official AngysGuard Bale/Telegram bots and future Android/Linux/Windows app surfaces.

## Target managed onboarding

```text
Protected device                            AngysGuard owner surface
----------------                            ------------------------
Install AngysGuard                          Open official AngysGuard bot/app
       |                                                |
Generate one-time pairing code                      Sign in
       |                                                |
       +-------------- pairing code ------------------->|
                                                        |
                                             Confirm device pairing
                                                        |
       <--------- device-scoped credential -------------+
       |
Device enrolled with fixed AngysGuard capabilities
```

The managed backend associates an AngysGuard account with an enrolled device using a **device-scoped credential**, not the user's computer password.

### Planned power-on boundary

An off device cannot receive a bot command. Power-on therefore requires an
always-on, owner-authorized Wake-on-LAN gateway and an explicitly enrolled LAN
target; it is not universal remote-power support. AngysGuard never sends the
protected device's OS password through Bale, Telegram or the gateway to bypass
that limitation.

## User account authentication

If AngysGuard offers username/password accounts in the future:

- the account password is only for the AngysGuard account;
- the server stores a modern salted password hash, never plaintext;
- passwordless/passkey authentication should also be evaluated;
- account authentication never supplies operating-system administrator/root credentials to the device.

## Computer/OS password rule — hard boundary

**Do not send the computer's Windows/Linux/macOS password to Bale, Telegram, the managed AngysGuard service, a bot message, or an API request.**

Also do not treat an environment variable as a safe substitute for sending/storing an OS password. Process environments can leak through diagnostics, process inspection, crash reporting or child processes.

The preferred model is:

```text
remote owner authentication
        |
        v
signed/scoped AngysGuard action
        |
        v
local AngysGuard policy check
        |
        v
narrow OS-native privileged mechanism
```

Examples of safer local privilege mechanisms include platform-native services, policy frameworks and narrowly granted capabilities. On Linux this can include an intentionally designed service/polkit boundary; Windows should use Windows-native service/security APIs.

If a future platform truly requires a local reusable secret, it should use the OS credential/keyring facility with explicit lifecycle/revocation rules—not a bot message or general environment variable.

Issue #39 owns this architecture/security requirement.

The planned protocol, data-minimization policy, command-integrity evaluation and
implementation gates are defined in
[Managed onboarding protocol](MANAGED_ONBOARDING_PROTOCOL.md). It is an
architecture contract for future work, not a currently available managed
service.

## Managed service security requirements

Before implementation/release, the managed mode requires:

- a threat model;
- device-scoped revocable/rotatable credentials;
- short-lived one-time pairing codes;
- authentication recovery without account/device takeover shortcuts;
- audit logs for security-sensitive actions;
- rate limiting and abuse controls;
- documented retention/deletion policy;
- server-side secret management;
- clear offline/reconnect behavior;
- ability to revoke one device without invalidating all devices;
- no generic remote command execution;
- external security review before broad availability.

## Multi-device future

Issue #40 targets owners with multiple Linux/Windows devices and future mobile clients.

A future owner experience may look like:

```text
AngysGuard account
├── Home laptop       online · armed
├── Work laptop       online · home profile
├── Windows PC        offline
└── Test machine      online · testing profile
```

Before a sensitive action, the UI/bot must make the target device unambiguous.

## Self-hosted vs managed comparison

| Topic | Self-hosted bot | Managed AngysGuard service |
|---|---|---|
| Bot ownership | User creates/owns Bale/Telegram bot | AngysGuard operates official bot/service |
| Bot token storage | On user's protected device | Managed service owns its own service bot credentials |
| AngysGuard account required | No, unless later chosen | Yes / planned |
| Device pairing | Local token + one-time owner pairing | One-time device code + account/device credential |
| Works without startup backend | Yes | No |
| OS password sent to bot/service | **Never** | **Never** |
| Generic remote shell | **Never** | **Never** |
| Multi-device dashboard | Possible later | Planned (#40) |
| Best for | Technical/privacy-focused users who want provider ownership | Non-technical users who want simpler onboarding/multi-device management |

The project should keep self-hosted mode available even if the managed service is introduced.

## Provider capability parity

Bale and Telegram are similar at a bot-API level but should not be assumed identical. Issue #41 tracks:

- commands/buttons;
- file/media sending;
- polling/webhook behavior;
- proxies/network behavior;
- limits/timeouts;
- provider-specific errors;
- capability detection and user-facing fallbacks.

## Related roadmap

- #37 — self-hosted bot pairing;
- #38 — managed onboarding/trust model;
- #39 — passwordless device authorization/local privilege;
- #40 — multi-device account/dashboard;
- #41 — Bale/Telegram parity;
- #42 — managed backend + official bots;
- #35 — Android companion app.
