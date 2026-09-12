#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [ ! -d .venv ]; then
  echo "No .venv found; running the normal installer instead."
  exec ./install.sh
fi

. .venv/bin/activate
python -m pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python opencv-contrib-python-headless >/dev/null 2>&1 || true
python -m pip install --upgrade "opencv-python>=4.13,<5"
python -m pip install -e .
python - <<'PY'
import cv2
print("OpenCV:", cv2.__version__)
print("HOGDescriptor:", hasattr(cv2, "HOGDescriptor"))
print("People detector:", hasattr(cv2, "HOGDescriptor_getDefaultPeopleDetector"))
if not hasattr(cv2, "HOGDescriptor") or not hasattr(cv2, "HOGDescriptor_getDefaultPeopleDetector"):
    raise SystemExit("Repair failed: compatible HOG detector is still unavailable")
print("OpenCV repair complete.")
PY
