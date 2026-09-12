import json
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
