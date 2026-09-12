#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / ".github" / "repository-profile.json"
API = "https://api.github.com"


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def infer_repository() -> str | None:
    env_repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if env_repo:
        return env_repo

    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except OSError:
        return None

    remote = result.stdout.strip()
    if not remote:
        return None

    patterns = (
        r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$",
        r"api\.github\.com/repos/([^/]+/[^/]+?)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.search(pattern, remote)
        if match:
            return match.group(1)
    return None


def request(token: str, method: str, path: str, payload: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "laptop-guard-repository-profile-sync",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30):
            return
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API {method} {path} failed with HTTP {exc.code}: {body[:800]}"
        ) from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Show or apply the canonical GitHub About description/topics."
    )
    parser.add_argument(
        "--repo",
        help="GitHub repository in owner/name form; defaults to GITHUB_REPOSITORY or origin remote.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply profile metadata through the GitHub API. Without this flag the command is read-only.",
    )
    args = parser.parse_args()

    profile = load_profile()
    repo = args.repo or infer_repository()

    summary = {
        "repository": repo,
        "description": profile["description"],
        "homepage": profile.get("homepage"),
        "topics": profile["topics"],
        "social_preview_source": profile.get("social_preview_source"),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if not args.apply:
        print("Read-only preview. Re-run with --apply and an admin-capable GH_TOKEN/GITHUB_TOKEN to sync About metadata.")
        return 0

    if not repo or "/" not in repo:
        print("Unable to determine repository. Pass --repo owner/name.", file=sys.stderr)
        return 2

    token = os.environ.get("GH_TOKEN", "").strip() or os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print(
            "GH_TOKEN or GITHUB_TOKEN is required for --apply. The token must have repository Administration write permission.",
            file=sys.stderr,
        )
        return 2

    request(
        token,
        "PATCH",
        f"/repos/{repo}",
        {
            "description": profile["description"],
            "homepage": profile.get("homepage"),
        },
    )
    request(
        token,
        "PUT",
        f"/repos/{repo}/topics",
        {"names": profile["topics"]},
    )

    print("Repository About description/homepage/topics synchronized successfully.")
    if profile.get("social_preview_source"):
        print(
            "Social preview remains a GitHub Settings UI upload; use the canonical source visual listed above."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
