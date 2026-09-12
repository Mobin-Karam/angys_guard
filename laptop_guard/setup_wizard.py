from __future__ import annotations

import getpass
import shutil
import subprocess
import time

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from .camera_devices import discover_cameras
from .config import CONFIG_PATH, default_api_base, get_bot_token, load_config, save_config, set_bot_token, get_api_token, set_api_token
from .models import AppConfig
from .profiles import PROFILE_LABELS, apply_profile
from .providers import build_provider


def detect_audio_sources() -> list[str]:
    if not shutil.which("pactl"):
        return ["default"]
    try:
        out = subprocess.check_output(["pactl", "list", "short", "sources"], text=True, timeout=5)
        names = []
        for line in out.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2 and ".monitor" not in parts[1]:
                names.append(parts[1])
        return names or ["default"]
    except Exception:
        return ["default"]


def pair_chat(bot, console: Console, timeout_seconds: int = 180) -> int:
    offset = None
    try:
        pending = bot.get_updates(offset=None, timeout=1)
        ids = [u.get("update_id") for u in pending if isinstance(u.get("update_id"), int)] if pending else []
        if ids:
            offset = max(ids) + 1
    except Exception:
        pass
    console.print("\nSend [bold]/start[/bold] to the bot from the account you want to authorize.")
    console.print("Waiting for a NEW /start message...")
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        updates = bot.get_updates(offset=offset, timeout=8)
        for update in updates:
            uid = update.get("update_id")
            if isinstance(uid, int):
                offset = uid + 1
            msg = update.get("message") or update.get("edited_message")
            if not msg:
                continue
            if not str(msg.get("text") or "").strip().startswith("/start"):
                continue
            chat_id = (msg.get("chat") or {}).get("id")
            if isinstance(chat_id, int):
                return chat_id
    raise RuntimeError("Pairing timed out. Run setup again and send /start to the bot.")


def _choose_camera(cfg: AppConfig, console: Console) -> None:
    cameras = discover_cameras()
    if not cameras:
        console.print("[yellow]No usable capture camera was detected.[/yellow]")
        cfg.camera.index = IntPrompt.ask("Camera index (manual fallback)", default=cfg.camera.index)
        return
    if len(cameras) == 1:
        cfg.camera.index = cameras[0].index
        console.print(f"[green]Camera detected automatically:[/green] {cameras[0].label}")
        return
    console.print("Detected capture cameras:")
    current_choice = 1
    for i, camera in enumerate(cameras, 1):
        marker = " [current]" if camera.index == cfg.camera.index else ""
        if marker:
            current_choice = i
        console.print(f"  {i}. {camera.label}{marker}")
    choice = IntPrompt.ask("Camera number", default=current_choice)
    cfg.camera.index = cameras[max(1, min(choice, len(cameras))) - 1].index


def run_setup() -> AppConfig:
    console = Console()
    console.print(Panel.fit("[bold]Laptop Guard v6 Setup[/bold]\nGuided + resumable configuration", border_style="cyan"))
    cfg = load_config() if CONFIG_PATH.exists() else AppConfig()
    cfg.setup_complete = False
    save_config(cfg)
    try:
        cfg.device_name = Prompt.ask("Device name", default=cfg.device_name).strip() or cfg.device_name
        profile = Prompt.ask("Starting profile", choices=["away", "home", "night", "testing", "custom"], default=cfg.profile)
        if profile != "custom":
            apply_profile(cfg, profile)
        else:
            cfg.profile = "custom"
        console.print(f"Profile: [bold]{PROFILE_LABELS.get(cfg.profile, cfg.profile)}[/bold]")
        save_config(cfg)

        previous_provider = cfg.bot.provider
        provider = Prompt.ask("Notification provider", choices=["telegram", "bale", "local"], default=previous_provider if previous_provider in {"telegram", "bale", "local"} else "telegram")
        cfg.bot.provider = provider
        if provider != previous_provider or not cfg.bot.api_base:
            cfg.bot.api_base = default_api_base(provider)
        if provider == "local":
            cfg.bot.api_base = ""; cfg.bot.chat_id = None; cfg.bot.proxy = ""; save_config(cfg)
        else:
            stored_token = get_bot_token()
            token = stored_token if stored_token and Confirm.ask("A stored bot token exists. Reuse it?", default=True) else ""
            if not token:
                token = getpass.getpass(f"{provider.title()} bot token: ").strip()
            if not token:
                raise RuntimeError("A bot token is required.")
            cfg.bot.proxy = Prompt.ask("Proxy URL (blank = direct)", default=cfg.bot.proxy).strip()
            cfg.bot.api_base = Prompt.ask("API base URL", default=cfg.bot.api_base or default_api_base(provider)).strip()
            save_config(cfg)
            bot = build_provider(provider, token, cfg.bot.api_base, cfg.bot.proxy)
            console.print("Testing bot connection...")
            me = bot.get_me()
            console.print(f"[green]Connected[/green] to {me.get('username') or me.get('first_name') or 'bot'}")
            set_bot_token(token)
            reuse = cfg.bot.chat_id is not None and Confirm.ask(f"Reuse paired owner chat {cfg.bot.chat_id}?", default=True)
            if not reuse:
                cfg.bot.chat_id = pair_chat(bot, console)
            save_config(cfg)
            console.print(f"[green]Owner paired and saved.[/green] Chat ID: {cfg.bot.chat_id}")

        _choose_camera(cfg, console)
        cfg.camera.enabled = Confirm.ask("Start with camera enabled?", default=cfg.camera.enabled)
        cfg.camera.mode = Prompt.ask("Detection mode", choices=["motion", "motion_person"], default=cfg.camera.mode)
        if cfg.camera.mode == "motion_person":
            from .camera import person_detection_capability
            ok, detail = person_detection_capability()
            if not ok:
                console.print(f"[yellow]Person verifier unavailable; safe motion fallback will be used.[/yellow]\n[dim]{detail}[/dim]")
        cfg.camera.pre_event_seconds = max(0, min(IntPrompt.ask("Pre-event video buffer (seconds)", default=cfg.camera.pre_event_seconds), 15))
        if Confirm.ask("Record a post-event video clip?", default=cfg.camera.event_clip_seconds > 0):
            cfg.camera.event_clip_seconds = max(1, min(IntPrompt.ask("Post-event clip seconds", default=max(1, cfg.camera.event_clip_seconds)), 60))
        else:
            cfg.camera.event_clip_seconds = 0
        cfg.camera.tamper_enabled = Confirm.ask("Detect camera blocked/frozen/disconnected?", default=cfg.camera.tamper_enabled)
        save_config(cfg)

        sources = detect_audio_sources()
        console.print("Detected microphone sources:")
        default_audio = 1
        for i, source in enumerate(sources, 1):
            if source == cfg.audio.input:
                default_audio = i
            console.print(f"  {i}. {source}")
        choice = max(1, min(IntPrompt.ask("Microphone number", default=default_audio), len(sources)))
        cfg.audio.input = sources[choice - 1]
        cfg.audio.backend = "pulse" if shutil.which("pactl") else "alsa"
        cfg.audio.play_remote_voice = Confirm.ask("Auto-play owner Voice messages on laptop speakers?", default=cfg.audio.play_remote_voice)
        cfg.audio.tts_enabled = Confirm.ask("Enable local /say text-to-speech?", default=cfg.audio.tts_enabled)
        save_config(cfg)

        cfg.security.auto_arm = Confirm.ask("Arm automatically when service starts?", default=cfg.security.auto_arm)
        cfg.security.input_action = Prompt.ask(
            "Unexpected keyboard/mouse response",
            choices=["warning_lock", "warning", "notify"],
            default=cfg.security.input_action if cfg.security.input_action in {"warning_lock", "warning", "notify"} else "warning_lock",
        )
        cfg.security.lock_on_input = False
        if cfg.security.input_action in {"warning", "warning_lock"}:
            default_seconds = 5 if cfg.security.input_action == "warning_lock" else cfg.security.warning_seconds
            cfg.security.warning_seconds = max(3, min(IntPrompt.ask("Visible warning/countdown seconds", default=default_seconds), 300))
            cfg.security.lock_after_countdown = cfg.security.input_action == "warning_lock"
            console.print(f"Warning text: [bold]{cfg.security.warning_text}[/bold]")
        cfg.security.input_snapshot = Confirm.ask("Take a camera snapshot on unexpected input?", default=cfg.security.input_snapshot)
        cfg.security.intrusion_photo_background = Confirm.ask("Use the event camera photo as the fullscreen warning background?", default=cfg.security.intrusion_photo_background)
        cfg.security.input_screen_snapshot = Confirm.ask("Capture a native Linux screen screenshot on unexpected input?", default=cfg.security.input_screen_snapshot)
        cfg.security.input_screen_video_seconds = max(0, min(IntPrompt.ask("Screen recording seconds after unexpected input (0=off)", default=cfg.security.input_screen_video_seconds), 30))
        cfg.security.allow_remote_unlock = Confirm.ask("Allow remote unlock from bot?", default=cfg.security.allow_remote_unlock)
        cfg.security.input_backend = Prompt.ask("Input activity backend", choices=["auto", "evdev", "pynput"], default=cfg.security.input_backend)
        save_config(cfg)

        surface_default = "live_notepad" if cfg.communication.surface == "text_editor" else cfg.communication.surface
        cfg.communication.surface = Prompt.ask(
            "Security conversation surface",
            choices=["guard_chat", "live_notepad", "both", "fullscreen"],
            default=surface_default if surface_default in {"guard_chat", "live_notepad", "both", "fullscreen"} else "both",
        )
        cfg.communication.chat_seconds = max(10, min(IntPrompt.ask("Security chat/countdown seconds", default=cfg.communication.chat_seconds), 600))
        cfg.communication.allow_visitor_reply = Confirm.ask("Allow a person at the laptop to reply in Guard Chat?", default=cfg.communication.allow_visitor_reply)
        cfg.communication.open_text_editor_mirror = False
        console.print("[dim]Live Notepad is built into Guard Chat; the external editor mirror is no longer auto-opened.[/dim]")
        save_config(cfg)

        cfg.screen.screenshots_enabled = Confirm.ask("Allow paired owner to request visible screen snapshots?", default=cfg.screen.screenshots_enabled)
        cfg.screen.screen_video_enabled = Confirm.ask("Allow bounded screen recordings when supported?", default=cfg.screen.screen_video_enabled)
        cfg.screen.notify_local_capture = True
        save_config(cfg)

        cfg.apps.enabled = Confirm.ask("Enable safe GUI application manager?", default=cfg.apps.enabled)
        if cfg.apps.enabled:
            console.print("[dim]Application actions use .desktop allowlists; no arbitrary shell is exposed.[/dim]")
        save_config(cfg)

        cfg.api.enabled = Confirm.ask("Enable localhost authenticated control API?", default=cfg.api.enabled)
        if cfg.api.enabled:
            cfg.api.host = "127.0.0.1"
            cfg.api.port = max(1024, min(IntPrompt.ask("Local API port", default=cfg.api.port), 65535))
            if not get_api_token():
                import secrets
                set_api_token(secrets.token_urlsafe(32))
            console.print("[green]Local API token generated/stored in protected secrets.json.[/green]")
        save_config(cfg)

        cfg.monitors.offline_queue = Confirm.ask("Queue security alerts while bot/network is offline?", default=cfg.monitors.offline_queue)
        cfg.monitors.usb_events = Confirm.ask("Alert about USB add/remove while armed?", default=cfg.monitors.usb_events)
        cfg.monitors.health_events = Confirm.ask("Monitor battery/disk/temperature health?", default=cfg.monitors.health_events)
        save_config(cfg)

        cfg.setup_complete = True
        save_config(cfg)
        console.print("\n[green]Configuration saved and setup completed.[/green]")
        console.print("Run: [bold]./run.sh doctor[/bold]\nThen: [bold]./run.sh[/bold]")
        return cfg
    except KeyboardInterrupt:
        cfg.setup_complete = False; save_config(cfg)
        console.print("\n[yellow]Setup paused. Progress was saved. Run setup again to resume.[/yellow]")
        return cfg
    except Exception as exc:
        cfg.setup_complete = False; save_config(cfg)
        console.print(f"\n[red]Setup could not continue:[/red] {exc}")
        console.print("Completed steps were saved; run setup again to resume.")
        return cfg
