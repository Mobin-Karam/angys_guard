# Architecture

```text
Sensors                    Guard core                  Delivery / actions
-------                    ----------                  ------------------
Camera  -----------------> events/rules ------------> Telegram / Bale
Keyboard/mouse -----------> severity                  Offline outbox
USB ----------------------> profiles                  Fullscreen warning
Power/health -------------> local SQLite ------------> Camera snapshot/video
Microphone <-------------- commands                  Audio playback / TTS
```

The laptop remains protected locally when the bot/network is unavailable. Bot delivery is a secondary channel, not a dependency for local event capture.

## Event priorities

- `info`: owner actions and routine state.
- `notice`: power/profile/service changes.
- `warning`: motion, first unexpected input, low resources.
- `high`: person detection, repeated input, new USB while armed.
- `critical`: repeated intrusion/battery critical.
- `tamper`: camera blocked/frozen/disconnected.

## Multi-device direction

The laptop implementation is the reference agent. Raspberry Pi agents can reuse the Python event model. ESP32 nodes should be sensor agents, not run this Linux/Python stack. See `hardware/PROTOCOL.md`.

## v5 desktop communication layer

v5 adds four desktop-facing components:

1. `SecurityChatManager` + `chat_window`: visible fullscreen security conversation, countdown, visitor reply box, and Text Editor transcript mirror.
2. `ScreenCaptureManager`: capability-detected screenshot / bounded snapshot-session / bounded recording backends with local notifications.
3. `AppManager`: `.desktop`-based GUI allowlist and normal process termination; never accepts arbitrary shell commands.
4. `LocalControlAPI`: bearer-authenticated API bound to `127.0.0.1` by default for status, chat, TTS, warning, screen snapshot, voice record and voice playback.

### Input privacy

`InputMonitor` prefers Linux `evdev` in `auto` mode when the current user can read suitable input devices. It converts raw events immediately into one of `keyboard`, `mouse movement`, `mouse click`, or `mouse scroll`. Actual typed key identities are not persisted or forwarded. If evdev is unavailable, the existing `pynput` activity fallback is used.

### Wayland boundary

v5 does not bypass Wayland security boundaries for arbitrary input injection or invisible screen capture. Full interactive remote desktop is intentionally left to permissioned desktop portal / desktop-native remote-desktop facilities. The bot layer provides bounded visibility and safe GUI application actions instead of a remote shell.
