from __future__ import annotations

import getpass
import secrets
import shutil
import subprocess
import time
from collections.abc import Callable

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from .camera_devices import discover_cameras
from .config import (
    CONFIG_PATH,
    default_api_base,
    get_api_token,
    get_bot_token,
    get_legacy_bot_token,
    load_config,
    load_setup_progress,
    save_config,
    save_setup_progress,
    set_api_token,
    set_bot_token,
    migrate_legacy_bot_token,
)
from .models import AppConfig
from .profiles import PROFILE_LABELS, apply_profile
from .providers import build_provider

SETUP_SECTIONS: tuple[tuple[str, str], ...] = (
    ("identity", "Identity & profile"),
    ("provider", "Notification provider"),
    ("owner", "Owner pairing"),
    ("camera", "Camera"),
    ("audio", "Audio"),
    ("security", "Security behavior"),
    ("communication", "Communication surface"),
    ("screen", "Screen capture"),
    ("apps_api", "Apps & local API"),
    ("monitors", "Monitors"),
    ("startup", "Startup"),
)
SECTION_KEYS = tuple(key for key, _label in SETUP_SECTIONS)
SECTION_LABELS = dict(SETUP_SECTIONS)


class SetupSectionDeferred(RuntimeError):
    """Expected setup pause that preserves current safe configuration/secrets."""


def detect_audio_sources() -> list[str]:
    if not shutil.which("pactl"):
        return ["default"]
    try:
        out = subprocess.check_output(
            ["pactl", "list", "short", "sources"],
            text=True,
            timeout=5,
        )
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
        ids = [
            update.get("update_id")
            for update in pending
            if isinstance(update.get("update_id"), int)
        ] if pending else []
        if ids:
            offset = max(ids) + 1
    except Exception:
        pass

    console.print(
        "\nSend [bold]/start[/bold] to the bot from the account you want to authorize."
    )
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
    raise RuntimeError("Pairing timed out.")


def _choose_camera(cfg: AppConfig, console: Console) -> None:
    cameras = discover_cameras()
    if not cameras:
        console.print("[yellow]No usable capture camera was detected.[/yellow]")
        cfg.camera.index = IntPrompt.ask(
            "Camera index (manual fallback)",
            default=cfg.camera.index,
        )
        return
    if len(cameras) == 1:
        cfg.camera.index = cameras[0].index
        console.print(
            f"[green]Camera detected automatically:[/green] {cameras[0].label}"
        )
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


def _check_provider_token(cfg: AppConfig, token: str):
    from .doctor import check_bot_connectivity_detailed

    return check_bot_connectivity_detailed(cfg, token)


def _provider_check_parts(result) -> tuple[bool, str, str]:
    """Normalize detailed provider checks and legacy 2-tuples used by tests/callers."""
    if isinstance(result, tuple) and len(result) >= 3:
        return bool(result[0]), str(result[1]), str(result[2])
    ok, detail = result
    return bool(ok), str(detail), "ok" if ok else "auth"


def _validate_section(cfg: AppConfig, section: str) -> tuple[bool, str]:
    from .doctor import validate_setup_section

    return validate_setup_section(cfg, section)


def _ensure_provider_token(cfg: AppConfig, console: Console) -> str:
    provider = cfg.bot.provider
    stored = get_bot_token(provider)
    if stored:
        console.print("Validating stored bot credential...")
        ok, detail, kind = _provider_check_parts(
            _check_provider_token(cfg, stored)
        )
        if ok:
            console.print("[green]Stored bot credential is valid and will be reused.[/green]")
            return stored

        if kind == "auth":
            console.print(f"[yellow]{detail}[/yellow]")
            console.print(
                "The stored credential was not displayed and will be replaced only after validation."
            )
        else:
            console.print(f"[yellow]{detail}[/yellow]")
            console.print(
                "[green]Stored bot credential kept unchanged because the provider did not reject it.[/green]"
            )
            raise SetupSectionDeferred(
                "Fix the internet/proxy/API-base problem, then rerun setup. "
                "You do not need to enter another token unless the provider rejects it."
            )

    if not stored and get_legacy_bot_token():
        console.print(
            "[yellow]An older shared bot credential exists, but it is not tied to Bale or Telegram.[/yellow]"
        )
        console.print(
            f"For safety it will not be tried automatically against {provider.title()}. "
            f"Enter the {provider.title()} token once; it will be stored separately."
        )

    while True:
        token = getpass.getpass(
            f"{provider.title()} bot token: "
        ).strip()
        if not token:
            console.print("[red]A bot token is required.[/red]")
            continue

        ok, detail, kind = _provider_check_parts(
            _check_provider_token(cfg, token)
        )
        if ok:
            set_bot_token(token, provider)
            console.print(
                f"[green]{provider.title()} bot credential validated and stored privately.[/green]"
            )
            return token

        console.print(f"[red]{detail}[/red]")
        if kind == "auth":
            console.print("Enter a new token. The rejected token will not be saved.")
            continue

        console.print(
            "The entered token was not saved because validation could not reach/verify the provider, "
            "but it was not proven invalid."
        )
        raise SetupSectionDeferred(
            "Fix the internet/proxy/API-base problem, then rerun setup and validate the same token again."
        )


def _configure_identity(cfg: AppConfig, console: Console) -> None:
    cfg.device_name = (
        Prompt.ask("Device name", default=cfg.device_name).strip()
        or cfg.device_name
    )
    profile = Prompt.ask(
        "Starting profile",
        choices=["away", "home", "night", "testing", "custom"],
        default=cfg.profile,
    )
    if profile != "custom":
        apply_profile(cfg, profile)
    else:
        cfg.profile = "custom"
    console.print(
        f"Profile: [bold]{PROFILE_LABELS.get(cfg.profile, cfg.profile)}[/bold]"
    )


def _configure_provider(cfg: AppConfig, console: Console) -> None:
    previous_provider = cfg.bot.provider
    provider = Prompt.ask(
        "Notification provider",
        choices=["telegram", "bale", "local"],
        default=(
            previous_provider
            if previous_provider in {"telegram", "bale", "local"}
            else "telegram"
        ),
    )
    cfg.bot.provider = provider
    if provider != previous_provider or not cfg.bot.api_base:
        cfg.bot.api_base = default_api_base(provider)

    if provider == "local":
        cfg.bot.api_base = ""
        cfg.bot.chat_id = None
        cfg.bot.proxy = ""
        return

    cfg.bot.proxy = Prompt.ask(
        "Proxy URL (blank = direct)",
        default=cfg.bot.proxy,
    ).strip()
    cfg.bot.api_base = Prompt.ask(
        "API base URL",
        default=cfg.bot.api_base or default_api_base(provider),
    ).strip()
    save_config(cfg)
    _ensure_provider_token(cfg, console)


def _configure_owner(cfg: AppConfig, console: Console) -> None:
    if cfg.bot.provider == "local":
        cfg.bot.chat_id = None
        console.print("[dim]Local mode does not require remote owner pairing.[/dim]")
        return

    token = get_bot_token(cfg.bot.provider)
    if not token:
        raise RuntimeError("Provider credential is missing.")

    ok, _detail, kind = _provider_check_parts(
        _check_provider_token(cfg, token)
    )
    if not ok:
        if kind == "auth":
            raise RuntimeError(
                "Provider credential was rejected before owner pairing."
            )
        raise SetupSectionDeferred(
            "Provider connectivity must be restored before owner pairing. "
            "The stored credential was not proven invalid."
        )

    bot = build_provider(
        cfg.bot.provider,
        token,
        cfg.bot.api_base,
        cfg.bot.proxy,
    )
    if bot is None:
        raise RuntimeError("Configured provider is unavailable.")

    if cfg.bot.chat_id is not None and Confirm.ask(
        "An owner pairing already exists. Keep it?",
        default=True,
    ):
        console.print("[green]Existing owner pairing kept.[/green]")
        return

    if Confirm.ask(
        "Pair automatically by waiting for a new /start message?",
        default=True,
    ):
        cfg.bot.chat_id = pair_chat(bot, console)
    else:
        cfg.bot.chat_id = IntPrompt.ask("Owner chat ID")
    console.print("[green]Owner pairing saved.[/green]")


def _configure_camera(cfg: AppConfig, console: Console) -> None:
    _choose_camera(cfg, console)
    cfg.camera.enabled = Confirm.ask(
        "Start with camera enabled?",
        default=cfg.camera.enabled,
    )
    cfg.camera.mode = Prompt.ask(
        "Detection mode",
        choices=["motion", "motion_person"],
        default=cfg.camera.mode,
    )
    if cfg.camera.mode == "motion_person":
        from .camera import person_detection_capability

        ok, detail = person_detection_capability()
        if not ok:
            console.print(
                "[yellow]Person verifier unavailable; safe motion fallback will be used.[/yellow]"
            )
            console.print(f"[dim]{detail}[/dim]")
    cfg.camera.pre_event_seconds = max(
        0,
        min(
            IntPrompt.ask(
                "Pre-event video buffer (seconds)",
                default=cfg.camera.pre_event_seconds,
            ),
            15,
        ),
    )
    if Confirm.ask(
        "Record a post-event video clip?",
        default=cfg.camera.event_clip_seconds > 0,
    ):
        cfg.camera.event_clip_seconds = max(
            1,
            min(
                IntPrompt.ask(
                    "Post-event clip seconds",
                    default=max(1, cfg.camera.event_clip_seconds),
                ),
                60,
            ),
        )
    else:
        cfg.camera.event_clip_seconds = 0
    cfg.camera.tamper_enabled = Confirm.ask(
        "Detect camera blocked/frozen/disconnected?",
        default=cfg.camera.tamper_enabled,
    )


def _configure_audio(cfg: AppConfig, console: Console) -> None:
    sources = detect_audio_sources()
    console.print("Detected microphone sources:")
    default_audio = 1
    for i, source in enumerate(sources, 1):
        if source == cfg.audio.input:
            default_audio = i
        console.print(f"  {i}. {source}")
    choice = max(
        1,
        min(
            IntPrompt.ask("Microphone number", default=default_audio),
            len(sources),
        ),
    )
    cfg.audio.input = sources[choice - 1]
    cfg.audio.backend = "pulse" if shutil.which("pactl") else "alsa"
    cfg.audio.play_remote_voice = Confirm.ask(
        "Auto-play owner Voice messages on laptop speakers?",
        default=cfg.audio.play_remote_voice,
    )
    cfg.audio.sound_detection_enabled = Confirm.ask(
        "When armed, record and send a clip after loud environmental sound?",
        default=cfg.audio.sound_detection_enabled,
    )
    if cfg.audio.sound_detection_enabled:
        cfg.audio.sound_record_seconds = max(
            2,
            min(
                IntPrompt.ask(
                    "Sound-triggered recording seconds",
                    default=cfg.audio.sound_record_seconds,
                ),
                30,
            ),
        )
        cfg.audio.sound_cooldown = max(
            5,
            min(
                IntPrompt.ask(
                    "Seconds between sound alerts",
                    default=cfg.audio.sound_cooldown,
                ),
                3600,
            ),
        )
    cfg.audio.tts_enabled = Confirm.ask(
        "Enable local /say text-to-speech?",
        default=cfg.audio.tts_enabled,
    )


def _configure_security(cfg: AppConfig, console: Console) -> None:
    cfg.security.auto_arm = Confirm.ask(
        "Arm automatically when service starts?",
        default=cfg.security.auto_arm,
    )
    cfg.security.input_action = Prompt.ask(
        "Unexpected keyboard/mouse response",
        choices=["warning_lock", "warning", "notify"],
        default=(
            cfg.security.input_action
            if cfg.security.input_action in {"warning_lock", "warning", "notify"}
            else "warning_lock"
        ),
    )
    cfg.security.lock_on_input = False
    if cfg.security.input_action in {"warning", "warning_lock"}:
        default_seconds = (
            5
            if cfg.security.input_action == "warning_lock"
            else cfg.security.warning_seconds
        )
        cfg.security.warning_seconds = max(
            3,
            min(
                IntPrompt.ask(
                    "Visible warning/countdown seconds",
                    default=default_seconds,
                ),
                300,
            ),
        )
        cfg.security.lock_after_countdown = (
            cfg.security.input_action == "warning_lock"
        )
        console.print(f"Warning text: [bold]{cfg.security.warning_text}[/bold]")
    cfg.security.input_snapshot = Confirm.ask(
        "Take a camera snapshot on unexpected input?",
        default=cfg.security.input_snapshot,
    )
    cfg.security.intrusion_photo_background = Confirm.ask(
        "Use the event camera photo as the fullscreen warning background?",
        default=cfg.security.intrusion_photo_background,
    )
    cfg.security.input_screen_snapshot = Confirm.ask(
        "Capture a native Linux screen screenshot on unexpected input?",
        default=cfg.security.input_screen_snapshot,
    )
    cfg.security.input_screen_video_seconds = max(
        0,
        min(
            IntPrompt.ask(
                "Screen recording seconds after unexpected input (0=off)",
                default=cfg.security.input_screen_video_seconds,
            ),
            30,
        ),
    )
    cfg.security.allow_remote_unlock = Confirm.ask(
        "Allow remote unlock from bot?",
        default=cfg.security.allow_remote_unlock,
    )
    cfg.security.input_backend = Prompt.ask(
        "Input activity backend",
        choices=["auto", "evdev", "pynput"],
        default=cfg.security.input_backend,
    )


def _configure_communication(cfg: AppConfig, console: Console) -> None:
    surface_default = (
        "live_notepad"
        if cfg.communication.surface == "text_editor"
        else cfg.communication.surface
    )
    cfg.communication.surface = Prompt.ask(
        "Security conversation surface",
        choices=["guard_chat", "live_notepad", "both", "fullscreen"],
        default=(
            surface_default
            if surface_default in {"guard_chat", "live_notepad", "both", "fullscreen"}
            else "both"
        ),
    )
    cfg.communication.chat_seconds = max(
        10,
        min(
            IntPrompt.ask(
                "Security chat/countdown seconds",
                default=cfg.communication.chat_seconds,
            ),
            600,
        ),
    )
    cfg.communication.allow_visitor_reply = Confirm.ask(
        "Allow a person at the laptop to reply in Guard Chat?",
        default=cfg.communication.allow_visitor_reply,
    )
    cfg.communication.open_text_editor_mirror = False
    console.print(
        "[dim]Live Notepad is built into Guard Chat; the external editor mirror is no longer auto-opened.[/dim]"
    )


def _configure_screen(cfg: AppConfig, console: Console) -> None:
    cfg.screen.screenshots_enabled = Confirm.ask(
        "Allow paired owner to request visible screen snapshots?",
        default=cfg.screen.screenshots_enabled,
    )
    cfg.screen.screen_video_enabled = Confirm.ask(
        "Allow bounded screen recordings when supported?",
        default=cfg.screen.screen_video_enabled,
    )
    cfg.screen.notify_local_capture = True


def _configure_apps_api(cfg: AppConfig, console: Console) -> None:
    cfg.apps.enabled = Confirm.ask(
        "Enable safe GUI application manager?",
        default=cfg.apps.enabled,
    )
    if cfg.apps.enabled:
        console.print(
            "[dim]Application actions use .desktop allowlists; no arbitrary shell is exposed.[/dim]"
        )

    cfg.api.enabled = Confirm.ask(
        "Enable localhost authenticated control API?",
        default=cfg.api.enabled,
    )
    if cfg.api.enabled:
        cfg.api.host = "127.0.0.1"
        cfg.api.port = max(
            1024,
            min(
                IntPrompt.ask("Local API port", default=cfg.api.port),
                65535,
            ),
        )
        if not get_api_token():
            set_api_token(secrets.token_urlsafe(32))
        console.print(
            "[green]Local API credential is stored privately.[/green]"
        )


def _configure_monitors(cfg: AppConfig, console: Console) -> None:
    cfg.monitors.offline_queue = Confirm.ask(
        "Queue security alerts while bot/network is offline?",
        default=cfg.monitors.offline_queue,
    )
    cfg.monitors.usb_events = Confirm.ask(
        "Alert about USB add/remove while armed?",
        default=cfg.monitors.usb_events,
    )
    cfg.monitors.health_events = Confirm.ask(
        "Monitor battery/disk/temperature health?",
        default=cfg.monitors.health_events,
    )
    cfg.monitors.failed_login_events = Confirm.ask(
        "Notify the owner about failed Linux login attempts?",
        default=cfg.monitors.failed_login_events,
    )


def _configure_startup(cfg: AppConfig, console: Console) -> None:
    cfg.startup.enabled = Confirm.ask(
        "Start Laptop Guard automatically after graphical login?",
        default=cfg.startup.enabled,
    )
    save_config(cfg)
    try:
        from .service import set_autostart

        ok = set_autostart(cfg.startup.enabled, start_now=False)
    except OSError:
        ok = False

    if cfg.startup.enabled and not ok:
        raise RuntimeError("Autostart could not be enabled.")
    if not cfg.startup.enabled and not ok:
        console.print(
            "[yellow]Autostart is disabled in configuration; systemd state could not be updated.[/yellow]"
        )


SECTION_HANDLERS: dict[str, Callable[[AppConfig, Console], None]] = {
    "identity": _configure_identity,
    "provider": _configure_provider,
    "owner": _configure_owner,
    "camera": _configure_camera,
    "audio": _configure_audio,
    "security": _configure_security,
    "communication": _configure_communication,
    "screen": _configure_screen,
    "apps_api": _configure_apps_api,
    "monitors": _configure_monitors,
    "startup": _configure_startup,
}


def _load_completed(cfg: AppConfig) -> set[str]:
    completed = load_setup_progress() & set(SECTION_KEYS)
    if cfg.setup_complete:
        completed.update(SECTION_KEYS)

    # A saved provider checkpoint predating provider-scoped tokens is a
    # trustworthy association. Migrate before validation reads the token.
    if "provider" in completed and cfg.bot.provider in {"telegram", "bale"}:
        migrate_legacy_bot_token(cfg.bot.provider)

    return completed


def _validate_completed(
    cfg: AppConfig,
    completed: set[str],
) -> tuple[set[str], dict[str, str]]:
    valid = set(completed)
    issues: dict[str, str] = {}
    for key in SECTION_KEYS:
        if key not in valid:
            continue
        ok, detail = _validate_section(cfg, key)
        if not ok:
            valid.discard(key)
            issues[key] = detail
    return valid, issues


def _checkpoint(cfg: AppConfig, completed: set[str]) -> None:
    cfg.setup_complete = set(SECTION_KEYS).issubset(completed)
    save_config(cfg)
    save_setup_progress(completed)


def _print_section_status(
    console: Console,
    completed: set[str],
    issues: dict[str, str] | None = None,
) -> None:
    issues = issues or {}
    console.print("\n[bold]Setup sections[/bold]")
    for key, label in SETUP_SECTIONS:
        if key in completed:
            state = "[green]completed[/green]"
        elif key in issues:
            state = "[red]needs attention[/red]"
        else:
            state = "[yellow]pending[/yellow]"
        console.print(f"  {label:<24} {state}")
        if key in issues:
            console.print(f"    [dim]{issues[key]}[/dim]")


def _first_incomplete(completed: set[str]) -> str | None:
    return next((key for key in SECTION_KEYS if key not in completed), None)


def _choose_section(console: Console) -> str | None:
    console.print("\n[bold]Choose a section to edit[/bold]")
    for index, (key, label) in enumerate(SETUP_SECTIONS, 1):
        console.print(f"  {index}. {label} [dim]({key})[/dim]")
    console.print("  0. Cancel")
    choice = IntPrompt.ask(
        "Section number",
        default=0,
    )
    if choice <= 0:
        return None
    choice = max(1, min(choice, len(SETUP_SECTIONS)))
    return SETUP_SECTIONS[choice - 1][0]


def _resume_action() -> str:
    return Prompt.ask(
        "Continue setup",
        choices=["resume", "edit"],
        default="resume",
    )


def _run_section(
    cfg: AppConfig,
    completed: set[str],
    key: str,
    console: Console,
) -> bool:
    label = SECTION_LABELS[key]
    console.rule(f"[bold]{label}[/bold]")

    old_profile = cfg.profile
    old_provider = cfg.bot.provider

    # Before editing a previously completed provider section, migrate the old
    # shared credential while its provider association is still trustworthy,
    # then mark the section pending so a crash cannot re-associate it later.
    if key == "provider" and key in completed:
        if old_provider in {"telegram", "bale"}:
            migrate_legacy_bot_token(old_provider)
        completed.discard(key)
        _checkpoint(cfg, completed)

    try:
        SECTION_HANDLERS[key](cfg, console)
    except KeyboardInterrupt:
        raise
    except SetupSectionDeferred as exc:
        completed.discard(key)
        _checkpoint(cfg, completed)
        console.print(f"[yellow]{label} paused:[/yellow] {exc}")
        console.print(
            "Saved settings were kept; stored secrets were not printed or replaced."
        )
        return False
    except Exception:
        completed.discard(key)
        _checkpoint(cfg, completed)
        console.print(
            f"[red]{label} could not be completed safely.[/red]"
        )
        console.print(
            "Fix this section and rerun setup; stored secrets were not printed."
        )
        return False

    if key == "identity" and cfg.profile != old_profile:
        for dependent in ("camera", "security", "monitors"):
            completed.discard(dependent)
    if key == "provider" and cfg.bot.provider != old_provider:
        completed.discard("owner")

    save_config(cfg)
    ok, detail = _validate_section(cfg, key)
    if not ok:
        completed.discard(key)
        _checkpoint(cfg, completed)
        console.print(f"[red]{label} still needs attention:[/red] {detail}")
        console.print(
            f"Rerun setup to return directly to {label}."
        )
        return False

    completed.add(key)
    _checkpoint(cfg, completed)
    console.print(f"[green]{label} completed.[/green]")
    return True


def run_reconfigure(
    section: str | None = None,
    *,
    console: Console | None = None,
    cfg: AppConfig | None = None,
    completed: set[str] | None = None,
) -> AppConfig:
    console = console or Console()
    cfg = cfg or load_config()
    completed = set(completed) if completed is not None else _load_completed(cfg)

    if section is None:
        _print_section_status(console, completed)
        section = _choose_section(console)
        if section is None:
            return cfg

    if section not in SECTION_HANDLERS:
        console.print(f"[red]Unknown setup section: {section}[/red]")
        return cfg

    _run_section(cfg, completed, section, console)
    _checkpoint(cfg, completed)

    if cfg.setup_complete:
        console.print(
            "\n[green]Configuration remains complete.[/green]"
        )
    else:
        next_key = _first_incomplete(completed)
        if next_key:
            console.print(
                f"\n[yellow]{SECTION_LABELS[next_key]} now needs attention. "
                "Run ./run.sh setup to resume.[/yellow]"
            )
    return cfg


def run_setup(*, console: Console | None = None) -> AppConfig:
    console = console or Console()
    console.print(
        Panel.fit(
            "[bold]Laptop Guard v11 Setup[/bold]\nSection-checkpointed + resumable configuration",
            border_style="cyan",
        )
    )
    cfg = load_config() if CONFIG_PATH.exists() else AppConfig()
    completed = _load_completed(cfg)
    completed, issues = _validate_completed(cfg, completed)
    _checkpoint(cfg, completed)
    _print_section_status(console, completed, issues)

    if cfg.setup_complete:
        console.print(
            "\n[green]Setup is complete.[/green] Choose one section to reconfigure, or cancel."
        )
        return run_reconfigure(
            console=console,
            cfg=cfg,
            completed=completed,
        )

    first = _first_incomplete(completed)
    if first and first in issues:
        console.print(
            f"\n[yellow]Saved validation points to {SECTION_LABELS[first]}; setup will resume there.[/yellow]"
        )

    if completed:
        action = _resume_action()
        if action == "edit":
            return run_reconfigure(
                console=console,
                cfg=cfg,
                completed=completed,
            )

    first = _first_incomplete(completed)
    if first:
        console.print(
            f"\nResuming at: [bold]{SECTION_LABELS[first]}[/bold]"
        )

    try:
        for key in SECTION_KEYS:
            if key in completed:
                continue
            if not _run_section(cfg, completed, key, console):
                return cfg
    except KeyboardInterrupt:
        _checkpoint(cfg, completed)
        console.print(
            "\n[yellow]Setup paused. Completed sections were saved; rerun setup to resume here.[/yellow]"
        )
        return cfg

    _checkpoint(cfg, completed)
    if cfg.setup_complete:
        console.print(
            "\n[green]Configuration saved and setup completed.[/green]"
        )
        console.print(
            "Run: [bold]./run.sh doctor[/bold]\nThen: [bold]./run.sh[/bold]"
        )
    return cfg
