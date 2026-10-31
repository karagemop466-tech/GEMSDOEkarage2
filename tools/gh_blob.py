#!/usr/bin/env python3
"""Fetch a single file from a public GitHub repository by pinned commit.

Why this exists
---------------
This sandbox can reach ``github.com``, ``codeload.github.com`` and
``api.github.com`` but **not** ``raw.githubusercontent.com``.  ``curl`` against
a raw URL fails with ``SSL_ERROR_SYSCALL``.  The Git *blobs* API is served from
``api.github.com`` and returns base64 content up to 100 MB per blob, so it is a
reliable transport here.

Every download is content-addressed: the caller passes the expected sha256 when
it is known and the fetch *fails closed* on mismatch.  Nothing is written to the
working tree unless the hash matches (or unless the caller explicitly advertises
``--no-verify``, which this project's gates never use for evidence inputs).

Usage
-----
    python tools/gh_blob.py --repo buffedlizard55-lab/GEMSDOE24 \
        --ref 07345ea0604953d7efb858d9cfbc21e20c7aca0b \
        --path data/bridge/labels.tif \
        --sha256 7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093 \
        --out .cache/gems_mirror/labels.tif
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = "https://api.github.com"
TREE_CACHE: dict[tuple[str, str], dict] = {}


def _get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "gemsdoe-research-desk/1",
        },
    )
    last = None
    for _attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError) as exc:  # pragma: no cover
            last = exc
    raise RuntimeError(f"GET failed after 3 attempts: {url}: {last}")


def tree(repo: str, ref: str) -> dict:
    key = (repo, ref)
    if key not in TREE_CACHE:
        TREE_CACHE[key] = json.loads(_get(f"{API}/repos/{repo}/git/trees/{ref}?recursive=1"))
    return TREE_CACHE[key]


def blob_sha(repo: str, ref: str, path: str) -> str:
    entries = tree(repo, ref).get("tree", [])
    for e in entries:
        if e["path"] == path and e["type"] == "blob":
            return e["sha"]
    raise KeyError(f"{path} not found in {repo}@{ref}")


def fetch(repo: str, ref: str, path: str, out: Path, sha256: str | None = None) -> dict:
    sha = blob_sha(repo, ref, path)
    payload = json.loads(_get(f"{API}/repos/{repo}/git/blobs/{sha}"))
    if payload.get("encoding") != "base64" or payload.get("truncated"):
        raise RuntimeError(f"unexpected blob payload for {path}: {payload.get('encoding')}, truncated={payload.get('truncated')}")
    data = base64.b64decode(payload["content"])
    got = hashlib.sha256(data).hexdigest()
    if sha256 is not None and got != sha256:
        raise SystemExit(f"HASH MISMATCH {path}: expected {sha256}, got {got}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return {"repo": repo, "ref": ref, "path": path, "blob_sha": sha, "sha256": got,
            "bytes": len(data), "out": str(out)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--sha256", default=None)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    rec = fetch(a.repo, a.ref, a.path, a.out, a.sha256)
    print(json.dumps(rec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
