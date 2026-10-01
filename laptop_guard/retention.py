"""Bound local evidence storage without exposing remote filesystem control."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from .models import RetentionConfig


@dataclass(frozen=True)
class RetentionResult:
    removed_files: int = 0
    reclaimed_bytes: int = 0


def cleanup_media(path: Path, policy: RetentionConfig, *, now: float | None = None) -> RetentionResult:
    """Delete only regular files inside the configured local evidence directory."""
    if not policy.enabled or not path.is_dir():
        return RetentionResult()
    now = time.time() if now is None else now
    age_cutoff = now - max(1, min(int(policy.media_max_age_days), 3650)) * 86400
    limit = max(16, min(int(policy.media_max_total_mb), 1024 * 1024)) * 1024 * 1024
    files = []
    for item in path.iterdir():
        try:
            if item.is_file() and not item.is_symlink():
                stat = item.stat()
                files.append((item, stat.st_mtime, stat.st_size))
        except OSError:
            continue
    removed = reclaimed = 0
    for item, modified, size in files:
        if modified < age_cutoff:
            try:
                item.unlink()
                removed += 1
                reclaimed += size
            except OSError:
                pass
    survivors = [(item, modified, size) for item, modified, size in files if item.exists()]
    total = sum(size for _, _, size in survivors)
    for item, _, size in sorted(survivors, key=lambda row: row[1]):
        if total <= limit:
            break
        try:
            item.unlink()
            removed += 1
            reclaimed += size
            total -= size
        except OSError:
            pass
    return RetentionResult(removed, reclaimed)
