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
    # Bale is the primary channel in the current Guard runtime.
    provider: ProviderName = "bale"
    api_base: str = "https://tapi.bale.ai"
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

    # Compatibility with the v8-v11 Bale Guard runtime.
    @property
    def motion_enabled(self) -> bool:
        return self.enabled

    @motion_enabled.setter
    def motion_enabled(self, value: bool) -> None:
        self.enabled = bool(value)


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
    intercom_chunk_seconds: int = 4
    listen_default_seconds: int = 8
    sound_detection_enabled: bool = False
    sound_threshold: float = 0.08
    sound_trigger_chunks: int = 2
    sound_record_seconds: int = 8
    sound_cooldown: int = 30

    @property
    def auto_play_owner_voice(self) -> bool:
        return self.play_remote_voice

    @auto_play_owner_voice.setter
    def auto_play_owner_voice(self, value: bool) -> None:
        self.play_remote_voice = bool(value)

    @property
    def intercom_max_seconds(self) -> int:
        return self.max_seconds

    @intercom_max_seconds.setter
    def intercom_max_seconds(self, value: int) -> None:
        self.max_seconds = int(value)


@dataclass
class SecurityConfig:
    auto_arm: bool = False
    arm_delay: float = 3.0
    input_cooldown: float = 30.0
    mouse_move_threshold: float = 12.0
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
    allow_remote_power: bool = False
    warning_attempt_window: int = 120
    warning_sound: bool = True
    escalation_attempts: int = 0
    escalation_action: InputAction = "notify"
    input_backend: str = "auto"  # auto|evdev|pynput

    # v8-v11 runtime/security compatibility settings.
    warning_video: bool = True
    lock_on_guard_exit: bool = True
    stop_auth_enabled: bool = True
    stop_pin_timeout: int = 15
    stop_owner_confirm_timeout: int = 10
    lock_on_stop_auth_failure: bool = True

    @property
    def camera_snapshot_on_input(self) -> bool:
        return self.input_snapshot

    @camera_snapshot_on_input.setter
    def camera_snapshot_on_input(self, value: bool) -> None:
        self.input_snapshot = bool(value)

    @property
    def screen_snapshot_on_input(self) -> bool:
        return self.input_screen_snapshot

    @screen_snapshot_on_input.setter
    def screen_snapshot_on_input(self, value: bool) -> None:
        self.input_screen_snapshot = bool(value)

    @property
    def lock_after_warning(self) -> bool:
        return self.lock_after_countdown

    @lock_after_warning.setter
    def lock_after_warning(self, value: bool) -> None:
        self.lock_after_countdown = bool(value)


@dataclass
class CommunicationConfig:
    # "both" means Guard Chat + built-in live-notepad tab. It no longer
    # launches an external editor that prompts when the mirror file changes.
    surface: ChatSurfaceMode = "both"
    chat_seconds: int = 120
    allow_visitor_reply: bool = True
    open_text_editor_mirror: bool = False
    open_on_intrusion: bool = True
    mirror_filename: str = "security-chat.txt"


@dataclass
class ChatConfig:
    # Compatibility section used by the current full-screen security chat.
    seconds: int = 120
    allow_reply: bool = True
    direction: str = "auto"

    def normalize(self) -> None:
        if self.direction not in {"auto", "rtl", "ltr"}:
            self.direction = "auto"
        self.seconds = max(15, min(int(self.seconds), 3600))


@dataclass
class TTSConfig:
    enabled: bool = True
    voice: str = "man2"
    rate_limit: float = 0.5
    max_chars: int = 700
    show_notification: bool = True
    mirror_to_chat: bool = False

    def normalize(self) -> None:
        allowed = {
            "woman1", "woman2", "woman3", "woman4",
            "man1", "man2", "man3", "man4", "man5", "man6", "man7", "man8",
            "boy1",
        }
        if self.voice not in allowed:
            self.voice = "man2"
        self.rate_limit = max(0.0, min(float(self.rate_limit), 10.0))
        self.max_chars = max(20, min(int(self.max_chars), 2000))


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
    failed_login_events: bool = True


@dataclass
class StartupConfig:
    enabled: bool = False


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
    chat: ChatConfig = field(default_factory=ChatConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    apps: AppsConfig = field(default_factory=AppsConfig)
    api: ApiConfig = field(default_factory=ApiConfig)
    health: HealthConfig = field(default_factory=HealthConfig)
    monitors: MonitorConfig = field(default_factory=MonitorConfig)
    startup: StartupConfig = field(default_factory=StartupConfig)
