from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parent / "assets" / "warnings"
VIDEO_PATH = ASSET_DIR / "countdown.mp4"
BASE_VIDEO_SECONDS = 5.0

_player_proc: subprocess.Popen | None = None


def _notify(text: str) -> None:
    binary = shutil.which("notify-send")
    if not binary:
        return
    try:
        subprocess.Popen(
            [binary, "Laptop Guard", text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass


def _build_player_command(video: Path, seconds: int) -> tuple[str, list[str]] | None:
    seconds = max(3, min(int(seconds), 15))
    speed = BASE_VIDEO_SECONDS / float(seconds)

    # VLC is the preferred warning surface. It opens immediately in its own
    # fullscreen/on-top instance when the Guard countdown starts.
    for executable in ("vlc", "cvlc"):
        vlc = shutil.which(executable)
        if vlc:
            return "vlc", [
                vlc,
                "--no-one-instance",
                "--fullscreen",
                "--video-on-top",
                "--play-and-exit",
                "--no-video-title-show",
                "--no-osd",
                "--no-audio",
                f"--rate={speed:.6f}",
                str(video),
            ]

    mpv = shutil.which("mpv")
    if mpv:
        return "mpv", [
            mpv,
            "--fs",
            "--ontop",
            "--no-border",
            "--no-osc",
            "--no-input-default-bindings",
            "--really-quiet",
            "--audio=no",
            f"--speed={speed:.6f}",
            str(video),
        ]

    ffplay = shutil.which("ffplay")
    if ffplay:
        # setpts multiplier controls the final silent-video duration.
        multiplier = float(seconds) / BASE_VIDEO_SECONDS
        return "ffplay", [
            ffplay,
            "-fs",
            "-autoexit",
            "-loglevel",
            "quiet",
            "-an",
            "-vf",
            f"setpts={multiplier:.6f}*PTS",
            str(video),
        ]

    return None


def _notification_fallback(seconds: int) -> None:
    _notify(
        "⚠️ به لپ‌تاپ دست نزنید / Do not touch this laptop\n"
        f"System lock countdown: {seconds}s"
    )


def launch_warning(seconds: int = 5, video: Path = VIDEO_PATH) -> subprocess.Popen | None:
    """Launch the fullscreen MP4 warning and return immediately.

    The video player is only the visual surface. The main guard owns the actual
    lock deadline, so closing the player cannot cancel the lock countdown.
    """
    global _player_proc

    seconds = max(3, min(int(seconds), 15))
    _terminate_player()

    video = Path(video)
    if not video.is_file() or video.stat().st_size <= 0:
        _notify(f"Laptop Guard warning video is unavailable: {video}")
        _notification_fallback(seconds)
        return None

    result = _build_player_command(video, seconds)
    if result is None:
        _notify("Laptop Guard: install VLC (preferred), mpv, or ffplay for fullscreen warning video.")
        _notification_fallback(seconds)
        return None

    backend, cmd = result
    try:
        _player_proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=os.environ.copy(),
            start_new_session=(os.name != "nt"),
        )
        return _player_proc
    except (OSError, subprocess.SubprocessError) as exc:
        _player_proc = None
        _notify(f"Laptop Guard could not start {backend}: {exc}")
        _notification_fallback(seconds)
        return None


def _terminate_player() -> None:
    global _player_proc
    proc = _player_proc
    _player_proc = None
    if not proc or proc.poll() is not None:
        return
    try:
        if os.name != "nt":
            os.killpg(proc.pid, signal.SIGTERM)
        else:
            proc.terminate()
        proc.wait(timeout=1.5)
    except Exception:
        try:
            if os.name != "nt":
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
        except Exception:
            pass


def dismiss_warning(proc: subprocess.Popen | None = None) -> None:
    global _player_proc
    target = proc or _player_proc
    if target is None:
        return
    if target.poll() is not None:
        if target is _player_proc:
            _player_proc = None
        return
    try:
        if os.name != "nt":
            os.killpg(target.pid, signal.SIGTERM)
        else:
            target.terminate()
        target.wait(timeout=1.5)
    except Exception:
        try:
            if os.name != "nt":
                os.killpg(target.pid, signal.SIGKILL)
            else:
                target.kill()
        except Exception:
            pass
    if target is _player_proc:
        _player_proc = None


def play_warning_video(seconds: int = 5, video: Path = VIDEO_PATH) -> int:
    proc = launch_warning(seconds, video)
    if proc is None:
        return 1
    try:
        proc.wait()
    except KeyboardInterrupt:
        dismiss_warning(proc)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Laptop Guard fullscreen MP4 warning")
    parser.add_argument("--seconds", type=int, default=5)
    parser.add_argument("--video", type=Path, default=VIDEO_PATH)
    args = parser.parse_args()
    return play_warning_video(args.seconds, args.video)


if __name__ == "__main__":
    raise SystemExit(main())
