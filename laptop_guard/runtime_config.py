from __future__ import annotations

import getpass
import sys
from typing import Any

from rich.console import Console
from rich.prompt import Confirm, IntPrompt

from .config import (
    CONFIG_PATH,
    default_api_base,
    get_bot_token,
    import_legacy_env_secrets,
    load_config,
    save_config,
    set_bot_token,
    setup_is_complete,
)
from .models import AppConfig
from .providers import build_provider
from .runtime_recovery import is_provider_auth_error, write_runtime_diagnostic


class RuntimeConfigurationError(RuntimeError):
    pass


def _interactive() -> bool:
    return bool(getattr(sys.stdin, "isatty", lambda: False)())


def _auth_error(exc: BaseException) -> bool:
    return is_provider_auth_error(exc)


def _provider_name(cfg: AppConfig) -> str:
    provider = str(cfg.bot.provider or "bale").strip().lower()
    return provider if provider in {"telegram", "bale", "local"} else "bale"


def _provider(cfg: AppConfig, token: str):
    provider_name = _provider_name(cfg)
    api_base = cfg.bot.api_base.strip() or default_api_base(provider_name)
    cfg.bot.api_base = api_base
    return build_provider(provider_name, token, api_base, cfg.bot.proxy)


def _ask_valid_token(cfg: AppConfig, console: Console, *, force_new: bool = False) -> tuple[str, dict[str, Any]]:
    provider_name = _provider_name(cfg)
    if provider_name == "local":
        return "", {}

    stored = "" if force_new else get_bot_token()
    attempted_stored = False

    while True:
        token = stored
        if token:
            attempted_stored = True
        else:
            if not _interactive():
                raise RuntimeConfigurationError(
                    f"{provider_name.title()} bot token is required, but no interactive terminal is available. "
                    "Run './run.sh setup' once from a terminal."
                )
            token = getpass.getpass(f"{provider_name.title()} bot token: ").strip()

        if not token:
            console.print("[red]A bot token is required.[/red]")
            stored = ""
            continue

        bot = _provider(cfg, token)
        if bot is None:
            raise RuntimeConfigurationError(f"Unsupported provider: {provider_name}")

        try:
            console.print(f"Testing {provider_name.title()} bot credentials...")
            me = bot.get_me()
        except Exception as exc:
            diagnostic = write_runtime_diagnostic("provider-credential-validation", exc)
            if not _interactive():
                if _auth_error(exc):
                    raise RuntimeConfigurationError(
                        f"{provider_name.title()} bot credential was rejected. "
                        "Run './run.sh reconfigure provider', then './run.sh test bot'."
                    ) from exc
                raise RuntimeConfigurationError(
                    f"Could not reach the {provider_name.title()} bot service. "
                    "Check network/proxy settings, then run './run.sh test bot'."
                ) from exc
            if _auth_error(exc):
                console.print("[red]The saved bot credential was rejected.[/red]")
                console.print(
                    "Run the Provider section with the current token. "
                    "The old credential is replaced only after validation."
                )
            else:
                console.print(
                    f"[red]Could not reach the {provider_name.title()} bot service.[/red]"
                )
                console.print("Check network/proxy settings or run ./run.sh test bot.")
                if attempted_stored and Confirm.ask(
                    "Keep the stored credential and retry it?",
                    default=False,
                ):
                    stored = token
                    attempted_stored = False
                    continue
            if diagnostic is not None:
                console.print(f"[dim]Diagnostic details: {diagnostic}[/dim]")
            stored = ""
            attempted_stored = False
            continue

        set_bot_token(token)
        save_config(cfg)
        return token, me if isinstance(me, dict) else {}


def _pair_owner_chat(cfg: AppConfig, token: str, console: Console) -> None:
    if cfg.bot.provider == "local":
        cfg.bot.chat_id = None
        save_config(cfg)
        return
    if cfg.bot.chat_id is not None:
        return
    if not _interactive():
        raise RuntimeConfigurationError(
            "Owner chat ID is missing, but no interactive terminal is available. Run './run.sh setup' from a terminal."
        )

    bot = _provider(cfg, token)
    if bot is None:
        raise RuntimeConfigurationError(f"Unsupported provider: {cfg.bot.provider}")

    console.print("\n[yellow]No owner chat is configured.[/yellow]")
    try:
        if Confirm.ask("Pair it automatically by waiting for a new /start message?", default=True):
            from .setup_wizard import pair_chat

            cfg.bot.chat_id = pair_chat(bot, console)
        else:
            cfg.bot.chat_id = IntPrompt.ask("Owner chat ID")
    except Exception as exc:
        write_runtime_diagnostic("owner-pairing", exc)
        raise RuntimeConfigurationError(
            "Owner pairing did not complete. Run './run.sh reconfigure owner' and try again."
        ) from exc

    save_config(cfg)
    console.print(f"[green]Owner chat saved:[/green] {cfg.bot.chat_id}")


def ensure_runtime_configuration(console: Console | None = None) -> AppConfig:
    """Return a usable configuration, prompting only when something required is missing/broken.

    Normal settings are stored in ~/.config/laptop-guard/config.toml.
    Tokens are stored separately in ~/.config/laptop-guard/secrets.json (0600).
    No .env file is required.
    """
    console = console or Console()

    if not setup_is_complete():
        if not _interactive():
            raise RuntimeConfigurationError(
                "Laptop Guard setup is incomplete and cannot prompt without a terminal. Run './run.sh setup'."
            )
        from .setup_wizard import run_setup

        if CONFIG_PATH.exists():
            console.print("[yellow]Configuration is incomplete. Resuming setup.[/yellow]")
        else:
            console.print("[yellow]First run: starting interactive setup.[/yellow]")
        cfg = run_setup()
        if not cfg.setup_complete:
            raise RuntimeConfigurationError("Setup was not completed.")
    else:
        cfg = load_config()

    if cfg.bot.provider == "local":
        return cfg

    # Optional one-time compatibility with an already-exported old environment.
    # run.sh itself no longer loads .env.
    import_legacy_env_secrets()

    token, me = _ask_valid_token(cfg, console)
    label = me.get("username") or me.get("first_name") or me.get("id")
    if label:
        console.print(f"[green]Bot authenticated:[/green] {label}")

    _pair_owner_chat(cfg, token, console)
    return cfg


def repair_runtime_token(cfg: AppConfig, console: Console | None = None) -> str:
    """Prompt for a replacement token after an authentication failure."""
    console = console or Console()
    if not _interactive():
        raise RuntimeConfigurationError(
            "Bot authentication failed and the process has no interactive terminal. Run './run.sh' manually to replace the token."
        )
    token, _ = _ask_valid_token(cfg, console, force_new=True)
    return token
