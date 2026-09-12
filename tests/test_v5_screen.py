from laptop_guard.screen_capture import ScreenCaptureManager


def test_screen_manager_reports_backend_string():
    mgr = ScreenCaptureManager(notify_local=False)
    assert isinstance(mgr.screenshot_backend, str)
    assert isinstance(mgr.video_backend, str)
