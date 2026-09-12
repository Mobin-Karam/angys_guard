# Upgrade to Laptop Guard v3.2

The important compatibility fix in v3.2 is OpenCV.

OpenCV 5 moved classic HOG people detection out of the main OpenCV package. Older Laptop Guard releases allowed `opencv-python>=4.8`, so pip could install OpenCV 5 and `motion_person` would crash at startup with:

```text
AttributeError: module 'cv2' has no attribute 'HOGDescriptor'
```

## Upgrade an existing installation

From this project directory:

```bash
./install.sh
./run.sh doctor
./run.sh
```

`install.sh` now forces the compatible OpenCV 4.x package and verifies the HOG people detector before finishing.

Your existing config under `~/.config/laptop-guard/` is not deleted, so your Bale/Telegram pairing should remain.

## If OpenCV still conflicts

Only if `./install.sh` reports an OpenCV conflict, run:

```bash
source .venv/bin/activate
python -m pip uninstall -y opencv-contrib-python opencv-contrib-python-headless opencv-python-headless
./install.sh
```

Do not delete your `~/.config/laptop-guard/` directory unless you intentionally want to pair the bot again.
