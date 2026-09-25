from laptop_guard import cli


def test_lock_command_reports_failure(monkeypatch):
    monkeypatch.setattr(cli, "lock_screen", lambda: False)
    assert cli.cmd_lock(None) == 2


def test_lock_command_reports_success(monkeypatch):
    monkeypatch.setattr(cli, "lock_screen", lambda: True)
    assert cli.cmd_lock(None) == 0


def test_menu_status_shows_setup_arm_and_provider_state(monkeypatch):
    from types import SimpleNamespace

    cfg = SimpleNamespace(bot=SimpleNamespace(provider="bale"))
    state = SimpleNamespace(armed=True, bot_online=True)

    monkeypatch.setattr(cli, "setup_is_complete", lambda: True)
    monkeypatch.setattr(cli, "load_config", lambda: cfg)
    monkeypatch.setattr(
        cli,
        "RuntimeStateStore",
        lambda: SimpleNamespace(refresh=lambda: state),
    )

    assert cli._menu_status() == ("configured", "armed", "Bale — connected")


def test_interactive_no_argument_launch_uses_menu(monkeypatch):
    monkeypatch.setattr(cli.sys, "argv", ["laptop-guard"])
    monkeypatch.setattr(cli, "_interactive_terminal", lambda: True)
    monkeypatch.setattr(cli, "run_main_menu", lambda: 17)
    monkeypatch.setattr(
        cli,
        "cmd_run",
        lambda _args: (_ for _ in ()).throw(AssertionError("guard should not start")),
    )

    assert cli.main() == 17


def test_noninteractive_no_argument_launch_preserves_direct_run(monkeypatch):
    monkeypatch.setattr(cli.sys, "argv", ["laptop-guard"])
    monkeypatch.setattr(cli, "_interactive_terminal", lambda: False)
    monkeypatch.setattr(cli, "cmd_run", lambda _args: 23)

    assert cli.main() == 23


def test_explicit_cli_subcommand_remains_backward_compatible(monkeypatch):
    called = []
    monkeypatch.setattr(cli.sys, "argv", ["laptop-guard", "status"])
    monkeypatch.setattr(cli, "cmd_status", lambda _args: called.append("status") or 0)

    assert cli.main() == 0
    assert called == ["status"]


def test_menu_retries_invalid_input_and_exits_cleanly(monkeypatch):
    answers = iter(["not-a-choice", "0"])
    monkeypatch.setattr(cli, "_render_main_menu", lambda: None)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))

    assert cli.run_main_menu() == 0


def test_menu_disarm_requires_confirmation(monkeypatch):
    answers = iter(["4", "n", "0"])
    called = []
    monkeypatch.setattr(cli, "_render_main_menu", lambda: None)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    monkeypatch.setattr(cli, "cmd_disarm", lambda _args: called.append("disarm") or 0)

    assert cli.run_main_menu() == 0
    assert called == []


def test_menu_returns_after_status_action(monkeypatch):
    answers = iter(["5", "0"])
    called = []
    monkeypatch.setattr(cli, "_render_main_menu", lambda: None)
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    monkeypatch.setattr(cli, "cmd_status", lambda _args: called.append("status") or 0)

    assert cli.run_main_menu() == 0
    assert called == ["status"]



def test_all_cli_subcommands_parse_to_callable_handlers():
    parser = cli.build_parser()
    commands = [
        ["setup"],
        ["reconfigure", "camera"],
        ["run"],
        ["doctor"],
        ["arm"],
        ["disarm"],
        ["status"],
        ["config"],
        ["lock"],
        ["profile", "away"],
        ["events", "--limit", "5"],
        ["health"],
        ["test", "camera"],
        ["service", "status"],
        ["service", "start"],
        ["service", "stop"],
        ["autostart", "status"],
        ["desktop-setup", "--device-name", "Linux Desktop", "--consent"],
        ["desktop-status"],
    ]

    for argv in commands:
        args = parser.parse_args(argv)
        assert args.command == argv[0]
        assert callable(args.func)
