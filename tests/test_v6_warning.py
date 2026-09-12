from pathlib import Path

import laptop_guard.warning as warning_module


class FakeProc:
    def poll(self):
        return None

    def terminate(self):
        return None


def test_warning_manager_passes_image_stages_and_notifications(monkeypatch, tmp_path):
    calls = []

    def fake_popen(cmd, **kwargs):
        calls.append(cmd)
        return FakeProc()

    monkeypatch.setattr(warning_module.subprocess, "Popen", fake_popen)
    mgr = warning_module.WarningScreenManager()
    image = tmp_path / "event.jpg"
    image.write_bytes(b"x")
    assert mgr.show("هشدار", 5, image_path=image, stages=["یک", "دو"], notify_each_second=True)
    cmd = calls[0]
    assert "--image" in cmd
    assert str(image) in cmd
    assert "--stages-json" in cmd
    assert "--notify-each-second" in cmd
