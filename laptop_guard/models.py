from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ProviderName = Literal["telegram", "bale", "local"]
DetectionMode = Literal["motion", "motion_person"]
InputAction = Literal["warning", "notify", "lock", "warning_lock"]
ProfileName = Literal["away", "home", "night", "testing", "custom"]
ChatSurfaceMode = Literal["guard_chat", "live_notepad", "both", "fullscreen", "text_editor"]


@dataclass
class BotConfig:
    provider: ProviderName = "telegram"
    api_base: str = "https://api.telegram.org"
    chat_id: int | None = None
    proxy: str = ""
    poll_timeout: int = 25
    language: str = "fa"


@dataclass
class CameraConfig:
    index: int = 0
    enabled: bool = True
    fps: float = 6.0
    analysis_width: int = 640
    motion_min_area: int = 2200
    motion_confirm_frames: int = 2
    motion_cooldown: float = 20.0
    mode: DetectionMode = "motion"
    event_clip_seconds: int = 10
    pre_event_seconds: int = 5
    tamper_enabled: bool = True
    tamper_black_brightness: float = 7.0
    tamper_frozen_seconds: float = 10.0
    tamper_cooldown: float = 90.0


@dataclass
class AudioConfig:
    backend: str = "auto"
    input: str = "default"
    max_seconds: int = 300
    local_notification: bool = True
    play_remote_voice: bool = True
    max_remote_file_mb: int = 20
    tts_enabled: bool = True
    max_tts_chars: int = 300


@dataclass
class SecurityConfig:
    auto_arm: bool = False
    arm_delay: float = 3.0
    input_cooldown: float = 30.0
    mouse_move_threshold: float = 35.0
    input_action: InputAction = "warning_lock"
    warning_seconds: int = 5
    lock_after_countdown: bool = True
    input_screen_snapshot: bool = True
    input_screen_video_seconds: int = 5
    intrusion_photo_background: bool = True
    warning_text: str = "به لپ‌تاپ من دست نزن!\nمن می‌توانم تو را ببینم."
    input_snapshot: bool = True
    lock_on_input: bool = False
    allow_remote_unlock: bool = False
    warning_attempt_window: int = 120
    warning_sound: bool = True
    escalation_attempts: int = 0
    escalation_action: InputAction = "notify"
    input_backend: str = "auto"  # auto|evdev|pynput


@dataclass
class CommunicationConfig:
    # "both" means Guard Chat + built-in live-notepad tab. It no longer
    # launches an external editor that prompts when the mirror file changes.
    surface: ChatSurfaceMode = "both"
    chat_seconds: int = 45
    allow_visitor_reply: bool = True
    open_text_editor_mirror: bool = False
    open_on_intrusion: bool = True
    mirror_filename: str = "security-chat.txt"


@dataclass
class ScreenConfig:
    screenshots_enabled: bool = True
    screen_video_enabled: bool = True
    notify_local_capture: bool = True
    max_video_seconds: int = 30
    max_burst_seconds: int = 60
    burst_interval_seconds: int = 3


@dataclass
class AppsConfig:
    enabled: bool = True
    allow_launch: bool = True
    allow_close: bool = True
    max_list_items: int = 12
    # A small conservative default. Users can add more .desktop IDs in config.
    allowlist: list[str] = field(default_factory=lambda: [
        "org.gnome.TextEditor.desktop",
        "org.gnome.Nautilus.desktop",
        "firefox.desktop",
        "firefox_firefox.desktop",
        "code.desktop",
        "code_code.desktop",
    ])


@dataclass
class ApiConfig:
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8765
    max_upload_mb: int = 20


@dataclass
class HealthConfig:
    enabled: bool = True
    interval_seconds: int = 30
    notify_changes: bool = True
    low_battery_percent: int = 20
    critical_battery_percent: int = 8
    min_free_disk_gb: float = 2.0
    temperature_warn_c: float = 85.0


@dataclass
class MonitorConfig:
    usb_events: bool = True
    power_events: bool = True
    health_events: bool = True
    offline_queue: bool = True


@dataclass
class AppConfig:
    setup_complete: bool = False
    profile: ProfileName = "away"
    device_name: str = "Laptop"
    bot: BotConfig = field(default_factory=BotConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    communication: CommunicationConfig = field(default_factory=CommunicationConfig)
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    apps: AppsConfig = field(default_factory=AppsConfig)
    api: ApiConfig = field(default_factory=ApiConfig)
    health: HealthConfig = field(default_factory=HealthConfig)
    monitors: MonitorConfig = field(default_factory=MonitorConfig)
