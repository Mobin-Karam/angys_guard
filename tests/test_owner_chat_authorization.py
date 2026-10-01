from laptop_guard.guard import LaptopGuard


def test_guard_rejects_group_and_sender_mismatched_updates_before_dispatch():
    guard = LaptopGuard.__new__(LaptopGuard)
    received = []
    guard._handle_text = lambda chat_id, message: received.append((chat_id, message["text"]))
    guard._handle_voice_or_audio = lambda *_args: False

    guard.handle_update(
        {"message": {"from": {"id": 7}, "chat": {"id": -100, "type": "group"}, "text": "/lock"}}
    )
    guard.handle_update(
        {"message": {"from": {"id": 8}, "chat": {"id": 7, "type": "private"}, "text": "/lock"}}
    )

    assert received == []


def test_guard_dispatches_private_owner_message():
    guard = LaptopGuard.__new__(LaptopGuard)
    received = []
    guard._handle_text = lambda chat_id, message: received.append((chat_id, message["text"]))
    guard._handle_voice_or_audio = lambda *_args: False

    guard.handle_update(
        {"message": {"from": {"id": 7}, "chat": {"id": 7, "type": "private"}, "text": "/status"}}
    )

    assert received == [(7, "/status")]
