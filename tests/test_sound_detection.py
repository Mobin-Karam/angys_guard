from array import array
from types import SimpleNamespace

from laptop_guard.guard import LaptopGuard
from laptop_guard.sound_detection import SoundDetectionMonitor, pcm_rms
from laptop_guard.models import AudioConfig


def test_pcm_rms_distinguishes_silence_and_loud_audio():
    silence = array("h", [0] * 160).tobytes()
    loud = array("h", [16384] * 160).tobytes()

    assert pcm_rms(silence) == 0.0
    assert 0.49 < pcm_rms(loud) < 0.51


def test_sound_detection_is_opt_in_and_bounded():
    cfg = AudioConfig()
    feature = SoundDetectionMonitor(cfg, lambda: False, lambda: False, lambda *_: None, lambda *_: None)

    assert cfg.sound_detection_enabled is False
    assert cfg.sound_record_seconds == 8
    assert cfg.sound_cooldown == 30
    assert feature.available in {True, False}


def test_detected_sound_sends_only_bounded_recording(tmp_path):
    sent = []

    cfg = AudioConfig(sound_record_seconds=999)
    feature = SoundDetectionMonitor(cfg, lambda: True, lambda: True, lambda *_: None, lambda *args: sent.append(args))
    clip = tmp_path / "clip.ogg"
    clip.write_bytes(b"audio")
    feature._recorder.record_blocking = lambda seconds: (clip, f"seconds={seconds}")

    feature._capture_and_send(0.5)

    assert sent == [("voice", clip, "🎙 صدای محیط پس از تشخیص صدا • 30 ثانیه")]


def test_automatic_capture_requires_active_guard_and_owner():
    state = {"active": True, "owner": False}
    feature = SoundDetectionMonitor(
        AudioConfig(),
        lambda: state["active"],
        lambda: state["owner"],
        lambda *_: None,
        lambda *_: None,
    )

    assert feature._eligible() is False
    state["owner"] = True
    assert feature._eligible() is True
    feature.pause()
    assert feature._eligible() is False


def test_overlapping_pause_owners_do_not_resume_early():
    feature = SoundDetectionMonitor(AudioConfig(), lambda: True, lambda: True, lambda *_: None, lambda *_: None)

    feature.pause()
    feature.pause()
    feature.resume()

    assert feature._eligible() is False
    feature.resume()
    assert feature._eligible() is True


def test_clip_is_deleted_if_guard_disarms_during_recording(tmp_path):
    state = {"active": True}
    sent = []
    events = []
    feature = SoundDetectionMonitor(
        AudioConfig(),
        lambda: state["active"],
        lambda: True,
        lambda *args: events.append(args),
        lambda *args: sent.append(args),
    )
    clip = tmp_path / "cancelled.ogg"
    clip.write_bytes(b"private audio")

    def record_then_disarm(_seconds):
        state["active"] = False
        return clip, "ok"

    feature._recorder.record_blocking = record_then_disarm
    feature._capture_and_send(0.5)

    assert sent == []
    assert not clip.exists()
    assert events[-1][0] == "sound_record_cancelled"


def test_oversized_owner_voice_is_rejected_before_download():
    replies = []
    events = []
    guard = object.__new__(LaptopGuard)
    guard.config = SimpleNamespace(
        bot=SimpleNamespace(chat_id=7),
        audio=SimpleNamespace(max_remote_file_mb=1, auto_play_owner_voice=True),
    )
    guard.events = SimpleNamespace(add=lambda *args: events.append(args))
    guard._reply_to_chat = lambda chat_id, text, markup=None: replies.append((chat_id, text))

    handled = guard._handle_voice_or_audio(
        7,
        {"voice": {"file_id": "voice-id", "file_size": 2 * 1024 * 1024}},
    )

    assert handled is True
    assert "1 MB" in replies[0][1]
    assert events[0][0] == "owner_voice_rejected"
