# Configuration

## Storage

Laptop Guard creates these user-scoped paths:

| Path | Purpose | Expected permissions |
|---|---|---|
| `~/.config/laptop-guard/config.toml` | Non-secret settings | `0600` |
| `~/.config/laptop-guard/secrets.json` | Provider-scoped bot tokens and local API token | `0600` |
| `~/.config/laptop-guard/stop-pin.json` | Salt and scrypt PIN digest | `0600` |
| `~/.local/share/laptop-guard/state.json` | Runtime state | User-only directory |
| `~/.local/share/laptop-guard/events.jsonl` | Current guard event log | User-only directory |
| `~/.local/share/laptop-guard/events.sqlite3` | CLI events and offline outbox | User-only directory |
| `~/.local/share/laptop-guard/media/` | Captured/generated media | User-only directory |

The token and PIN plaintext are not written to `config.toml`. `config.py` uses
atomic temporary-file replacement for configuration and secret updates.

Remote provider credentials are stored independently in `secrets.json`:

- `telegram_bot_token` — used only when Telegram is selected;
- `bale_bot_token` — used only when Bale is selected;
- `api_token` — the unrelated localhost control-API credential.

Changing or repairing one provider credential does not overwrite the other.
Older releases used a shared `bot_token`. A completed pre-upgrade setup can
migrate that token to its already-validated provider. If setup is incomplete or
the provider association is ambiguous, the old value is quarantined as
`legacy_bot_token` and is **not** automatically tried against Bale or Telegram;
enter the selected provider's token once to create its scoped credential.

## Initial setup

```bash
./run.sh setup
```

The wizard selects provider/profile/device/camera/audio settings, reads the bot
token without echoing it, validates the token with `getMe`, and pairs the owner
by waiting for a new `/start` update or accepting an explicit numeric chat ID.

Provider validation distinguishes a credential rejection from a network/proxy/TLS
or API-base failure. Validation reads only the credential for the selected
provider; a saved Bale token is never offered to Telegram and a saved Telegram
token is never offered to Bale. A stored credential is replaced only after that
provider actually rejects it. If the provider cannot be reached, setup keeps the
provider-scoped credential unchanged, pauses the Provider section, and lets you
fix the proxy/API base/network before resuming. A newly entered token is not
stored until it can be validated, but a transport failure is not reported as
proof that the token is bad.

Normal interactive startup validates stored credentials again. Missing or
unauthorized credentials can be repaired interactively. A systemd service
cannot safely answer prompts, so complete setup first:

```bash
./run.sh setup
./run.sh doctor
./run.sh service install
```

## Configuration sections

`AppConfig` contains `bot`, `camera`, `audio`, `security`, `communication`,
`chat`, `tts`, `screen`, `apps`, `api`, `health`, and `monitors` sections.
Important security defaults are:

| Setting | Default | Meaning |
|---|---:|---|
| `warning_seconds` | `5` | Intrusion warning duration |
| `mouse_move_threshold` | `12` | Distance for later pynput events; the first movement always triggers |
| `lock_after_countdown` | `true` | Lock after warning flow |
| `warning_video` | `true` | Use bundled MP4 when a player exists |
| `lock_on_guard_exit` | `true` | Watchdog requests lock after unsafe exit |
| `stop_auth_enabled` | `true` | Protect Ctrl+C with two factors |
| `stop_pin_timeout` | `15` | Local PIN window in seconds |
| `stop_owner_confirm_timeout` | `10` | Bale confirmation window |
| `allow_remote_unlock` | `false` | Remote unlock is opt-in |
| `allow_remote_power` | `false` | Suspend/reboot/shutdown are opt-in; each owner request needs a fresh, single-use confirmation that expires after 30 seconds. A powered-off device cannot turn itself back on; that needs separately configured hardware/network wake support. |
| `startup.enabled` | `false` | Start after graphical login |
| `security.auto_arm` | `false` | Arm immediately when the service starts |
| `monitors.failed_login_events` | `true` | Alert on readable Linux authentication failures |
| `chat.direction` | `auto` | Direction from first strong character |
| `chat.seconds` | `120` | Default local security-chat session duration |
| `audio.play_remote_voice` | `true` | Play authorized owner voice without starting microphone recording |
| `audio.sound_detection_enabled` | `false` | While armed, detect volume and send a bounded recording |
| `audio.sound_threshold` | `0.08` | Normalized RMS trigger threshold from 0 to 1 |
| `audio.sound_trigger_chunks` | `2` | Consecutive loud 100 ms chunks required |
| `audio.sound_record_seconds` | `8` | Length of a sound-triggered clip |
| `audio.sound_cooldown` | `30` | Minimum seconds between sound clips |

Legacy environment variables are read only when no saved TOML exists. This is
a compatibility migration path, not the preferred configuration mechanism.
Old warning/text-editor values are normalized by `config._migrate()`.

## Maintenance

Autostart can be changed independently of automatic arming:

```bash
./run.sh autostart on
./run.sh autostart off
./run.sh autostart status
```

This is intentionally a systemd user service that starts with the graphical
session; the capture, notification, input, and lock backends need that session.

Run `./run.sh setup` to review persisted settings. Do not delete the user config
directory unless intentionally resetting credentials and pairing. Never commit
`.env`, `secrets.json`, `stop-pin.json`, captured media, or live event data.
