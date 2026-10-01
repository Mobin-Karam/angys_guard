import os

from laptop_guard.models import RetentionConfig
from laptop_guard.retention import cleanup_media


def test_media_retention_removes_expired_files_only(tmp_path):
    old = tmp_path / "old.jpg"
    fresh = tmp_path / "fresh.jpg"
    old.write_bytes(b"old")
    fresh.write_bytes(b"fresh")
    os.utime(old, (0, 0))

    result = cleanup_media(tmp_path, RetentionConfig(media_max_age_days=1, media_max_total_mb=16), now=172800)

    assert result.removed_files == 1
    assert not old.exists()
    assert fresh.exists()


def test_media_retention_evicts_oldest_files_when_size_limit_exceeded(tmp_path):
    first = tmp_path / "first.mp4"
    second = tmp_path / "second.mp4"
    first.write_bytes(b"a" * (9 * 1024 * 1024))
    second.write_bytes(b"b" * (9 * 1024 * 1024))
    os.utime(first, (100, 100))
    os.utime(second, (200, 200))

    cleanup_media(tmp_path, RetentionConfig(media_max_age_days=30, media_max_total_mb=16), now=300)

    assert not first.exists()
    assert second.exists()
