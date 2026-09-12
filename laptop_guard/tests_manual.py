from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from rich.console import Console

from .camera_devices import camera_label, probe_camera
from .config import CONFIG_PATH, get_bot_token, load_config, setup_is_complete
from .providers import build_provider
from .system import lock_screen

console = Console()


def test_camera() -> int:
    cfg = load_config()
    ok, resolution = probe_camera(cfg.camera.index)
    if not ok:
        console.print(f"[red]{camera_label(cfg.camera.index)} could not capture a frame.[/red]")
        return 1
    w, h = resolution or (0, 0)
    console.print(f"[green]Camera OK[/green] — {camera_label(cfg.camera.index)} — captured {w}x{h} frame")
    return 0


def test_microphone() -> int:
    cfg = load_config()
    if not shutil.which("ffmpeg"):
        console.print("[red]ffmpeg is not installed.[/red]")
        return 1
    backend = cfg.audio.backend
    if backend == "auto":
        backend = "pulse" if shutil.which("pactl") else "alsa"
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "mic-test.ogg"
        source = cfg.audio.input or "default"
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-f", backend, "-i", source,
            "-t", "2", "-c:a", "libopus", "-y", str(out),
        ]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)
        if result.returncode == 0 and out.exists() and out.stat().st_size > 0:
            console.print("[green]Microphone OK[/green] — recorded a 2-second test")
            return 0
        console.print("[red]Microphone test failed.[/red]")
        err = result.stderr.decode(errors="ignore").strip()
        if err:
            console.print(err[-800:])
        return 1


def test_bot() -> int:
    if not CONFIG_PATH.exists() or not setup_is_complete():
        console.print(
            "[yellow]Bot test skipped: setup is incomplete.[/yellow]\n"
            "Run [bold]./run.sh setup[/bold] first. "
            "Laptop Guard will not guess Telegram/Bale from defaults."
        )
        return 1
    cfg = load_config()
    if cfg.bot.provider == "local":
        console.print("Bot provider is local-only.")
        return 0
    token = get_bot_token()
    if not token:
        console.print("[red]No stored bot token. Run setup.[/red]")
        return 1
    if cfg.bot.chat_id is None:
        console.print("[red]Owner chat is not paired. Run setup.[/red]")
        return 1
    try:
        bot = build_provider(cfg.bot.provider, token, cfg.bot.api_base, cfg.bot.proxy)
        me = bot.get_me()
        console.print(
            f"[green]{cfg.bot.provider.title()} bot OK[/green] — "
            f"{me.get('username') or me.get('first_name') or cfg.bot.provider}"
        )
        bot.send_message(cfg.bot.chat_id, "Laptop Guard bot connection test succeeded.")
        console.print(f"Test message sent to owner chat {cfg.bot.chat_id}.")
        return 0
    except Exception as exc:
        console.print(f"[red]{cfg.bot.provider.title()} bot test failed:[/red] {exc}")
        return 1


def test_lock() -> int:
    console.print("Requesting screen lock now...")
    return 0 if lock_screen() else 1


def test_screen() -> int:
    from .screen_capture import ScreenCaptureManager
    mgr = ScreenCaptureManager(notify_local=False)
    console.print(f"Screenshot backend: {mgr.screenshot_backend}")
    console.print(f"Video backend: {mgr.video_backend}")
    if mgr.screenshot_backend == "unavailable":
        console.print("[yellow]No supported screenshot backend was detected.[/yellow]")
        return 1
    path, detail = mgr.snapshot()
    if path:
        console.print(f"[green]Screen snapshot OK[/green] — {path} ({detail})")
        return 0
    console.print(f"[red]Screen snapshot failed:[/red] {detail}")
    return 1


def test_input() -> int:
    cfg = load_config()
    from .input_monitor import InputMonitor
    monitor = InputMonitor(cfg.security.mouse_move_threshold, lambda *_: None, backend=cfg.security.input_backend)
    console.print(f"Input preference: {cfg.security.input_backend}")
    console.print(f"Availability: {monitor.availability_detail}")
    return 0 if monitor.available else 1
