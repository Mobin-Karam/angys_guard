from __future__ import annotations

import argparse
import time

from rich.console import Console
from rich.table import Table

from .config import CONFIG_PATH, load_config, save_config, setup_is_complete
from .profiles import PROFILE_LABELS, apply_profile
from .state import RuntimeStateStore
from .storage import EventStore
from .system import lock_screen

console = Console()


def cmd_setup(_):
    from .setup_wizard import run_setup
    cfg = run_setup(); return 0 if cfg.setup_complete else 2


def cmd_run(_):
    from .runtime_config import RuntimeConfigurationError, ensure_runtime_configuration
    try:
        cfg = ensure_runtime_configuration(console)
    except RuntimeConfigurationError as exc:
        console.print(f"[red]{exc}[/red]")
        return 2
    from .guard import LaptopGuard
    LaptopGuard(cfg).run()
    return 0


def cmd_doctor(_):
    from .doctor import run_doctor
    return run_doctor()


def cmd_arm(_):
    if not setup_is_complete():
        console.print("[red]Setup is incomplete. Run ./run.sh setup first.[/red]"); return 2
    cfg = load_config(); RuntimeStateStore().mutate(armed=True, grace_until=0.0, arm_ready_at=time.time() + cfg.security.arm_delay); console.print("[green]Guard armed.[/green]"); return 0


def cmd_disarm(_):
    RuntimeStateStore().mutate(armed=False, grace_until=0.0); console.print("[green]Guard disarmed.[/green]"); return 0


def cmd_status(_):
    s = RuntimeStateStore().refresh(); cfg = load_config(); store = EventStore()
    console.print(f"Device: {cfg.device_name}")
    console.print(f"Profile: {PROFILE_LABELS.get(cfg.profile, cfg.profile)}")
    console.print(f"Armed: {'yes' if s.armed else 'no'}")
    console.print(f"Active: {'yes' if s.active() else 'no'}")
    console.print(f"Camera: {'online' if s.camera_ok else 'unknown/offline'}")
    console.print(f"Input monitor: {'online' if s.input_ok else 'unknown/offline'}")
    console.print(f"Bot: {'online' if s.bot_online else 'unknown/offline'}")
    console.print(f"Offline queue: {store.outbox_count()}")
    return 0


def cmd_config(_):
    cfg = load_config(); console.print(f"Config file: {CONFIG_PATH}"); console.print(f"Setup complete: {'yes' if cfg.setup_complete else 'no'}"); console.print(cfg); return 0


def cmd_lock(_):
    locked = lock_screen()
    console.print("Lock requested." if locked else "Could not lock screen.")
    return 0 if locked else 2


def cmd_profile(args):
    cfg = load_config()
    if args.name is None:
        console.print(f"Current: {PROFILE_LABELS.get(cfg.profile, cfg.profile)}"); return 0
    apply_profile(cfg, args.name); save_config(cfg); console.print(f"[green]Profile set:[/green] {PROFILE_LABELS.get(args.name, args.name)}"); return 0


def cmd_events(args):
    rows = EventStore().recent(args.limit)
    table = Table(title="Recent Laptop Guard Events")
    for c in ["ID", "Time", "Severity", "Kind", "Detail"]: table.add_column(c)
    for r in rows: table.add_row(str(r[0]), str(r[1]), str(r[5]), str(r[2]), str(r[3]))
    console.print(table); return 0


def cmd_health(_):
    from .health import collect_health
    h = collect_health(); console.print(h); return 0


def cmd_test(args):
    from .tests_manual import test_bot, test_camera, test_lock, test_microphone, test_screen, test_input
    return {"camera": test_camera, "microphone": test_microphone, "bot": test_bot, "lock": test_lock, "screen": test_screen, "input": test_input}[args.target]()


def cmd_service(args):
    from .service import install_service, logs_service, status_service, uninstall_service
    ok = {"install": install_service, "uninstall": uninstall_service, "status": status_service, "logs": logs_service}[args.action]()
    return 0 if ok else 2


def cmd_autostart(args):
    from .service import autostart_enabled, set_autostart
    if args.action == "status":
        enabled = autostart_enabled()
        console.print(f"Autostart: {'enabled' if enabled else 'disabled'}")
        return 0
    ok = set_autostart(args.action == "on")
    console.print(f"Autostart {'enabled' if args.action == 'on' else 'disabled'}." if ok else "Could not update autostart.")
    return 0 if ok else 2


def build_parser():
    p = argparse.ArgumentParser(prog="laptop-guard", description="Laptop Guard v11.1")
    sub = p.add_subparsers(dest="command")
    sub.add_parser("setup", help="guided/resumable setup").set_defaults(func=cmd_setup)
    sub.add_parser("run", help="run the guard").set_defaults(func=cmd_run)
    sub.add_parser("doctor", help="check dependencies/configuration").set_defaults(func=cmd_doctor)
    sub.add_parser("arm", help="arm the guard").set_defaults(func=cmd_arm)
    sub.add_parser("disarm", help="disarm the guard").set_defaults(func=cmd_disarm)
    sub.add_parser("status", help="show runtime state").set_defaults(func=cmd_status)
    sub.add_parser("config", help="show non-secret configuration").set_defaults(func=cmd_config)
    sub.add_parser("lock", help="manually lock screen now").set_defaults(func=cmd_lock)
    pr = sub.add_parser("profile", help="show or change operating profile"); pr.add_argument("name", nargs="?", choices=["away", "home", "night", "testing", "custom"]); pr.set_defaults(func=cmd_profile)
    ev = sub.add_parser("events", help="show recent local events"); ev.add_argument("--limit", type=int, default=20); ev.set_defaults(func=cmd_events)
    sub.add_parser("health", help="show local health snapshot").set_defaults(func=cmd_health)
    test = sub.add_parser("test", help="test hardware/integration"); test.add_argument("target", choices=["camera", "microphone", "bot", "lock", "screen", "input"]); test.set_defaults(func=cmd_test)
    svc = sub.add_parser("service", help="manage systemd user service"); svc.add_argument("action", choices=["install", "uninstall", "status", "logs"]); svc.set_defaults(func=cmd_service)
    auto = sub.add_parser("autostart", help="run automatically after graphical login"); auto.add_argument("action", choices=["on", "off", "status"]); auto.set_defaults(func=cmd_autostart)
    return p


def main():
    parser = build_parser(); args = parser.parse_args()
    try:
        if not getattr(args, "command", None): return cmd_run(args)
        result = args.func(args); return result if isinstance(result, int) else 0
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]"); return 130
