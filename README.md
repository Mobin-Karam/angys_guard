# Laptop Guard v9 — Bale Control + Persian Text-to-Speech

Laptop Guard v9 keeps the current single-device Bale workflow and adds queued Persian text-to-speech from Bale to the laptop speakers, while retaining the bilingual chat, warning countdown, owner controls, and exit-lock protection.

## v9 highlights

- Bale Bot API remains the primary control channel.

- **Persian text-to-speech via `py-persian-tts==3.0.2`**: send `/say متن` from Bale and the generated WAV is played on the laptop speakers.
- Audio > **متن → صدا** creates a one-shot prompt where the next normal Bale text is spoken.
- Optional **direct speech mode** (`/ttsmode on`) makes every ordinary Bale text message play as Persian speech until turned off.
- Voice selection from Bale for all documented voices: `woman1..woman4`, `man1..man8`, `boy1`.
- The selected TTS voice is persisted locally across Guard restarts.
- TTS jobs are serialized in a bounded queue so rapid messages do not overlap on the laptop speakers.
- `py_persian_tts.PersianTTS` is loaded lazily; a TTS dependency failure does not prevent the security guard from starting.
- Guard Chat now supports **RTL + LTR automatically per message**:
  - Persian / Arabic / Hebrew → RTL
  - English / Latin text → LTR
  - mixed text follows the first strong directional character
  - local user can switch composer mode between `AUTO`, `RTL`, and `LTR`
- Better fullscreen chat UI with responsive bubbles, multiline composer, quick replies, countdown, message direction badge, and bilingual labels.
- While Guard Chat is open, ordinary Bale text is forwarded directly to the laptop; `/chat` is only needed to open/start the session.
- Owner Bale voice/audio messages can play on the laptop speakers; visible near-live microphone intercom remains available.
- Owner-only **Lock** from Bale.
- Optional owner-only **Unlock** on supported Linux sessions with a second confirmation step.
- System information from Bale: CPU, memory, battery, disk, uptime, OS, architecture.
- Visible local notifications from Bale using `/notify`.
- Confirmed remote power controls: Suspend, Restart, Shutdown.
- Five bundled 16:9 warning images still run as `5.png → 1.png` before automatic lock.
- `tkinter` is now optional for the core bot: missing `python3-tk` no longer crashes Laptop Guard. Fullscreen chat/warning UI falls back where possible.
- **Exit Lock Watchdog**: by default, closing the guard terminal, sending SIGINT/SIGTERM/SIGHUP, crashing the process, or abruptly killing it triggers the normal OS lock.
- No arbitrary remote shell and no destructive wipe functionality.

## Security behavior when the Guard process stops

Default:

```text
LOCK_ON_GUARD_EXIT=true
```

Normal stop path:

```text
Ctrl+C / SIGTERM / terminal SIGHUP
        ↓
immediate OS lock request
        ↓
guard shutdown
```

Abrupt stop path:

```text
Guard process killed/crashes
        ↓
detached exit watchdog detects parent death
        ↓
normal OS lock request
```

This is a normal desktop-session lock, not file deletion or shutdown.

For maintenance you can explicitly disable it in `.env`:

```bash
LOCK_ON_GUARD_EXIT=false
```

## Remote unlock

Remote unlock is included but intentionally opt-in:

```bash
ALLOW_REMOTE_UNLOCK=false
```

To enable it on a Linux machine you control:

```bash
ALLOW_REMOTE_UNLOCK=true
```

The bot always asks for a second confirmation before requesting unlock. Linux uses the normal session manager (`loginctl unlock-session`) and the desktop may refuse it. Laptop Guard does **not** bypass the Windows secure logon screen or store Windows/Linux login passwords.

A successful Linux remote unlock grants a short local-use grace period so the guard does not immediately retrigger when the owner resumes typing.

## Bale dashboard

```text
🛡 Protection      📷 Camera
🖥 Screen          🎙 Audio
💬 Chat            📜 Events
💻 System          ⚡ Power
        🩺 Status
```

Menus use `editMessageText` when possible so navigation does not create a new message for every button press.

## Bot commands

```text
/menu
/status
/sysinfo

/arm
/disarm
/allow 5
/lock
/unlock

/photo
/cameravideo 8
/screen
/screenvideo 8

/say سلام، لطفاً از لپ‌تاپ فاصله بگیرید
/ttsvoice man2
/ttsvoices
/ttsmode on
/ttstest

/listen 8
/voicechat 30
/voicechat_stop

/chat سلام، لطفاً از لپ‌تاپ فاصله بگیرید
/chatclose
/notify Maintenance message

/events
/suspend
/reboot
/shutdown
/id
/help
```

When Security Chat is open, you can simply send:

```text
Are you there?
```

or:

```text
لطفاً از لپ‌تاپ فاصله بگیرید.
```

without `/chat`; v9 forwards the message to the open Guard Chat and automatically renders the correct direction.

## Persian text-to-speech from Bale

The project uses the `PersianTTS` async API from `py-persian-tts` rather than the Selenium-based `TextToSpeech` class.

Basic usage from Bale:

```text
/say سلام. لطفاً از لپ‌تاپ فاصله بگیرید.
```

Or open:

```text
🎙 صدا → 🗣 متن → صدا
```

and send the next normal text message.

To keep speaking every ordinary text message without `/say`:

```text
/ttsmode on
```

Turn it off with:

```text
/ttsmode off
```

Select a voice:

```text
/ttsvoice woman2
```

Supported keys:

```text
woman1 woman2 woman3 woman4
man1 man2 man3 man4 man5 man6 man7 man8
boy1
```

The Audio menu also provides buttons for each voice. Generated audio is queued and played one item at a time.

Relevant `.env` settings:

```bash
PERSIAN_TTS_ENABLED=true
PERSIAN_TTS_VOICE=man2
PERSIAN_TTS_RATE_LIMIT=0.5
PERSIAN_TTS_MAX_CHARS=700
PERSIAN_TTS_NOTIFY=true
PERSIAN_TTS_MIRROR_CHAT=false
```

`ffplay`, `paplay`, `pw-play`, or `aplay` is needed to play generated audio. Installing `ffmpeg` is the easiest default because it provides `ffplay`.

## Warning flow

```text
Armed device
   ↓
keyboard / mouse activity
   ↓
camera + screen evidence
   ↓
5.png → 4.png → 3.png → 2.png → 1.png
(one image per second, fullscreen)
   ↓
normal OS screen lock
```

Warning images are stored at:

```text
laptop_guard/assets/warnings/5.png
laptop_guard/assets/warnings/4.png
laptop_guard/assets/warnings/3.png
laptop_guard/assets/warnings/2.png
laptop_guard/assets/warnings/1.png
```

Each is 1280×720 (16:9).

## Install

```bash
chmod +x install.sh run.sh doctor.sh
./install.sh
```

On Ubuntu/GNOME, install useful native packages:

```bash
sudo apt install python3-venv python3-tk ffmpeg gnome-screenshot libnotify-bin
```

If your system uses a version-specific Python package, install the matching Tk package, for example `python3.14-tk` where provided by your distribution.

Optional Wayland/wlroots tools:

```bash
sudo apt install grim wf-recorder
```

Configure `.env`:

```bash
BALE_BOT_TOKEN=YOUR_TOKEN
BALE_CHAT_ID=YOUR_OWNER_CHAT_ID

LOCK_ON_GUARD_EXIT=true
ALLOW_REMOTE_UNLOCK=false
ALLOW_REMOTE_POWER=false
CHAT_DIRECTION=auto
CHAT_SECONDS=120
PERSIAN_TTS_ENABLED=true
PERSIAN_TTS_VOICE=man2
```

Then:

```bash
./doctor.sh
./run.sh
```

## Privacy / safety

- Only the configured Bale chat ID can control the laptop.
- `/id` is available before pairing only to show the current Bale chat ID.
- Input monitoring records activity events, not key contents.
- Microphone intercom is visible locally.
- Camera/screen capture is for devices and spaces you own/control and where recording is permitted.
- Remote power controls require a confirmation step.
- Remote unlock is disabled by default and never handles the user's login password.
- No arbitrary remote shell is exposed.
- No destructive file wipe/self-destruct behavior is included.
