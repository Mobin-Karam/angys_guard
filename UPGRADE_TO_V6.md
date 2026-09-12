# Upgrade to v6

v6 reuses the existing persistent configuration under:

```text
~/.config/laptop-guard/
```

Upgrade the project directory, run the installer, then rerun setup once:

```bash
./install.sh
./run.sh setup
./run.sh doctor
```

## Migration changes

- Old `text_editor` chat surfaces migrate to `live_notepad`.
- `open_text_editor_mirror=true` migrates to `false`; the transcript file is still written but no external editor is auto-opened.
- Older `warning` input behavior without v6 countdown fields migrates to `warning_lock` with a 5-second visible countdown.
- Away/Night profiles use the visible countdown → desktop lock behavior.
- Home remains a warning-oriented lower-noise profile; Testing remains notify-only.

If you do not want countdown locking, rerun setup and choose `warning` or `notify` for unexpected keyboard/mouse activity.
