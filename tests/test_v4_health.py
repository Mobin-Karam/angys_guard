from laptop_guard.health import collect_health


def test_health_snapshot_is_non_throwing():
    snap = collect_health()
    assert snap.disk_free_gb is not None
    assert snap.disk_free_gb >= 0
