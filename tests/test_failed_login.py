from laptop_guard.features.failed_login import FailedLoginEvent, FailedLoginFeature, parse_failed_login


class FakeHost:
    def __init__(self):
        self.events = []
        self.messages = []

    def feature_event(self, kind, detail, severity="info"):
        self.events.append((kind, detail, severity))

    def feature_notify_owner(self, text):
        self.messages.append(text)


def test_parses_gdm_authentication_failure_without_password_content():
    event = parse_failed_login({
        "SYSLOG_IDENTIFIER": "gdm-password",
        "MESSAGE": "pam_unix(gdm-password:auth): authentication failure; user=alice",
    })
    assert event == FailedLoginEvent(source="gdm-password", username="alice")


def test_parses_remote_ssh_failure_address():
    event = parse_failed_login({
        "_COMM": "sshd",
        "MESSAGE": "Failed password for invalid user admin from 192.0.2.5 port 22 ssh2",
    })
    assert event == FailedLoginEvent(source="sshd", username="admin", address="192.0.2.5")


def test_ignores_non_authentication_logs():
    assert parse_failed_login({"_COMM": "app", "MESSAGE": "authentication failure"}) is None
    assert parse_failed_login({"_COMM": "sshd", "MESSAGE": "session opened"}) is None


def test_notifies_owner_and_deduplicates_burst():
    host = FakeHost()
    feature = FailedLoginFeature(host)
    event = FailedLoginEvent("gdm-password", "alice")
    feature._notify(event)
    feature._notify(event)
    assert len(host.events) == 1
    assert len(host.messages) == 1
    assert "alice" in host.messages[0]
