from laptop_guard.features.manager import FeatureManager
from laptop_guard.features.system_info import SystemInfoFeature


class Host:
    def __init__(self):
        self.replies = []

    def feature_reply(self, chat_id, text, markup=None):
        self.replies.append((chat_id, text, markup))

    def feature_main_menu(self):
        return {"menu": "main"}

    def feature_system_info(self):
        return "system"

    def feature_status(self):
        return "status"

    def feature_incident_summary(self):
        return "incident summary"

    def feature_help(self):
        return "help"

    def feature_event(self, *_args, **_kwargs):
        return None

    def feature_notify_owner(self, _text):
        return None


def test_system_info_feature_exposes_owner_incident_timeline():
    host = Host()
    manager = FeatureManager()
    manager.install(SystemInfoFeature(host))

    assert manager.dispatch_command("/incident", 7)
    assert host.replies == [(7, "incident summary", {"menu": "main"})]
