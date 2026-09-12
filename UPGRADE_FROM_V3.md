# Upgrade from Laptop Guard v3.0

v3.1 fixes interrupted setup, wrong-provider bot tests, noisy camera probing, and Ctrl+C tracebacks.

## Recommended upgrade

1. Stop any running guard/service:

```bash
./run.sh service uninstall 2>/dev/null || true
```

2. Extract v3.1 and run:

```bash
chmod +x install.sh run.sh
./install.sh
./run.sh setup
```

3. If v3.0 already stored a token in `~/.config/laptop-guard/secrets.json`, the wizard offers to reuse it. Explicitly choose the matching provider (`bale` or `telegram`).

4. If the previous setup was interrupted before `config.toml` was written, send `/start` again when pairing is requested. v3.1 saves the chat ID immediately, so later interruption will not lose it.

5. Verify:

```bash
./run.sh doctor
./run.sh test camera
./run.sh test microphone
./run.sh test bot
```

A Wayland warning is expected on Ubuntu Wayland because global keyboard/mouse monitoring can be restricted by the compositor. Camera, microphone, bot, and screen-lock features are independent of that warning.
