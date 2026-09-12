# Upgrade to Laptop Guard v9

Keep your existing `.env`; v9 reads the old variables and supplies defaults for the new Persian TTS settings.

Recommended upgrade:

```bash
cp .env ~/laptop-guard.env.backup
```

Extract v9, then copy the old `.env` into the new folder:

```bash
cp ~/laptop-guard.env.backup /path/to/laptop_guard_bale_v9/.env
cd /path/to/laptop_guard_bale_v9
./install.sh
./doctor.sh
./run.sh
```

New optional `.env` values:

```bash
LOCK_ON_GUARD_EXIT=true
ALLOW_REMOTE_UNLOCK=false
ALLOW_REMOTE_POWER=false
CHAT_DIRECTION=auto
CHAT_SECONDS=120
CHAT_ALLOW_REPLY=true

PERSIAN_TTS_ENABLED=true
PERSIAN_TTS_VOICE=man2
PERSIAN_TTS_RATE_LIMIT=0.5
PERSIAN_TTS_MAX_CHARS=700
PERSIAN_TTS_NOTIFY=true
PERSIAN_TTS_MIRROR_CHAT=false
```

Important: with `LOCK_ON_GUARD_EXIT=true`, stopping the running guard or closing its terminal intentionally requests the normal OS screen lock. Set it to `false` temporarily if you are doing maintenance and do not want that behavior.


After upgrading, `./install.sh` installs `py-persian-tts==3.0.2`. Test it from Bale with `/ttstest`, then use `/say متن` or the Audio > متن → صدا menu.
