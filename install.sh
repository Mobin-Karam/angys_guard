#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"

if ! "$PYTHON" -m venv .venv 2>/dev/null; then
  echo "Could not create a venv. On Ubuntu install the matching python3-venv package first."
  echo "Example: sudo apt install python3-venv python3-tk ffmpeg"
  exit 1
fi
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  chmod 600 .env
  echo "Created .env. Add BALE_BOT_TOKEN, run ./run.sh, send /id, then add BALE_CHAT_ID."
fi

echo "Recommended Ubuntu packages:"
echo "  sudo apt install python3-tk ffmpeg gnome-screenshot libnotify-bin"
echo "Wayland/wlroots screen video fallback: sudo apt install grim wf-recorder"
echo "Persian TTS: py-persian-tts 3.0.2 is installed from requirements.txt."
echo "Use /say متن or the Audio > متن → صدا menu in Bale."
echo "Installation complete. Run: ./doctor.sh && ./run.sh"

echo "Tkinter is optional for the core bot, but required for fullscreen chat/warning windows."
