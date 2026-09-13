import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import laptop_guard.bale_api as mod


class FakeResponse:
    status_code = 200
    def json(self):
        return {'ok': True, 'result': {'message_id': 1}}
    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self):
        self.headers = {}
        self.calls = []
    def post(self, url, data=None, files=None, timeout=None):
        self.calls.append((url, data, files, timeout))
        return FakeResponse()


def test_send_message_serializes_inline_keyboard(monkeypatch):
    fake = FakeSession()
    monkeypatch.setattr(mod.requests, 'Session', lambda: fake)
    api = mod.BaleApi('123:secret')
    markup = {'inline_keyboard': [[{'text': 'Lock', 'callback_data': 'guard:lock'}]]}
    api.send_message(42, 'hello', reply_markup=markup)
    url, data, _, _ = fake.calls[-1]
    assert url.endswith('/bot123:secret/sendMessage')
    assert data['chat_id'] == '42'
    assert json.loads(data['reply_markup']) == markup


def test_file_download_url():
    api = object.__new__(mod.BaleApi)
    api.token = '123:secret'
    api.base_url = 'https://tapi.bale.ai'
    assert api._file_url('voice/file.ogg') == 'https://tapi.bale.ai/file/bot123:secret/voice/file.ogg'


def test_client_ignores_ambient_proxy_and_uses_explicit_proxy():
    api = mod.BaleApi('123:secret', proxy='http://127.0.0.1:8080')
    assert api.session.trust_env is False
    assert api.session.proxies['https'] == 'http://127.0.0.1:8080'


def test_download_limit_removes_partial_file():
    class DownloadResponse:
        headers = {}
        def __enter__(self): return self
        def __exit__(self, *_args): return None
        def raise_for_status(self): return None
        def iter_content(self, _size): yield b'1234'; yield b'5678'

    api = object.__new__(mod.BaleApi)
    api.token = 'test'
    api.base_url = 'https://example.invalid'
    api.get_file = lambda _file_id: {'file_path': 'voice.ogg'}
    api.session = type('Session', (), {'get': lambda *_args, **_kwargs: DownloadResponse()})()
    with TemporaryDirectory() as raw:
        target = Path(raw) / 'voice.ogg'
        with pytest.raises(mod.BaleApiError):
            api.download_file('voice', target, max_bytes=6)
        assert not target.exists()
