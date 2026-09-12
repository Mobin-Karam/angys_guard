# Upgrade to v5

Your persistent configuration and bot pairing remain under `~/.config/laptop-guard/`, so replacing the source directory does not normally remove them.

```bash
cd ~/Downloads
mv laptop_guard_v4 laptop_guard_v4_backup 2>/dev/null || true
unzip laptop_guard_v5_full.zip
cd laptop_guard_v5
./install.sh
./run.sh setup
./run.sh doctor
./run.sh
```

v5 migrates older configs by applying defaults for the new `[communication]`, `[screen]`, `[apps]`, and `[api]` sections. The requested warning-first behavior remains the default; it does not silently restore automatic locking.
