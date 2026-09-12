from array import array

from laptop_guard.features.sound_detection import SoundDetectionFeature, pcm_rms
from laptop_guard.models import AudioConfig


def test_pcm_rms_distinguishes_silence_and_loud_audio():
    silence = array("h", [0] * 160).tobytes()
    loud = array("h", [16384] * 160).tobytes()

    assert pcm_rms(silence) == 0.0
    assert 0.49 < pcm_rms(loud) < 0.51


def test_sound_detection_is_opt_in_and_bounded():
    cfg = AudioConfig()
    feature = SoundDetectionFeature(object(), cfg)

    assert cfg.sound_detection_enabled is False
    assert cfg.sound_record_seconds == 8
    assert cfg.sound_cooldown == 30
    assert feature.name == "sound_detection"
