from pathlib import Path

import cv2


def test_warning_video_is_fullhd_five_seconds():
    path = Path(__file__).resolve().parents[1] / "laptop_guard" / "assets" / "warnings" / "countdown.mp4"
    assert path.exists()
    assert path.stat().st_size > 0
    cap = cv2.VideoCapture(str(path))
    try:
        assert cap.isOpened()
        assert int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) == 1920
        assert int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == 1080
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        assert 29 <= fps <= 31
        assert 4.9 <= frames / fps <= 5.1
    finally:
        cap.release()
