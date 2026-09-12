# Release and migration history

## 11.1

- Replaced project `.env` requirements with `config.toml` and mode-0600
  `secrets.json` under `~/.config/laptop-guard/`.
- Added resumable guided setup, token validation/repair, and owner pairing.
- Reconciled the configuration model with the direct Bale guard runtime.
- Added explicit packaged warning media and a test dependency extra.

Upgrade with `./install.sh`, `./run.sh setup`, and `./run.sh doctor` before
installing the user service.

## 11

- Added protected Ctrl+C: local scrypt-backed PIN plus timed Bale confirmation.
- Added one-time safe-exit authorization for the detached exit watchdog.
- Replaced the image sequence with a fixed five-second 1920×1080 MP4 warning.
- Wrong/expired stop authorization locks the session while the guard continues.

## 9

- Added `py-persian-tts` through its asynchronous `PersianTTS` API.
- Added speech commands, selectable persisted voices, bounded serialized jobs,
  lazy imports, and local playback detection.

## 8

- Added automatic RTL/LTR chat rendering and richer fullscreen chat.
- Added opt-in confirmed unlock, confirmed power controls, system information,
  desktop notifications, and the process exit-lock watchdog.
- Made Tkinter optional for the core bot.

## 7

- Added native Bale transport, intrusion warning media, camera/screen evidence,
  voice intercom, and security chat.

## 6

- Migrated `text_editor` to built-in `live_notepad` and disabled automatic
  external-editor launching.
- Migrated old 20-second warning behavior to visible five-second warning+lock.
- Preserved lower-noise Home and notify-only Testing profiles.

## 5

- Added communication, screen, app-control, and local API sections.
- Added allowlisted GUI controls, bounded screen capture, offline delivery, and
  privacy-preserving input activity classification.

## 4

- Added profiles, tamper/pre-event concepts, offline queue, USB, and health
  monitoring. Persisted configuration remained outside the source directory.

## 3.2–3.3

- Pinned OpenCV 4.x compatibility because classic HOG person detection is not
  guaranteed in OpenCV 5; runtime now safely falls back to motion-only mode.
- Added Persian warning UI, owner audio playback, dashboard controls, camera
  toggles, capture indicators, and input evidence.

Historical standalone upgrade guides and version feature matrices were removed
after their still-relevant information was consolidated here and in the current
system audit.
