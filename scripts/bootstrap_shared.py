#!/usr/bin/env python3
"""Restore hash-pinned public mirrors and upstream shared files into .cache.

No shared evaluator or writer is forked, modified, or executed by this script.
Mirror hashes verify consistency, not organizer provenance. The prepared feature
stack and an assigned lane are not supplied by this restoration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REF32 = "73485f27cf230af770167397c2b72cb9ce3b3f25"
HELPERS32 = {
    "scripts/restore_data.py": "4bbbb6552c4725558cadddc97f698393d584a5ec2a71bd1d41bb1f95c108dff6",
    "src/gems32/paths.py": "ceb7c79097958beff1f618e608491c3528341b14ee8b2e9cdcfafe1406230b69",
    "registry/data_manifest.json": "463cf26c840a9338816e873a762beb8186c50952ae26ae572e73d71eb329bd34",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def checked_download(repo: str, ref: str, source: str, dest: Path, expected: str) -> None:
    if dest.exists():
        if sha256(dest) != expected:
            raise ValueError(f"Cached file has wrong SHA-256: {dest}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.with_suffix(dest.suffix + ".partial")
    try:
        with temp.open("wb") as f:
            subprocess.run(["gh", "api", f"repos/{repo}/contents/{source}?ref={ref}",
                            "-H", "Accept: application/vnd.github.raw+json"], stdout=f, check=True)
        if sha256(temp) != expected:
            raise ValueError(f"Fetched file has wrong SHA-256: {source}")
        os.replace(temp, dest)
    finally:
        temp.unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--core", action="store_true", help="Also restore ~419 MB of unverified owner-mirror core data")
    ap.add_argument("--cache", type=Path, default=ROOT / ".cache")
    args = ap.parse_args()
    cache = args.cache.resolve()
    manifest = json.loads((ROOT / "registry/shared_protocol_assets.json").read_text())
    for item in manifest["files"]:
        relative = Path(item["dest"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Unsafe destination: {relative}")
        checked_download(item["repo"], item["ref"], item["path"], cache / "upstream" / relative, item["sha256"])
        print(f"verified {item['id']}")
    print("Shared protocol asset list restored. The evaluator CLI also imports lane-specific modules not in this manifest.")
    if args.core:
        helper_root = cache / "shared32"
        for path, expected in HELPERS32.items():
            checked_download("buffedlizard55-lab/GEMSDOE32", REF32, path, helper_root / path, expected)
        # Execute the unchanged upstream restoration utility against its pinned manifest.
        subprocess.run([sys.executable, str(helper_root / "scripts/restore_data.py"), "--group", "core",
                        "--target-dir", str(cache / "competition_data")], check=True)
        print("Owner-mirrored core bytes restored and hashed; official origin is not authenticated.")
    print("No experiment, prepared feature stack, TIFF, or submission authorization was created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
