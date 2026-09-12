# Upgrade to Laptop Guard v3.3

v3.3 adds:

- Persian fullscreen warning on unexpected mouse/keyboard activity (default)
- no automatic lock for input events unless `input_action = "lock"` is explicitly selected
- bot dashboard with inline menus
- owner Voice/Audio messages downloaded and automatically played on the laptop
- remote camera on/off controls
- privacy-safe camera indicator controls where Linux exposes a writable camera LED
- input-event camera snapshots

Your existing config in `~/.config/laptop-guard/` is preserved. Old configs that do not contain `input_action` default to `warning`.

For fullscreen warning support on Ubuntu:

```bash
sudo apt install python3-tk
```

For Voice playback, `ffplay` is installed with `ffmpeg`:

```bash
sudo apt install ffmpeg
```

Run setup once if you want to review the new options:

```bash
./run.sh setup
```
