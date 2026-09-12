# v6 feature matrix

| Area | v6 behavior |
|---|---|
| Keyboard/mouse intrusion | Visible photo warning + 5-second status sequence + desktop lock |
| Countdown cancellation | Owner grace/disarm cancels pending lock |
| Local chat | Guard Chat bubbles + built-in Live Notepad |
| External text editor | Mirror file retained, no automatic opening/reload prompts |
| Camera evidence | Snapshot + optional event video |
| Screen screenshot | GNOME D-Bus first, then native desktop fallbacks |
| Screen video | GNOME Shell Screencast first, then Wayland/X11 fallbacks |
| Offline alerts | SQLite outbox retry |
| Voice | Owner voice playback + environment recording |
| Input privacy | Activity only; key identities discarded |
| App control | `.desktop` allowlist only, no remote shell |
| Privacy LED | Never deliberately suppressed during active capture |
