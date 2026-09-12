#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"

if ! "$PYTHON" -m venv .venv 2>/dev/null; then
  echo "Could not create a venv. On Ubuntu install the matching python3-venv package first."
  echo "Example: sudo apt install python3-venv python3-tk ffmpeg vlc"
  exit 1
fi
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

echo ""
echo "Laptop Guard no longer requires a .env file."
echo "On first run it will ask for required configuration, validate the bot token,"
echo "pair the owner chat, and save settings under ~/.config/laptop-guard/."
echo ""
echo "Recommended Ubuntu packages:"
echo "  sudo apt install python3-tk ffmpeg vlc gnome-screenshot libnotify-bin"
echo "Wayland/wlroots screen video fallback: sudo apt install grim wf-recorder"
echo "Persian TTS: py-persian-tts 3.0.2 is installed from requirements.txt."
echo ""
echo "Installation complete. Start interactive setup with:"
echo "  ./run.sh setup"
echo "Then verify with:"
echo "  ./run.sh doctor"
echo "Then start with:"
echo "  ./run.sh"
