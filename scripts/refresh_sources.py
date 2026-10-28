#!/usr/bin/env python3
"""Refresh GitHub repository HEAD metadata only (never the DrivenData site)."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import urllib.error

# Reuse the GitHub-only, same-origin redirect guard and bounded response reader.
# This job may carry an Actions token; urllib's default redirect handler does
# not enforce an origin boundary for that credential.
if __package__:
    from .refresh_feed import get
else:
    from refresh_feed import get

ROOT = Path(__file__).resolve().parents[1]


def github_head(repo: str, token: str | None = None) -> str:
    if not repo.startswith("GEMSDOE") or not repo[7:].isdigit():
        raise ValueError("Unexpected repository name")
    url = f"https://api.github.com/repos/buffedlizard55-lab/{repo}/commits/main"
    result = json.loads(get(url, github_token=token))
    sha = result["sha"]
    if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("Invalid GitHub commit SHA")
    return sha


def build_feed(snapshot: dict, getter) -> dict:
    rows = []
    for site, baseline in snapshot["heads"].items():
        try:
            current = getter(site)
            status = "unchanged" if current == baseline else "changed_since_review"
            error = None
        except (OSError, ValueError, KeyError, TypeError, UnicodeError, urllib.error.URLError) as exc:
            current, status, error = None, "unavailable", type(exc).__name__
        rows.append({"site": site, "reviewed_head": baseline, "current_head": current,
                     "status": status, "error": error})
    return {
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "reviewed_utc": snapshot["observed_utc"],
        "scope": "GitHub main-branch HEAD metadata only; no score, raster re-audit, organizer quota, or complete-registry claim.",
        "summary": {"total": len(rows),
                    "changed": sum(r["status"] == "changed_since_review" for r in rows),
                    "unavailable": sum(r["status"] == "unavailable" for r in rows)},
        "sources": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=ROOT / "registry/source_snapshot.json")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/field-notes/data/source-feed.json")
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text())
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    feed = build_feed(snapshot, lambda repo: github_head(repo, token))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(feed, indent=2, allow_nan=False) + "\n")
    print(json.dumps(feed["summary"], indent=2))
    return 0  # Publish an explicit unavailable state rather than stale success.


if __name__ == "__main__":
    raise SystemExit(main())
