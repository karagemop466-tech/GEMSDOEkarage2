#!/usr/bin/env python3
"""Refresh public leaderboard and pinned-repository freshness for Pages.

No login, credentials beyond an optional GitHub API token, private scores, or
submission actions are used. Failures are explicit and preserve a dated last
successful leaderboard snapshot rather than silently presenting stale data.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
LEADERBOARD = "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag == "br" and self.cell is not None:
            self.cell.append(" ")

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None and self.row is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row:
                self.rows.append(self.row)
            self.row, self.cell = None, None


def diagnose_leaderboard_page(html: str) -> dict:
    """Return only fixed boolean/count facts, never response or exception text."""
    parser = TableParser()
    parser.feed(html)
    headers = [row for row in parser.rows if any("tversky" in c.casefold() for c in row)]
    lower = html.casefold()
    return {
        "parsed_rows": len(parser.rows),
        "header_has_rank": any(any("rank" in c.casefold() for c in row) for row in headers),
        "header_has_public_tversky": any(any("public" in c.casefold() and "tversky" in c.casefold() for c in row) for row in headers),
        "has_table_element": bool(re.search(r"<table(?:\s|>)", lower)),
        "has_script_element": bool(re.search(r"<script(?:\s|>)", lower)),
        "has_leaderboard_word": "leaderboard" in lower,
        "has_tversky_word": "tversky" in lower,
        "has_login_password_field": bool(re.search(r"name\s*=\s*['\"](?:password|passwd)['\"]", lower)),
        "has_challenge_markers": any(marker in lower for marker in ("cf-chl-", "challenge-platform", "cf-turnstile", "just a moment...")),
        "has_access_denied_marker": any(marker in lower for marker in ("access denied", "403 forbidden")),
        "empty_response": not bool(html.strip()),
    }


def parse_leaderboard(html: str) -> str:
    """Read the top public score only from a rank/Tversky-labelled table."""
    p = TableParser()
    p.feed(html)
    rank_index = score_index = None
    matches = []
    for row in p.rows:
        lowered = [x.casefold() for x in row]
        ranks = [i for i, x in enumerate(lowered) if x == "rank"]
        scores = [i for i, x in enumerate(lowered) if "tversky" in x and "public" in x]
        if ranks and scores:
            rank_index, score_index = ranks[0], scores[0]
            continue
        if rank_index is None or score_index is None or max(rank_index, score_index) >= len(row):
            continue
        if re.fullmatch(r"#?\s*1", row[rank_index].strip()):
            value = row[score_index].strip()
            if not re.fullmatch(r"(?:0(?:\.\d+)?|1(?:\.0+)?)", value):
                raise ValueError("Rank-one score is not a valid probability-like value")
            matches.append(value)
    if len(matches) != 1:
        raise ValueError("Could not unambiguously parse public rank-one score")
    return matches[0]


class SameOriginRedirect(HTTPRedirectHandler):
    """Prevent credentials or an apparent official result crossing origins."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old, new = urlparse(req.full_url), urlparse(newurl)
        if (old.scheme, old.hostname, old.port) != (new.scheme, new.hostname, new.port):
            raise ValueError("Unexpected cross-origin redirect")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get(url: str, *, github_token: str | None = None) -> str:
    headers = {"User-Agent": "GEMSDOEkarage2-public-status/1.0", "Accept": "text/html, application/json"}
    if github_token:
        if not url.startswith("https://api.github.com/"):
            raise ValueError("GitHub token may only be sent to the GitHub API")
        headers["Authorization"] = f"Bearer {github_token}"
    req = Request(url, headers=headers)
    with build_opener(SameOriginRedirect()).open(req, timeout=15) as response:
        # Cross-origin redirects are rejected before the follow-up request, so
        # a GitHub token cannot be forwarded to a different host.
        final = response.geturl()
        original, destination = urlparse(url), urlparse(final)
        if (original.scheme, original.hostname, original.port) != (destination.scheme, destination.hostname, destination.port):
            raise ValueError("Unexpected cross-origin redirect")
        data = response.read(4 * 1024 * 1024 + 1)
        if len(data) > 4 * 1024 * 1024:
            raise ValueError("Response exceeds monitor size limit")
    return data.decode("utf-8")


def previous_snapshot(previous: dict) -> dict | None:
    board = previous.get("leaderboard", {})
    if board.get("status") in ("ok", "snapshot") and board.get("score_text") and board.get("checked_utc"):
        return {k: board[k] for k in ("score_text", "checked_utc", "source", "evidence_class") if k in board}
    return board.get("last_successful")


def refresh(old: dict, manifest: dict, *, github_only: bool = False) -> dict:
    updated = {"generated_utc": now(), "note": "Freshness is not a scientific, format or submission-approval gate."}
    if github_only:
        updated["leaderboard"] = old.get("leaderboard", {"status": "unavailable"})
    else:
        page = None
        try:
            page = get(LEADERBOARD)
            score = parse_leaderboard(page)
            updated["leaderboard"] = {"status": "ok", "score_text": score, "rank": 1,
                "checked_utc": now(), "source": LEADERBOARD,
                "evidence_class": "PUBLIC ORGANIZER LEADERBOARD SNAPSHOT; not a file-bound submission receipt"}
        except (OSError, ValueError, UnicodeError, HTTPError, URLError) as exc:
            # Only publish fixed, locally generated diagnostics. Never publish a
            # response body, token, URL query, cookie, or arbitrary exception text.
            known = {
                "Unexpected cross-origin redirect": "cross-origin redirect rejected",
                "Response exceeds monitor size limit": "response exceeded size limit",
                "Rank-one score is not a valid probability-like value": "invalid rank-one value",
                "Could not unambiguously parse public rank-one score": "leaderboard table not recognized",
            }
            updated["leaderboard"] = {"status": "unavailable", "checked_utc": now(),
                "source": LEADERBOARD, "error_type": type(exc).__name__,
                "error_reason": known.get(str(exc), "network or unexpected response"),
                "last_successful": previous_snapshot(old)}
            if page is not None:
                try:
                    # Fixed response-shape facts only: no rows, body, or secrets.
                    updated["leaderboard"]["diagnostics"] = diagnose_leaderboard_page(page)
                except ValueError:
                    updated["leaderboard"]["diagnostics"] = {"parser_failed": True}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    sites = []
    for item in [x for x in manifest["assets"] if x["role"] == "focus"]:
        entry = {"site": item["site"], "pinned_ref": item["ref"], "checked_utc": now()}
        try:
            raw = get(f"https://api.github.com/repos/{item['repo']}/commits/main", github_token=token)
            head = json.loads(raw)["sha"]
            if not re.fullmatch(r"[0-9a-f]{40}", head):
                raise ValueError("Invalid GitHub commit id")
            entry.update(latest_ref=head, status="unchanged" if head == item["ref"] else "changed")
        except (OSError, ValueError, UnicodeError, KeyError, TypeError, HTTPError, URLError) as exc:
            entry.update(status="unavailable", error_type=type(exc).__name__)
        sites.append(entry)
    updated["sites"] = sites
    return updated


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=ROOT / "docs/data/monitor.json")
    ap.add_argument("--manifest", type=Path, default=ROOT / "registry/pinned_assets.json")
    ap.add_argument("--github-only", action="store_true", help="Keep the existing leaderboard snapshot without attempting its refresh")
    args = ap.parse_args()
    old = json.loads(args.output.read_text()) if args.output.exists() else {}
    result = refresh(old, json.loads(args.manifest.read_text()), github_only=args.github_only)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix(args.output.suffix + ".partial")
    tmp.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    os.replace(tmp, args.output)
    print(json.dumps({"leaderboard_status": result["leaderboard"]["status"],
                      "site_statuses": {i["site"]: i["status"] for i in result["sites"]},
                      "output": str(args.output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
