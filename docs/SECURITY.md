# Security and privacy design

- Only the paired owner chat is accepted.
- Bot token is stored separately in an owner-readable `0600` secrets file.
- HTTP clients ignore ambient proxy variables and use only the configured proxy.
- Unexpected local input defaults to a visible warning + owner notification, not forced lock.
- Remote unlock remains optional and disabled unless explicitly configured.
- Audio capture starts only through owner action and can issue a local desktop notification.
- Voice/audio playback accepts media only from the paired owner chat.
- Camera indicator suppression while the camera is active is intentionally unsupported.
- Offline alerts/media remain local until delivery succeeds.
- Keyboard monitoring observes activity only; this project does not store keystroke contents.

For deployment beyond your own device, account for local consent/recording laws.
