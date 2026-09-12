from __future__ import annotations

import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Callable

import cv2

from .camera_devices import open_camera
from .config import MEDIA_DIR
from .models import CameraConfig


def person_detection_capability() -> tuple[bool, str]:
    version = getattr(cv2, "__version__", "unknown")
    if not hasattr(cv2, "HOGDescriptor"):
        return False, f"OpenCV {version}: HOGDescriptor is unavailable"
    if not hasattr(cv2, "HOGDescriptor_getDefaultPeopleDetector"):
        return False, f"OpenCV {version}: default HOG people detector is unavailable"
    try:
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    except Exception as exc:
        return False, f"OpenCV {version}: HOG initialization failed: {exc}"
    return True, f"OpenCV {version}: HOG people detector available"


class CameraMonitor:
    def __init__(
        self,
        config: CameraConfig,
        is_active: Callable[[], bool],
        on_motion: Callable[[Path, bool], None],
        on_tamper: Callable[[str, str], None] | None = None,
    ) -> None:
        self.config = config
        self.is_active = is_active
        self.on_motion = on_motion
        self.on_tamper = on_tamper
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.frame_lock = threading.RLock()
        self.last_frame = None
        self.camera_ok = False
        self.enabled_event = threading.Event()
        if self.config.enabled:
            self.enabled_event.set()

        pre_frames = max(1, int(max(1.0, self.config.fps) * max(0, self.config.pre_event_seconds)))
        self.prebuffer: deque = deque(maxlen=pre_frames)
        self._last_tamper: dict[str, float] = {}

        self.hog = None
        self.person_detector_available, self.person_detector_detail = person_detection_capability()
        if self.person_detector_available:
            try:
                self.hog = cv2.HOGDescriptor()
                self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            except Exception as exc:
                self.hog = None
                self.person_detector_available = False
                self.person_detector_detail = f"HOG initialization failed: {exc}"
        self.person_fallback_active = self.config.mode == "motion_person" and not self.person_detector_available
        if self.person_fallback_active:
            print("[camera] motion_person unavailable; safely falling back to motion-only alerts")

    def refresh_config(self) -> None:
        """Refresh runtime structures after a profile/settings change."""
        desired = max(1, int(max(1.0, self.config.fps) * max(0, self.config.pre_event_seconds)))
        with self.frame_lock:
            if self.prebuffer.maxlen != desired:
                recent = list(self.prebuffer)[-desired:]
                self.prebuffer = deque(recent, maxlen=desired)

    @property
    def enabled(self) -> bool:
        return self.enabled_event.is_set()

    def enable(self) -> None:
        self.config.enabled = True
        self.enabled_event.set()

    def disable(self) -> None:
        self.config.enabled = False
        self.enabled_event.clear()
        self.camera_ok = False
        with self.frame_lock:
            self.last_frame = None
            self.prebuffer.clear()

    def start(self) -> None:
        if self.thread and self.thread.is_alive():
            return
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._worker, daemon=True, name="camera-monitor")
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3)

    def snapshot(self) -> Path | None:
        if not self.enabled or not self.camera_ok:
            return None
        with self.frame_lock:
            if self.last_frame is None:
                return None
            frame = self.last_frame.copy()
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        path = MEDIA_DIR / f"snapshot-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.jpg"
        return path if cv2.imwrite(str(path), frame) else None

    def _video_frame(self, frame):
        h, w = frame.shape[:2]
        target = max(320, int(self.config.analysis_width))
        if w <= target:
            return frame.copy()
        scale = target / w
        return cv2.resize(frame, (target, int(h * scale)), interpolation=cv2.INTER_AREA)

    def record_clip(self, seconds: int | None = None, include_pre_event: bool = False) -> Path | None:
        if not self.enabled or not self.camera_ok:
            return None
        seconds = seconds if seconds is not None else self.config.event_clip_seconds
        seconds = max(1, min(int(seconds), 60))
        with self.frame_lock:
            current = None if self.last_frame is None else self._video_frame(self.last_frame)
            before = [f.copy() for f in self.prebuffer] if include_pre_event else []
        if current is None:
            return None
        h, w = current.shape[:2]
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        path = MEDIA_DIR / f"video-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.mp4"
        writer = cv2.VideoWriter(
            str(path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            max(4.0, float(self.config.fps)),
            (w, h),
        )
        if not writer.isOpened():
            return None
        try:
            for frame in before:
                if frame.shape[:2] != (h, w):
                    frame = cv2.resize(frame, (w, h), interpolation=cv2.INTER_AREA)
                writer.write(frame)
            end = time.monotonic() + seconds
            while time.monotonic() < end and not self.stop_event.is_set():
                with self.frame_lock:
                    live = None if self.last_frame is None else self._video_frame(self.last_frame)
                if live is not None:
                    if live.shape[:2] != (h, w):
                        live = cv2.resize(live, (w, h), interpolation=cv2.INTER_AREA)
                    writer.write(live)
                time.sleep(1 / max(4.0, float(self.config.fps)))
        finally:
            writer.release()
        return path if path.exists() and path.stat().st_size > 0 else None

    def _analysis_frame(self, frame):
        h, w = frame.shape[:2]
        if w <= self.config.analysis_width:
            return frame
        scale = self.config.analysis_width / w
        return cv2.resize(frame, (self.config.analysis_width, int(h * scale)), interpolation=cv2.INTER_AREA)

    def _has_person(self, frame) -> bool:
        if self.hog is None:
            return False
        try:
            boxes, _ = self.hog.detectMultiScale(frame, winStride=(8, 8), padding=(8, 8), scale=1.05)
            return len(boxes) > 0
        except Exception as exc:
            print(f"[camera] person detector failed; using motion fallback: {exc}")
            self.hog = None
            self.person_detector_available = False
            self.person_fallback_active = True
            return False

    def _tamper(self, kind: str, detail: str) -> None:
        if not self.on_tamper or not self.config.tamper_enabled:
            return
        now = time.monotonic()
        if now - self._last_tamper.get(kind, 0.0) < max(15.0, self.config.tamper_cooldown):
            return
        self._last_tamper[kind] = now
        try:
            self.on_tamper(kind, detail)
        except Exception as exc:
            print(f"[camera] tamper callback failed: {exc}")

    def _worker(self) -> None:
        had_camera = False
        while not self.stop_event.is_set():
            if not self.enabled_event.is_set():
                self.camera_ok = False
                self.enabled_event.wait(timeout=0.5)
                continue
            cap = open_camera(self.config.index)
            if not cap.isOpened():
                if had_camera and self.is_active():
                    self._tamper("camera_disconnected", "Camera could not be reopened")
                self.camera_ok = False
                time.sleep(5)
                continue
            had_camera = True
            self.camera_ok = True
            subtractor = cv2.createBackgroundSubtractorMOG2(history=350, varThreshold=35, detectShadows=True)
            confirm = 0
            warmup = max(12, int(self.config.fps * 2))
            frame_count = 0
            sleep_for = max(0.02, 1.0 / max(self.config.fps, 1.0))
            failures = 0
            black_count = 0
            frozen_since: float | None = None
            previous_gray = None
            try:
                while not self.stop_event.is_set():
                    if not self.enabled_event.is_set():
                        break
                    ok, frame = cap.read()
                    if not ok:
                        failures += 1
                        if failures >= 15:
                            if self.is_active():
                                self._tamper("camera_stream_lost", "Camera stopped returning frames")
                            break
                        time.sleep(0.15)
                        continue
                    failures = 0
                    with self.frame_lock:
                        self.last_frame = frame.copy()
                        if self.config.pre_event_seconds > 0:
                            self.prebuffer.append(self._video_frame(frame))

                    small = self._analysis_frame(frame)
                    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                    frame_count += 1

                    if self.config.tamper_enabled and self.is_active() and frame_count > warmup:
                        mean_brightness = float(gray.mean())
                        black_count = black_count + 1 if mean_brightness <= self.config.tamper_black_brightness else 0
                        if black_count >= max(3, int(self.config.fps * 2)):
                            self._tamper("camera_blocked", f"Very dark camera image (mean={mean_brightness:.1f})")
                            black_count = 0
                        if previous_gray is not None and previous_gray.shape == gray.shape:
                            diff = float(cv2.absdiff(previous_gray, gray).mean())
                            if diff < 0.015:
                                frozen_since = frozen_since or time.monotonic()
                                if time.monotonic() - frozen_since >= self.config.tamper_frozen_seconds:
                                    self._tamper("camera_frozen", "Camera image appears frozen")
                                    frozen_since = time.monotonic()
                            else:
                                frozen_since = None
                        previous_gray = gray.copy()

                    if frame_count <= warmup:
                        subtractor.apply(small)
                        time.sleep(sleep_for)
                        continue
                    if not self.is_active():
                        subtractor.apply(small, learningRate=0.01)
                        confirm = 0
                        time.sleep(sleep_for)
                        continue

                    fg = subtractor.apply(small)
                    fg = cv2.GaussianBlur(fg, (5, 5), 0)
                    _, mask = cv2.threshold(fg, 210, 255, cv2.THRESH_BINARY)
                    mask = cv2.morphologyEx(
                        mask,
                        cv2.MORPH_OPEN,
                        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
                    )
                    mask = cv2.dilate(mask, None, iterations=2)
                    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    moving = any(cv2.contourArea(c) >= self.config.motion_min_area for c in contours)
                    confirm = confirm + 1 if moving else 0
                    if confirm >= self.config.motion_confirm_frames:
                        confirm = 0
                        needs_person = self.config.mode == "motion_person" and self.person_detector_available and self.hog is not None
                        person = self._has_person(small) if needs_person else False
                        if needs_person and not person:
                            time.sleep(sleep_for)
                            continue
                        path = self.snapshot()
                        if path:
                            self.on_motion(path, person)
                    time.sleep(sleep_for)
            finally:
                cap.release()
                self.camera_ok = False
                if not self.stop_event.is_set():
                    time.sleep(2)
