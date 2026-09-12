# Upgrade to v4

Your persistent configuration lives outside the project directory, so replacing the source directory normally keeps your Bale/Telegram pairing.

```bash
cd ~/Downloads
mv laptop_guard_v3 laptop_guard_v3_backup
unzip laptop_guard_v4.zip
cd laptop_guard_v4
./install.sh
./run.sh setup
./run.sh doctor
```

Running setup is recommended once after upgrade so you can choose the new profile, pre-event buffer, tamper, offline queue, USB and health options. Existing bot token/chat pairing can be reused.

v4 keeps the requested safety behavior: old configurations without a modern `input_action` migrate to `warning`, not automatic lock.
