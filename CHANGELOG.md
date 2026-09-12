# Changelog

## 9.0.0

- Added `py-persian-tts==3.0.2` integration using the documented async `PersianTTS.speak_async` API.
- Added `/say`, `/speak`, `/tts`, `/ttsvoice`, `/ttsvoices`, `/ttsmode`, and `/ttstest`.
- Added Bale Audio menu flows for one-shot TTS, direct-speech mode, TTS test, and all documented voice choices.
- Added serialized TTS playback queue to avoid overlapping generated speech.
- Persist selected TTS voice locally across restarts.
- Added lazy TTS imports so a TTS package problem does not stop Laptop Guard security features.
- Added TTS configuration and doctor checks for package/playback backend availability.
- Added TTS regression tests.

## 8.0.0

- Added automatic RTL/LTR rendering and manual AUTO/RTL/LTR composer controls.
- Redesigned Guard Chat with bilingual header, responsive bubbles, multiline composer and quick replies.
- Plain owner text is forwarded directly while local Guard Chat is active.
- Added optional confirmed Linux remote unlock; Windows secure logon remains non-bypassable.
- Added System menu, system information, local notification and Power menu.
- Added confirmation-gated suspend/restart/shutdown controls.
- Added process exit-lock watchdog for terminal closure, SIGINT/SIGTERM/SIGHUP, crash and abrupt process death.
- Made Tkinter optional for the core bot so missing `python3-tk` no longer crashes startup.
- Added notification fallback for warning countdown when Tkinter is unavailable.
- Added system status through `psutil`.
- Added regression tests for text direction, exit watchdog and v8 security defaults.

## 7.0.0

- Added native Bale Bot API transport.
- Added five-image intrusion warning sequence.
- Added camera/screen evidence, voice intercom and security chat.
