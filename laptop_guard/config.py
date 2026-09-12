from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

APP_NAME = "laptop-guard"
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / APP_NAME
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / APP_NAME
MEDIA_DIR = DATA_DIR / "media"
LOG_DIR = DATA_DIR / "logs"

for _path in (CONFIG_DIR, DATA_DIR, MEDIA_DIR, LOG_DIR):
    _path.mkdir(parents=True, exist_ok=True)


def env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(maximum, value))


def env_float(name: str, default: float, minimum: float, maximum: float) -> float:
    try:
        value = float(os.environ.get(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(maximum, value))


@dataclass(slots=True)
class BaleConfig:
    token: str = field(default_factory=lambda: os.environ.get("BALE_BOT_TOKEN", "").strip())
    chat_id: int | None = None
    api_base: str = field(default_factory=lambda: os.environ.get("BALE_API_BASE", "https://tapi.bale.ai").rstrip("/"))
    poll_timeout: int = field(default_factory=lambda: env_int("BALE_POLL_TIMEOUT", 25, 5, 50))

    def __post_init__(self) -> None:
        raw = os.environ.get("BALE_CHAT_ID", "").strip()
        if raw:
            try:
                self.chat_id = int(raw)
            except ValueError as exc:
                raise ValueError("BALE_CHAT_ID must be an integer") from exc


@dataclass(slots=True)
class SecurityConfig:
    auto_arm: bool = field(default_factory=lambda: env_bool("AUTO_ARM", False))
    arm_delay: int = field(default_factory=lambda: env_int("ARM_DELAY", 3, 0, 60))
    warning_seconds: int = field(default_factory=lambda: env_int("WARNING_SECONDS", 5, 3, 15))
    input_cooldown: int = field(default_factory=lambda: env_int("INPUT_COOLDOWN", 25, 3, 600))
    mouse_move_threshold: int = field(default_factory=lambda: env_int("MOUSE_MOVE_THRESHOLD", 35, 5, 300))
    camera_snapshot_on_input: bool = field(default_factory=lambda: env_bool("CAMERA_SNAPSHOT_ON_INPUT", True))
    screen_snapshot_on_input: bool = field(default_factory=lambda: env_bool("SCREEN_SNAPSHOT_ON_INPUT", True))
    lock_after_warning: bool = field(default_factory=lambda: env_bool("LOCK_AFTER_WARNING", True))
    warning_images: bool = field(default_factory=lambda: env_bool("WARNING_IMAGES", True))
    lock_on_guard_exit: bool = field(default_factory=lambda: env_bool("LOCK_ON_GUARD_EXIT", True))
    allow_remote_unlock: bool = field(default_factory=lambda: env_bool("ALLOW_REMOTE_UNLOCK", False))
    allow_remote_power: bool = field(default_factory=lambda: env_bool("ALLOW_REMOTE_POWER", False))


@dataclass(slots=True)
class CameraConfig:
    index: int = field(default_factory=lambda: env_int("CAMERA_INDEX", 0, 0, 16))
    fps: int = field(default_factory=lambda: env_int("CAMERA_FPS", 6, 1, 20))
    motion_min_area: int = field(default_factory=lambda: env_int("MOTION_MIN_AREA", 2200, 200, 100000))
    motion_cooldown: int = field(default_factory=lambda: env_int("MOTION_COOLDOWN", 30, 3, 3600))
    motion_enabled: bool = field(default_factory=lambda: env_bool("MOTION_ENABLED", True))


@dataclass(slots=True)
class ChatConfig:
    seconds: int = field(default_factory=lambda: env_int("CHAT_SECONDS", 120, 15, 3600))
    allow_reply: bool = field(default_factory=lambda: env_bool("CHAT_ALLOW_REPLY", True))
    direction: str = field(default_factory=lambda: os.environ.get("CHAT_DIRECTION", "auto").strip().lower())

    def __post_init__(self) -> None:
        if self.direction not in {"auto", "rtl", "ltr"}:
            self.direction = "auto"


@dataclass(slots=True)
class AudioConfig:
    auto_play_owner_voice: bool = field(default_factory=lambda: env_bool("AUTO_PLAY_OWNER_VOICE", True))
    intercom_chunk_seconds: int = field(default_factory=lambda: env_int("INTERCOM_CHUNK_SECONDS", 4, 2, 10))
    intercom_max_seconds: int = field(default_factory=lambda: env_int("INTERCOM_MAX_SECONDS", 90, 10, 300))
    listen_default_seconds: int = field(default_factory=lambda: env_int("LISTEN_DEFAULT_SECONDS", 8, 2, 30))




@dataclass(slots=True)
class TTSConfig:
    enabled: bool = field(default_factory=lambda: env_bool("PERSIAN_TTS_ENABLED", True))
    voice: str = field(default_factory=lambda: os.environ.get("PERSIAN_TTS_VOICE", "man2").strip().lower())
    rate_limit: float = field(default_factory=lambda: env_float("PERSIAN_TTS_RATE_LIMIT", 0.5, 0.0, 10.0))
    max_chars: int = field(default_factory=lambda: env_int("PERSIAN_TTS_MAX_CHARS", 700, 20, 2000))
    show_notification: bool = field(default_factory=lambda: env_bool("PERSIAN_TTS_NOTIFY", True))
    mirror_to_chat: bool = field(default_factory=lambda: env_bool("PERSIAN_TTS_MIRROR_CHAT", False))

    def __post_init__(self) -> None:
        allowed = {
            "woman1", "woman2", "woman3", "woman4",
            "man1", "man2", "man3", "man4", "man5", "man6", "man7", "man8",
            "boy1",
        }
        if self.voice not in allowed:
            self.voice = "man2"


@dataclass(slots=True)
class AppConfig:
    bale: BaleConfig = field(default_factory=BaleConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    chat: ChatConfig = field(default_factory=ChatConfig)


def load_config() -> AppConfig:
    return AppConfig()
