import laptop_guard.audio as audio_module
from laptop_guard.audio import AudioRecorder
from laptop_guard.models import AudioConfig


def test_failed_blocking_recording_removes_partial_private_file(tmp_path, monkeypatch):
    class CancelledProcess:
        returncode = 143

        def communicate(self, timeout=None):
            return b"", b"cancelled"

        def poll(self):
            return self.returncode

    def fake_popen(command, **_kwargs):
        output = tmp_path / command[-1].split("/")[-1]
        output.write_bytes(b"partial private audio")
        return CancelledProcess()

    monkeypatch.setattr(audio_module, "MEDIA_DIR", tmp_path)
    monkeypatch.setattr(audio_module.shutil, "which", lambda _name: "/usr/bin/ffmpeg")
    monkeypatch.setattr(audio_module.subprocess, "Popen", fake_popen)
    recorder = AudioRecorder(AudioConfig(local_notification=False), lambda *_: None)

    path, detail = recorder.record_blocking(2)

    assert path is None
    assert detail == "cancelled"
    assert list(tmp_path.iterdir()) == []
