from __future__ import annotations

import sys
import types
from pathlib import Path

import laptop_guard.persian_speech as speech
from laptop_guard.config import AppConfig


def test_tts_defaults(monkeypatch):
    for key in (
        "PERSIAN_TTS_ENABLED",
        "PERSIAN_TTS_VOICE",
        "PERSIAN_TTS_RATE_LIMIT",
        "PERSIAN_TTS_MAX_CHARS",
    ):
        monkeypatch.delenv(key, raising=False)
    cfg = AppConfig()
    assert cfg.tts.enabled is True
    assert cfg.tts.voice == "man2"
    assert cfg.tts.rate_limit == 0.5
    assert cfg.tts.max_chars == 700


def test_invalid_voice_falls_back(monkeypatch):
    monkeypatch.setenv("PERSIAN_TTS_VOICE", "unknown")
    cfg = AppConfig()
    assert cfg.tts.voice == "man2"


def test_normalize_voice():
    assert speech.normalize_voice("woman2") == "woman2"
    assert speech.normalize_voice("NOPE", "man4") == "man4"


def test_synthesis_and_playback_with_documented_async_api(tmp_path, monkeypatch):
    class FakeTTS:
        def __init__(self, default_voice="man1", rate_limit=0.5):
            self.default_voice = default_voice
            self.rate_limit = rate_limit

        async def speak_async(self, text, voice=None, filename="test.wav"):
            Path(filename).write_bytes(b"RIFFfake-wave")
            return filename

        async def shutdown(self):
            return None

    fake_module = types.ModuleType("py_persian_tts")
    fake_module.PersianTTS = FakeTTS
    monkeypatch.setitem(sys.modules, "py_persian_tts", fake_module)
    monkeypatch.setattr(speech, "MEDIA_DIR", tmp_path)
    monkeypatch.setattr(speech, "DATA_DIR", tmp_path)
    monkeypatch.setattr(speech, "play_audio", lambda path: path.exists())
    monkeypatch.setattr(speech, "notify", lambda _text: None)

    manager = speech.PersianSpeechManager(default_voice="man2")
    try:
        result = manager._run_job(speech._SpeechJob("سلام دنیا", "man2"))
        assert result.ok is True
        assert result.voice == "man2"
        assert result.path is not None and result.path.exists()
    finally:
        manager.stop()


def test_voice_selection_is_persisted(tmp_path, monkeypatch):
    monkeypatch.setattr(speech, "DATA_DIR", tmp_path)
    manager = speech.PersianSpeechManager(default_voice="man2")
    try:
        assert manager.set_voice("woman3") is True
        assert (tmp_path / "tts-state.txt").read_text(encoding="utf-8") == "woman3"
    finally:
        manager.stop()
