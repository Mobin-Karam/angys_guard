from laptop_guard.camera import CameraMonitor, person_detection_capability
from laptop_guard.models import CameraConfig
import laptop_guard.camera as camera_module


def test_person_detector_capability_returns_tuple():
    ok, detail = person_detection_capability()
    assert isinstance(ok, bool)
    assert isinstance(detail, str)
    assert detail


def test_missing_hog_falls_back_without_crashing(monkeypatch):
    monkeypatch.delattr(camera_module.cv2, "HOGDescriptor", raising=False)
    monkeypatch.delattr(
        camera_module.cv2,
        "HOGDescriptor_getDefaultPeopleDetector",
        raising=False,
    )
    cfg = CameraConfig(mode="motion_person")
    monitor = CameraMonitor(cfg, lambda: True, lambda _path, _person: None)
    assert monitor.hog is None
    assert monitor.person_detector_available is False
    assert monitor.person_fallback_active is True
