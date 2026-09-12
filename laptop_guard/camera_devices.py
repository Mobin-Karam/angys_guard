from __future__ import annotations

import contextlib
import os
import platform
import re
import struct
from dataclasses import dataclass
from pathlib import Path

import cv2


# Linux V4L2 capability bits. Keeping this tiny ioctl implementation avoids
# requiring v4l-utils just to distinguish camera capture nodes from metadata
# nodes that many laptop webcams expose as /dev/video1, /dev/video2, etc.
VIDIOC_QUERYCAP = 0x80685600
V4L2_CAP_VIDEO_CAPTURE = 0x00000001
V4L2_CAP_VIDEO_CAPTURE_MPLANE = 0x00001000
V4L2_CAP_DEVICE_CAPS = 0x80000000


@dataclass(frozen=True)
class CameraDevice:
    index: int
    path: str
    name: str
    bus_info: str = ""

    @property
    def label(self) -> str:
        location = f" — {self.bus_info}" if self.bus_info else ""
        return f"{self.name} ({self.path}){location}"


@contextlib.contextmanager
def quiet_opencv():
    """Temporarily suppress OpenCV backend warnings during device probing."""
    get_level = getattr(cv2, "getLogLevel", None)
    set_level = getattr(cv2, "setLogLevel", None)
    previous = None
    if callable(get_level):
        try:
            previous = get_level()
        except Exception:
            previous = None
    if callable(set_level):
        try:
            set_level(0)
        except Exception:
            pass
    try:
        yield
    finally:
        if callable(set_level) and previous is not None:
            try:
                set_level(previous)
            except Exception:
                pass


def _decode_c_string(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("utf-8", errors="replace").strip()


def _linux_capability(path: Path) -> CameraDevice | None:
    try:
        import fcntl

        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
    except (ImportError, OSError):
        return None
    try:
        buf = bytearray(104)
        fcntl.ioctl(fd, VIDIOC_QUERYCAP, buf, True)
        driver, card, bus, _version, capabilities, device_caps, *_reserved = struct.unpack(
            "=16s32s32sIII3I", buf
        )
        effective = device_caps if (capabilities & V4L2_CAP_DEVICE_CAPS) else capabilities
        if not (effective & (V4L2_CAP_VIDEO_CAPTURE | V4L2_CAP_VIDEO_CAPTURE_MPLANE)):
            return None
        match = re.search(r"(\d+)$", path.name)
        if not match:
            return None
        index = int(match.group(1))
        name = _decode_c_string(card) or _decode_c_string(driver) or f"Camera {index}"
        return CameraDevice(index=index, path=str(path), name=name, bus_info=_decode_c_string(bus))
    except OSError:
        return None
    finally:
        os.close(fd)


def open_camera(index: int) -> cv2.VideoCapture:
    """Open a camera predictably without probing nonexistent Linux indexes."""
    if platform.system().lower() == "linux":
        path = Path(f"/dev/video{index}")
        if path.exists():
            return cv2.VideoCapture(str(path), cv2.CAP_V4L2)
        # Return an unopened capture object rather than asking OpenCV/FFmpeg to
        # probe an index that Linux does not expose. This avoids noisy backend
        # errors when a camera is unplugged or the build host has no camera.
        return cv2.VideoCapture()
    return cv2.VideoCapture(index)


def probe_camera(index: int) -> tuple[bool, tuple[int, int] | None]:
    with quiet_opencv():
        cap = open_camera(index)
        try:
            if not cap.isOpened():
                return False, None
            ok, frame = cap.read()
            if not ok or frame is None:
                return False, None
            h, w = frame.shape[:2]
            return True, (w, h)
        finally:
            cap.release()


def discover_cameras(fallback_limit: int = 4) -> list[CameraDevice]:
    """Return usable camera capture devices without blindly probing indexes.

    Linux: inspect only existing /dev/video* nodes and reject metadata-only
    nodes through VIDIOC_QUERYCAP before opening anything with OpenCV.
    Other platforms: use a small quiet indexed probe as a fallback.
    """
    candidates: list[CameraDevice] = []
    if platform.system().lower() == "linux":
        def key(path: Path) -> int:
            m = re.search(r"(\d+)$", path.name)
            return int(m.group(1)) if m else 10_000

        for path in sorted(Path("/dev").glob("video[0-9]*"), key=key):
            device = _linux_capability(path)
            if device is not None:
                candidates.append(device)
    else:
        candidates = [
            CameraDevice(index=i, path=str(i), name=f"Camera {i}")
            for i in range(fallback_limit)
        ]

    usable: list[CameraDevice] = []
    for device in candidates:
        ok, _ = probe_camera(device.index)
        if ok:
            usable.append(device)

    # Some unusual Linux camera drivers may not implement QUERYCAP correctly.
    # If no candidates were discovered but /dev/video0 exists, make one quiet
    # fallback attempt so a working camera is not accidentally hidden.
    if not usable and platform.system().lower() == "linux" and Path("/dev/video0").exists():
        ok, _ = probe_camera(0)
        if ok:
            usable.append(CameraDevice(index=0, path="/dev/video0", name="Camera 0"))
    return usable


def camera_label(index: int) -> str:
    for device in discover_cameras():
        if device.index == index:
            return device.label
    return f"camera index {index}"
