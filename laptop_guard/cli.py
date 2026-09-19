from __future__ import annotations

import argparse
import sys
import time
from types import SimpleNamespace

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



def _interactive_terminal() -> bool:
    return bool(
        getattr(sys.stdin, "isatty", lambda: False)()
        and getattr(sys.stdout, "isatty", lambda: False)()
    )


def _menu_status() -> tuple[str, str, str]:
    try:
        configured = setup_is_complete()
    except Exception:
        configured = False

    try:
        cfg = load_config()
    except Exception:
        cfg = None

    try:
        state = RuntimeStateStore().refresh()
    except Exception:
        state = None

    setup_label = "configured" if configured else "not configured"
    if state is None:
        protection_label = "unknown"
    else:
        protection_label = "armed" if state.armed else "disarmed"

    if not configured:
        provider_label = "not configured"
    elif cfg is None:
        provider_label = "unknown"
    elif cfg.bot.provider == "local":
        provider_label = "Local — local only"
    else:
        connected = bool(state and state.bot_online)
        provider_label = f"{cfg.bot.provider.title()} — {'connected' if connected else 'offline'}"

    return setup_label, protection_label, provider_label


def _render_main_menu() -> None:
    setup_label, protection_label, provider_label = _menu_status()
    console.print()
    console.rule("[bold cyan]Laptop Guard[/bold cyan]")
    console.print(
        f"Setup: [bold]{setup_label}[/bold]  |  "
        f"Protection: [bold]{protection_label}[/bold]  |  "
        f"Provider: [bold]{provider_label}[/bold]"
    )
    console.print()
    console.print("  1. Setup / reconfigure")
    console.print("  2. Start Guard")
    console.print("  3. Arm protection")
    console.print("  4. Disarm protection")
    console.print("  5. Status")
    console.print("  6. Test hardware")
    console.print("  7. Doctor")
    console.print("  8. Autostart")
    console.print("  9. View events")
    console.print("  0. Exit")


def _read_menu_choice(prompt: str, valid: set[str]) -> str | None:
    while True:
        try:
            value = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            return None
        if value in valid:
            return value
        console.print(
            "[yellow]Invalid choice. Enter one of: "
            + ", ".join(sorted(valid))
            + ".[/yellow]"
        )


def _confirm_menu(prompt: str, *, default: bool = False) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        try:
            value = input(prompt + suffix).strip().lower()
        except (EOFError, KeyboardInterrupt):
            console.print()
            return False
        if not value:
            return default
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        console.print("[yellow]Please answer yes or no.[/yellow]")


def _run_menu_action(label: str, action) -> int:
    try:
        result = action()
    except Exception:
        console.print(f"[red]{label} could not complete safely.[/red]")
        console.print("Use Doctor from the menu for recovery guidance.")
        return 2

    code = result if isinstance(result, int) else 0
    if code != 0:
        console.print(
            f"[yellow]{label} finished with a problem. "
            "Use Doctor for the recommended next step.[/yellow]"
        )
    return code


def _hardware_menu() -> None:
    targets = {
        "1": ("Camera", "camera"),
        "2": ("Microphone", "microphone"),
        "3": ("Bot / provider", "bot"),
        "4": ("Screen lock", "lock"),
        "5": ("Screen capture", "screen"),
        "6": ("Keyboard / mouse input", "input"),
    }
    console.print("\n[bold]Hardware tests[/bold]")
    for key, (label, _target) in targets.items():
        console.print(f"  {key}. {label}")
    console.print("  0. Back")

    choice = _read_menu_choice("Choose a hardware test: ", set(targets) | {"0"})
    if choice in {None, "0"}:
        return

    label, target = targets[choice]
    if target == "lock" and not _confirm_menu(
        "The lock test may lock your desktop session. Continue?"
    ):
        console.print("Lock test cancelled.")
        return

    _run_menu_action(
        f"{label} test",
        lambda: cmd_test(SimpleNamespace(target=target)),
    )


def _autostart_menu() -> None:
    console.print("\n[bold]Autostart[/bold]")
    console.print("  1. Show status")
    console.print("  2. Turn on")
    console.print("  3. Turn off")
    console.print("  0. Back")

    choice = _read_menu_choice("Choose an autostart action: ", {"0", "1", "2", "3"})
    if choice in {None, "0"}:
        return
    if choice == "1":
        _run_menu_action(
            "Autostart status",
            lambda: cmd_autostart(SimpleNamespace(action="status")),
        )
        return
    if choice == "2":
        _run_menu_action(
            "Enable autostart",
            lambda: cmd_autostart(SimpleNamespace(action="on")),
        )
        return

    if not _confirm_menu(
        "Turning autostart off means Laptop Guard will not start automatically. Continue?"
    ):
        console.print("Autostart change cancelled.")
        return
    _run_menu_action(
        "Disable autostart",
        lambda: cmd_autostart(SimpleNamespace(action="off")),
    )


def run_main_menu() -> int:
    while True:
        _render_main_menu()
        choice = _read_menu_choice(
            "Choose an action: ",
            {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"},
        )
        if choice in {None, "0"}:
            console.print("Goodbye.")
            return 0

        if choice == "1":
            _run_menu_action("Setup", lambda: cmd_setup(None))
        elif choice == "2":
            _run_menu_action("Guard", lambda: cmd_run(None))
        elif choice == "3":
            _run_menu_action("Arm", lambda: cmd_arm(None))
        elif choice == "4":
            if _confirm_menu("Disarm protection?"):
                _run_menu_action("Disarm", lambda: cmd_disarm(None))
            else:
                console.print("Disarm cancelled.")
        elif choice == "5":
            _run_menu_action("Status", lambda: cmd_status(None))
        elif choice == "6":
            _hardware_menu()
        elif choice == "7":
            _run_menu_action("Doctor", lambda: cmd_doctor(None))
        elif choice == "8":
            _autostart_menu()
        elif choice == "9":
            _run_menu_action(
                "Events",
                lambda: cmd_events(SimpleNamespace(limit=20)),
            )


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
    parser = build_parser()
    args = parser.parse_args()
    try:
        if not getattr(args, "command", None):
            if _interactive_terminal():
                return run_main_menu()
            return cmd_run(args)
        result = args.func(args)
        return result if isinstance(result, int) else 0
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
        return 130
