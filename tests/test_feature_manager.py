from laptop_guard.features.manager import FeatureConflictError, FeatureManager


class DemoFeature:
    name = "demo"

    def __init__(self, calls):
        self.calls = calls

    def register(self, manager):
        manager.add_command(self.name, ("ping",), lambda chat_id, arg: self.calls.append((chat_id, arg)))

    def start(self):
        self.calls.append("start")

    def stop(self):
        self.calls.append("stop")


def test_feature_command_registration_dispatch_and_lifecycle():
    calls = []
    manager = FeatureManager()
    manager.install(DemoFeature(calls))
    assert manager.dispatch_command("/PING@my_bot", 42, "hello") is True
    assert manager.dispatch_command("/missing", 42) is False
    manager.start()
    manager.stop()
    assert calls == [(42, "hello"), "start", "stop"]


def test_duplicate_command_is_rejected():
    manager = FeatureManager()
    manager.add_command("one", ("/same",), lambda *_: None)
    try:
        manager.add_command("two", ("same",), lambda *_: None)
    except FeatureConflictError:
        pass
    else:
        raise AssertionError("duplicate command was accepted")


def test_overlapping_callback_prefix_is_rejected():
    manager = FeatureManager()
    manager.add_callback("one", "system:", lambda *_: None)
    try:
        manager.add_callback("two", "system:status", lambda *_: None)
    except FeatureConflictError:
        pass
    else:
        raise AssertionError("overlapping callback prefix was accepted")


def test_failed_feature_install_rolls_back_partial_routes():
    manager = FeatureManager()
    manager.add_command("existing", ("/taken",), lambda *_: None)

    class BrokenFeature(DemoFeature):
        name = "broken"

        def register(self, target):
            target.add_command(self.name, ("/partial",), lambda *_: None)
            target.add_command(self.name, ("/taken",), lambda *_: None)

    try:
        manager.install(BrokenFeature([]))
    except FeatureConflictError:
        pass
    else:
        raise AssertionError("broken feature was installed")
    assert manager.dispatch_command("/partial", 1) is False
