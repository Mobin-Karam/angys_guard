from __future__ import annotations

import json
import os
import tomllib
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any

from .models import AppConfig

APP_NAME = "laptop-guard"
APP_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_NAME
CONFIG_DIR = APP_DIR  # backwards-compatible name
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_NAME
MEDIA_DIR = DATA_DIR / "media"
LOG_DIR = DATA_DIR / "logs"
STATE_PATH = DATA_DIR / "state.json"
EVENT_DB_PATH = DATA_DIR / "events.sqlite3"
CONFIG_PATH = APP_DIR / "config.toml"
SECRETS_PATH = APP_DIR / "secrets.json"


def ensure_dirs() -> None:
    for path in (APP_DIR, DATA_DIR, MEDIA_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)
    try:
        APP_DIR.chmod(0o700)
    except OSError:
        pass


ensure_dirs()


def default_api_base(provider: str) -> str:
    provider = str(provider or "").strip().lower()
    if provider == "telegram":
        return "https://api.telegram.org"
    if provider == "bale":
        return "https://tapi.bale.ai"
    return ""


def _read_secrets() -> dict[str, str]:
    if not SECRETS_PATH.exists():
        return {}
    try:
        data = json.loads(SECRETS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items() if v is not None}


def _write_secrets(data: dict[str, str]) -> None:
    ensure_dirs()
    tmp = SECRETS_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        tmp.chmod(0o600)
    except OSError:
        pass
    tmp.replace(SECRETS_PATH)
    try:
        SECRETS_PATH.chmod(0o600)
    except OSError:
        pass


def get_bot_token() -> str:
    return _read_secrets().get("bot_token", "").strip()


def set_bot_token(token: str) -> None:
    data = _read_secrets()
    clean = str(token or "").strip()
    if clean:
        data["bot_token"] = clean
    else:
        data.pop("bot_token", None)
    _write_secrets(data)


def get_api_token() -> str:
    return _read_secrets().get("api_token", "").strip()


def set_api_token(token: str) -> None:
    data = _read_secrets()
    clean = str(token or "").strip()
    if clean:
        data["api_token"] = clean
    else:
        data.pop("api_token", None)
    _write_secrets(data)


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if value is None:
        # TOML has no null. None-valued keys are omitted by the writer.
        raise TypeError("None has no TOML scalar representation")
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
    raise TypeError(f"Unsupported TOML value: {type(value).__name__}")


def _section_dict(obj: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for f in fields(obj):
        value = getattr(obj, f.name)
        if is_dataclass(value):
            continue
        if value is None:
            continue
        result[f.name] = value
    return result


def save_config(cfg: AppConfig) -> None:
    """Persist non-secret configuration to config.toml.

    Bot/API secrets deliberately live in mode-0600 secrets.json and are never
    written to config.toml or required in .env.
    """
    ensure_dirs()
    cfg.chat.normalize()
    cfg.tts.normalize()

    lines: list[str] = []
    lines.append("# Laptop Guard configuration (non-secret)\n")
    lines.append("[app]")
    lines.append(f"setup_complete = {_toml_value(bool(cfg.setup_complete))}")
    lines.append(f"profile = {_toml_value(str(cfg.profile))}")
    lines.append(f"device_name = {_toml_value(str(cfg.device_name))}")
    lines.append("")

    for name in (
        "bot", "camera", "audio", "security", "communication", "chat", "tts",
        "screen", "apps", "api", "health", "monitors", "startup",
    ):
        section = getattr(cfg, name)
        lines.append(f"[{name}]")
        for key, value in _section_dict(section).items():
            lines.append(f"{key} = {_toml_value(value)}")
        lines.append("")

    tmp = CONFIG_PATH.with_suffix(".toml.tmp")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    try:
        tmp.chmod(0o600)
    except OSError:
        pass
    tmp.replace(CONFIG_PATH)
    try:
        CONFIG_PATH.chmod(0o600)
    except OSError:
        pass


def _coerce_like(current: Any, value: Any) -> Any:
    if current is None:
        return value
    if isinstance(current, bool):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
            return current
        if isinstance(value, (int, float)):
            return bool(value)
        return current
    if isinstance(current, int) and not isinstance(current, bool):
        try:
            return int(value)
        except (TypeError, ValueError):
            return current
    if isinstance(current, float):
        try:
            return float(value)
        except (TypeError, ValueError):
            return current
    if isinstance(current, str):
        return str(value)
    if isinstance(current, list):
        return list(value) if isinstance(value, list) else current
    return value


def _apply_section(obj: Any, data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        return
    known = {f.name for f in fields(obj)}
    for key, value in data.items():
        if key not in known:
            continue
        current = getattr(obj, key)
        setattr(obj, key, _coerce_like(current, value))


def _apply_legacy_env(cfg: AppConfig) -> None:
    """One-way compatibility for users launching with exported old variables.

    The application no longer requires .env. These are only read when no saved
    config exists, allowing an old installation to migrate without data loss.
    Tokens are never copied unless save_legacy_env_secrets() is explicitly used.
    """
    mapping: list[tuple[str, Any, str]] = [
        ("AUTO_ARM", cfg.security, "auto_arm"),
        ("ARM_DELAY", cfg.security, "arm_delay"),
        ("WARNING_SECONDS", cfg.security, "warning_seconds"),
        ("INPUT_COOLDOWN", cfg.security, "input_cooldown"),
        ("MOUSE_MOVE_THRESHOLD", cfg.security, "mouse_move_threshold"),
        ("LOCK_AFTER_WARNING", cfg.security, "lock_after_countdown"),
        ("CAMERA_SNAPSHOT_ON_INPUT", cfg.security, "input_snapshot"),
        ("SCREEN_SNAPSHOT_ON_INPUT", cfg.security, "input_screen_snapshot"),
        ("WARNING_VIDEO", cfg.security, "warning_video"),
        ("LOCK_ON_GUARD_EXIT", cfg.security, "lock_on_guard_exit"),
        ("STOP_AUTH_ENABLED", cfg.security, "stop_auth_enabled"),
        ("STOP_PIN_TIMEOUT", cfg.security, "stop_pin_timeout"),
        ("STOP_OWNER_CONFIRM_TIMEOUT", cfg.security, "stop_owner_confirm_timeout"),
        ("LOCK_ON_STOP_AUTH_FAILURE", cfg.security, "lock_on_stop_auth_failure"),
        ("ALLOW_REMOTE_UNLOCK", cfg.security, "allow_remote_unlock"),
        ("ALLOW_REMOTE_POWER", cfg.security, "allow_remote_power"),
        ("CAMERA_INDEX", cfg.camera, "index"),
        ("CAMERA_FPS", cfg.camera, "fps"),
        ("MOTION_ENABLED", cfg.camera, "enabled"),
        ("MOTION_MIN_AREA", cfg.camera, "motion_min_area"),
        ("MOTION_COOLDOWN", cfg.camera, "motion_cooldown"),
        ("AUTO_PLAY_OWNER_VOICE", cfg.audio, "play_remote_voice"),
        ("INTERCOM_CHUNK_SECONDS", cfg.audio, "intercom_chunk_seconds"),
        ("INTERCOM_MAX_SECONDS", cfg.audio, "max_seconds"),
        ("LISTEN_DEFAULT_SECONDS", cfg.audio, "listen_default_seconds"),
        ("PERSIAN_TTS_ENABLED", cfg.tts, "enabled"),
        ("PERSIAN_TTS_VOICE", cfg.tts, "voice"),
        ("PERSIAN_TTS_RATE_LIMIT", cfg.tts, "rate_limit"),
        ("PERSIAN_TTS_MAX_CHARS", cfg.tts, "max_chars"),
        ("PERSIAN_TTS_NOTIFY", cfg.tts, "show_notification"),
        ("PERSIAN_TTS_MIRROR_CHAT", cfg.tts, "mirror_to_chat"),
        ("CHAT_DIRECTION", cfg.chat, "direction"),
        ("CHAT_SECONDS", cfg.chat, "seconds"),
        ("CHAT_ALLOW_REPLY", cfg.chat, "allow_reply"),
    ]
    for env_name, obj, attr in mapping:
        raw = os.environ.get(env_name)
        if raw is None:
            continue
        current = getattr(obj, attr)
        if isinstance(current, bool):
            value: Any = raw.strip().lower() in {"1", "true", "yes", "on"}
        elif isinstance(current, int) and not isinstance(current, bool):
            try:
                value = int(raw)
            except ValueError:
                continue
        elif isinstance(current, float):
            try:
                value = float(raw)
            except ValueError:
                continue
        else:
            value = raw.strip()
        setattr(obj, attr, value)

    raw_chat_id = os.environ.get("BALE_CHAT_ID", "").strip()
    if raw_chat_id:
        try:
            cfg.bot.chat_id = int(raw_chat_id)
        except ValueError:
            pass
    api_base = os.environ.get("BALE_API_BASE", "").strip()
    if api_base:
        cfg.bot.provider = "bale"
        cfg.bot.api_base = api_base.rstrip("/")


def import_legacy_env_secrets() -> bool:
    """Import an already-exported legacy bot token into secrets.json once."""
    if get_bot_token():
        return False
    token = os.environ.get("BALE_BOT_TOKEN", "").strip()
    if not token:
        return False
    set_bot_token(token)
    return True


def _migrate(cfg: AppConfig, raw: dict[str, Any]) -> AppConfig:
    # Historical v6 safety migration: the old warning-only/20-second defaults
    # became the fixed five-second warning+lock behavior.
    security_raw = raw.get("security") if isinstance(raw, dict) else None
    if isinstance(security_raw, dict):
        # v3.3 used lock_on_input=true for an immediate lock. Migrate it to
        # the visible warning/countdown lock flow instead.
        if security_raw.get("lock_on_input") is True:
            cfg.security.input_action = "warning_lock"
            cfg.security.lock_on_input = False
            cfg.security.lock_after_countdown = True
            cfg.security.warning_seconds = 5
        if security_raw.get("input_action") == "warning" and cfg.security.warning_seconds == 20:
            cfg.security.input_action = "warning_lock"
            cfg.security.warning_seconds = 5
            cfg.security.lock_after_countdown = True

    if cfg.communication.surface == "text_editor":
        cfg.communication.surface = "live_notepad"
        cfg.communication.open_text_editor_mirror = False

    # Keep the old chat settings synchronized with the newer communication
    # section when a config only contains one side.
    if not (isinstance(raw, dict) and isinstance(raw.get("chat"), dict)):
        cfg.chat.seconds = max(15, min(int(cfg.communication.chat_seconds), 3600))
        cfg.chat.allow_reply = bool(cfg.communication.allow_visitor_reply)

    cfg.chat.normalize()
    cfg.tts.normalize()
    return cfg


def load_config() -> AppConfig:
    cfg = AppConfig()
    if not CONFIG_PATH.exists():
        _apply_legacy_env(cfg)
        cfg.chat.normalize()
        cfg.tts.normalize()
        return cfg

    try:
        raw = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return cfg

    app = raw.get("app", {}) if isinstance(raw, dict) else {}
    if isinstance(app, dict):
        if "setup_complete" in app:
            cfg.setup_complete = bool(app["setup_complete"])
        if "profile" in app:
            cfg.profile = str(app["profile"])  # type: ignore[assignment]
        if "device_name" in app:
            cfg.device_name = str(app["device_name"])

    for name in (
        "bot", "camera", "audio", "security", "communication", "chat", "tts",
        "screen", "apps", "api", "health", "monitors", "startup",
    ):
        section_data = raw.get(name, {}) if isinstance(raw, dict) else {}
        _apply_section(getattr(cfg, name), section_data)

    return _migrate(cfg, raw)


def setup_is_complete() -> bool:
    return CONFIG_PATH.exists() and bool(load_config().setup_complete)


__all__ = [
    "APP_NAME", "APP_DIR", "CONFIG_DIR", "DATA_DIR", "MEDIA_DIR", "LOG_DIR",
    "STATE_PATH", "EVENT_DB_PATH", "CONFIG_PATH", "SECRETS_PATH", "AppConfig",
    "ensure_dirs", "default_api_base", "load_config", "save_config",
    "setup_is_complete", "get_bot_token", "set_bot_token", "get_api_token",
    "set_api_token", "import_legacy_env_secrets",
]
