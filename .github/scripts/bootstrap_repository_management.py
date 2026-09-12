from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.github.com"
ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / ".github" / "repository-management"


def fail(message: str) -> None:
    print(f"::error::{message}")
    raise SystemExit(1)


def request(method: str, path: str, payload=None, *, allow_404: bool = False):
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        fail("GITHUB_TOKEN is missing")

    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "laptop-guard-repository-bootstrap",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if allow_404 and exc.code == 404:
            return None
        fail(f"GitHub API {method} {path} failed with HTTP {exc.code}: {body[:1000]}")


def load_json(name: str):
    return json.loads((CONFIG_DIR / name).read_text(encoding="utf-8"))


def ensure_labels(repo: str) -> None:
    print("==> labels")
    for label in load_json("labels.json"):
        encoded = urllib.parse.quote(label["name"], safe="")
        current = request("GET", f"/repos/{repo}/labels/{encoded}", allow_404=True)
        payload = {
            "color": label["color"],
            "description": label.get("description", ""),
        }
        if current is None:
            request("POST", f"/repos/{repo}/labels", {"name": label["name"], **payload})
            print(f"created label: {label['name']}")
        else:
            request("PATCH", f"/repos/{repo}/labels/{encoded}", {"new_name": label["name"], **payload})
            print(f"updated label: {label['name']}")


def ensure_milestones(repo: str) -> dict[str, int]:
    print("==> milestones")
    milestones = request("GET", f"/repos/{repo}/milestones?state=all&per_page=100") or []
    by_title = {item["title"]: item for item in milestones}
    result: dict[str, int] = {}

    for spec in load_json("milestones.json"):
        current = by_title.get(spec["title"])
        payload = {
            "title": spec["title"],
            "description": spec.get("description", ""),
            "state": "open",
        }
        if current is None:
            current = request("POST", f"/repos/{repo}/milestones", payload)
            print(f"created milestone: {spec['title']}")
        else:
            current = request("PATCH", f"/repos/{repo}/milestones/{current['number']}", payload)
            print(f"updated milestone: {spec['title']}")
        result[spec["title"]] = int(current["number"])
    return result


def ensure_issue_metadata(repo: str, milestone_numbers: dict[str, int]) -> None:
    print("==> issue metadata")
    issue_specs = load_json("issues.json")
    for number_text, spec in issue_specs.items():
        number = int(number_text)
        issue = request("GET", f"/repos/{repo}/issues/{number}", allow_404=True)
        if issue is None or "pull_request" in issue:
            print(f"skip missing/non-issue #{number}")
            continue

        current_labels = {item["name"] for item in issue.get("labels", [])}
        merged_labels = sorted(current_labels | set(spec.get("labels", [])))
        payload = {"labels": merged_labels}
        milestone_title = spec.get("milestone")
        if milestone_title:
            payload["milestone"] = milestone_numbers[milestone_title]
        request("PATCH", f"/repos/{repo}/issues/{number}", payload)
        print(f"updated issue #{number}")


def ensure_release(repo: str, sha: str) -> None:
    print("==> release")
    tag = "v11.1.0"
    encoded_tag = urllib.parse.quote(tag, safe="")
    notes = (CONFIG_DIR / "releases" / f"{tag}.md").read_text(encoding="utf-8")
    current = request("GET", f"/repos/{repo}/releases/tags/{encoded_tag}", allow_404=True)
    payload = {
        "tag_name": tag,
        "target_commitish": sha,
        "name": "Laptop Guard v11.1.0 — Stable Baseline",
        "body": notes,
        "draft": False,
        "prerelease": False,
        "make_latest": "true",
    }
    if current is None:
        release = request("POST", f"/repos/{repo}/releases", payload)
        print(f"created release: {release.get('html_url', tag)}")
    else:
        release = request("PATCH", f"/repos/{repo}/releases/{current['id']}", payload)
        print(f"updated release: {release.get('html_url', tag)}")


def main() -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    sha = os.environ.get("GITHUB_SHA", "").strip()
    if not repo or "/" not in repo:
        fail("GITHUB_REPOSITORY is missing or invalid")
    if not sha:
        fail("GITHUB_SHA is missing")

    print(f"Bootstrapping repository management for {repo} at {sha[:12]}")
    ensure_labels(repo)
    milestones = ensure_milestones(repo)
    ensure_issue_metadata(repo, milestones)
    ensure_release(repo, sha)
    print("Repository management bootstrap complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
