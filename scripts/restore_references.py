#!/usr/bin/env python3
"""Restore the immutable, public research references, never a candidate submission.

Uses the GitHub API through gh, streams each file to a temporary path and checks
its pinned SHA-256 before replacement. A missing or changed reference is fatal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "focus_sites.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def entries(manifest: dict):
    for row in manifest["sites"]:
        yield row, f"docs/downloads/{row['file']}", f"focus/{row['site']}.tif"
    witness = manifest["witness"]
    yield witness, f"docs/downloads/{witness['file']}", "r13-lattice.tif"
    for key, dest in (("mirror_template", "mirror-sample.tif"), ("mirror_labels", "mirror-labels.tif")):
        row = manifest[key]
        yield row, row["path"], dest


def restore(row: dict, source_path: str, dest: Path) -> str:
    expected = row["sha256"]
    if dest.is_file() and digest(dest) == expected:
        return "verified existing"
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    # A failed download cannot overwrite a good file or leave an accepted partial.
    try:
        api = f"repos/buffedlizard55-lab/{row['repo']}/contents/{source_path}?ref={row['ref']}"
        with tmp.open("wb") as out:
            subprocess.run(
                ["gh", "api", api, "-H", "Accept: application/vnd.github.raw"],
                stdout=out, stderr=subprocess.PIPE, check=True, timeout=180,
            )
        got = digest(tmp)
        if got != expected:
            raise ValueError(f"SHA-256 mismatch for {dest}: expected {expected}, got {got}")
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)
    return "restored and verified"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-dir", type=Path, default=ROOT / ".cache" / "input")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    try:
        for row, source_path, relative in entries(manifest):
            print(f"{relative}: {restore(row, source_path, args.target_dir / relative)}", flush=True)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Reference restoration failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
