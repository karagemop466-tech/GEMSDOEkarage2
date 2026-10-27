#!/usr/bin/env python3
"""Fetch pinned public research mirrors and shared tools; never publish a TIFF.

The mirrors are not independently authenticated organizer files. All binary
inputs remain in a git-ignored cache. No DrivenData credentials are used.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research/reference-sources.json"
DEFAULT_CACHE = ROOT / ".cache/research"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def blob_digest(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def gh_json(endpoint: str) -> dict:
    """gh reads Arena's configured GitHub auth; it is never logged or saved."""
    result = subprocess.run(
        ["gh", "api", endpoint], capture_output=True, check=True, text=True
    )
    return json.loads(result.stdout)


def safe_destination(cache: Path, relative: str) -> Path:
    cache = cache.resolve()
    destination = (cache / relative).resolve()
    if destination == cache or not destination.is_relative_to(cache):
        raise ValueError(f"Unsafe cache path: {relative}")
    return destination


def valid_bytes(data: bytes, item: dict) -> bool:
    return (
        len(data) == item["bytes"]
        and digest(data) == item["sha256"]
        and (not item.get("git_blob") or blob_digest(data) == item["git_blob"])
    )


def fetch(item: dict, cache: Path, relative: str) -> str:
    dest = safe_destination(cache, relative)
    if dest.is_file() and valid_bytes(dest.read_bytes(), item):
        return "cached"
    # Check that the *path at the pinned commit* really identifies the blob.
    # GitHub's contents endpoint omits content for files over 1 MiB; use the
    # immutable blob API in that case. Both content and hashes are checked.
    meta = gh_json(f"repos/{item['repo']}/contents/{item['path']}?ref={item['ref']}")
    if meta.get("type") != "file" or meta.get("size") != item["bytes"]:
        raise ValueError(f"Pinned source metadata mismatch: {item['path']}")
    if item.get("git_blob") and meta.get("sha") != item["git_blob"]:
        raise ValueError(f"Pinned Git blob mismatch: {item['path']}")
    if not meta.get("content"):
        meta = gh_json(f"repos/{item['repo']}/git/blobs/{meta['sha']}")
    if meta.get("encoding") != "base64" or not meta.get("content"):
        raise ValueError(f"No base64 payload: {item['path']}")
    data = base64.b64decode("".join(meta["content"].split()), validate=True)
    if not valid_bytes(data, item):
        raise ValueError(f"Content digest mismatch: {item['path']}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as out:
            name = out.name
            out.write(data)
        os.replace(name, dest)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)
    return "downloaded"


def bootstrap(cache: Path = DEFAULT_CACHE, manifest: Path = MANIFEST) -> dict:
    spec = json.loads(manifest.read_text())
    records = []
    for item in spec["inputs"] + spec["references"]:
        records.append((item["cache_path"], fetch(item, cache, item["cache_path"])))
    for item in spec["template"]["files"]:
        rel = "shared-template/" + item["path"]
        records.append((rel, fetch(item, cache, rel)))
    return {
        "cache": str(cache),
        "files": [{"path": p, "status": status} for p, status in records],
        "input_authority": "owner mirrors; not an authenticated organizer download",
        "submission_generated": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    args = p.parse_args()
    print(json.dumps(bootstrap(args.cache), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
