from __future__ import annotations

import contextlib
import os
import platform
import re
import struct
import threading
from dataclasses import dataclass
from pathlib import Path

import cv2


# Linux V4L2 capability bits.
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
    return raw.split(b"\0", 1)[0].decode(
        "utf-8",
        errors="replace",
    ).strip()


def _linux_capability(path: Path) -> CameraDevice | None:
    try:
        import fcntl

        fd = os.open(
            path,
            os.O_RDONLY | os.O_NONBLOCK,
        )

    except (ImportError, OSError):
        return None

    try:
        buf = bytearray(104)

        fcntl.ioctl(
            fd,
            VIDIOC_QUERYCAP,
            buf,
            True,
        )

        (
            driver,
            card,
            bus,
            _version,
            capabilities,
            device_caps,
            *_reserved,
        ) = struct.unpack(
            "=16s32s32sIII3I",
            buf,
        )

        effective = (
            device_caps
            if capabilities & V4L2_CAP_DEVICE_CAPS
            else capabilities
        )

        if not (
            effective
            & (
                V4L2_CAP_VIDEO_CAPTURE
                | V4L2_CAP_VIDEO_CAPTURE_MPLANE
            )
        ):
            return None

        match = re.search(r"(\d+)$", path.name)

        if not match:
            return None

        index = int(match.group(1))

        name = (
            _decode_c_string(card)
            or _decode_c_string(driver)
            or f"Camera {index}"
        )

        return CameraDevice(
            index=index,
            path=str(path),
            name=name,
            bus_info=_decode_c_string(bus),
        )

    except OSError:
        return None

    finally:
        os.close(fd)


def open_camera(index: int) -> cv2.VideoCapture:
    """
    Open a camera predictably without probing nonexistent Linux indexes.
    """
    if platform.system().lower() == "linux":
        path = Path(f"/dev/video{index}")

        if path.exists():
            return cv2.VideoCapture(
                str(path),
                cv2.CAP_V4L2,
            )

        # Return an unopened capture object instead of asking OpenCV to
        # probe a nonexistent camera index.
        return cv2.VideoCapture()

    return cv2.VideoCapture(index)


def close_camera(cap: cv2.VideoCapture | None) -> None:
    """
    Safely release a camera.

    Releasing VideoCapture stops this application from using the camera.
    On most laptop webcams this also causes the camera activity LED to
    turn off.
    """
    if cap is None:
        return

    try:
        if cap.isOpened():
            cap.release()
        else:
            cap.release()
    except Exception:
        pass


def turn_camera_on(index: int) -> cv2.VideoCapture | None:
    """
    Turn camera access ON for this application.

    Returns an opened VideoCapture on success.
    Returns None if the camera cannot be opened.
    """
    with quiet_opencv():
        cap = open_camera(index)

    if not cap.isOpened():
        close_camera(cap)
        return None

    return cap


def turn_camera_off(cap: cv2.VideoCapture | None) -> None:
    """
    Turn camera access OFF for this application.
    """
    close_camera(cap)


class CameraController:
    """
    Thread-safe camera ON/OFF controller.

    This controller owns one cv2.VideoCapture instance.

    Example:

        camera = CameraController(0)

        if camera.turn_on():
            ok, frame = camera.read()

        camera.turn_off()
    """

    def __init__(self, index: int = 0) -> None:
        self.index = index

        self._lock = threading.RLock()
        self._capture: cv2.VideoCapture | None = None

    @property
    def is_on(self) -> bool:
        """Return True when this controller currently owns an open camera."""
        with self._lock:
            return (
                self._capture is not None
                and self._capture.isOpened()
            )

    @property
    def capture(self) -> cv2.VideoCapture | None:
        """Return the underlying VideoCapture object."""
        with self._lock:
            if self._capture is None:
                return None

            if not self._capture.isOpened():
                return None

            return self._capture

    def turn_on(self) -> bool:
        """
        Open the camera.

        Returns:
            True  -> camera is ON
            False -> camera could not be opened
        """
        with self._lock:
            if self.is_on:
                return True

            self._release_unlocked()

            with quiet_opencv():
                cap = open_camera(self.index)

            if not cap.isOpened():
                close_camera(cap)
                self._capture = None
                return False

            self._capture = cap
            return True

    def turn_off(self) -> None:
        """
        Close and release the camera.
        """
        with self._lock:
            self._release_unlocked()

    def toggle(self) -> bool:
        """
        Toggle camera state.

        Returns the new state:

            True  = ON
            False = OFF
        """
        with self._lock:
            if self.is_on:
                self._release_unlocked()
                return False

            return self.turn_on()

    def read(self):
        """
        Read one frame.

        Returns:
            (False, None)

        when the camera is OFF.
        """
        with self._lock:
            if not self.is_on:
                return False, None

            try:
                return self._capture.read()
            except Exception:
                return False, None

    def _release_unlocked(self) -> None:
        if self._capture is not None:
            close_camera(self._capture)

        self._capture = None

    def __enter__(self):
        if not self.turn_on():
            raise RuntimeError(
                f"Could not open camera index {self.index}"
            )

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        self.turn_off()


def probe_camera(
    index: int,
) -> tuple[bool, tuple[int, int] | None]:

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
            close_camera(cap)


def discover_cameras(
    fallback_limit: int = 4,
) -> list[CameraDevice]:
    """
    Return usable camera capture devices without blindly probing indexes.

    Linux:
        Inspect existing /dev/video* nodes and reject metadata-only
        devices using VIDIOC_QUERYCAP.

    Other platforms:
        Use a small quiet indexed probe.
    """
    candidates: list[CameraDevice] = []

    if platform.system().lower() == "linux":

        def key(path: Path) -> int:
            match = re.search(r"(\d+)$", path.name)

            return (
                int(match.group(1))
                if match
                else 10_000
            )

        for path in sorted(
            Path("/dev").glob("video[0-9]*"),
            key=key,
        ):
            device = _linux_capability(path)

            if device is not None:
                candidates.append(device)

    else:
        candidates = [
            CameraDevice(
                index=i,
                path=str(i),
                name=f"Camera {i}",
            )
            for i in range(fallback_limit)
        ]

    usable: list[CameraDevice] = []

    for device in candidates:
        ok, _ = probe_camera(device.index)

        if ok:
            usable.append(device)

    # Some unusual Linux drivers may not implement QUERYCAP correctly.
    if (
        not usable
        and platform.system().lower() == "linux"
        and Path("/dev/video0").exists()
    ):
        ok, _ = probe_camera(0)

        if ok:
            usable.append(
                CameraDevice(
                    index=0,
                    path="/dev/video0",
                    name="Camera 0",
                )
            )

    return usable


def camera_label(index: int) -> str:
    for device in discover_cameras():
        if device.index == index:
            return device.label

    return f"camera index {index}"