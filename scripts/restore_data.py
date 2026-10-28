#!/usr/bin/env python3
"""Restore SHA-pinned *owner mirrors* to an ignored cache, not official data.

The default manifest contains four core rasters. Explicitly pass the upstream
manifest and a group to restore additional assets. A matching hash verifies
mirror bytes, not organizer authentication or permission to submit a file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32.paths import data_dir  # noqa: E402


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _fetch_from_codeload(repo: str, ref: str, path: str, dest: Path) -> None:
    import tarfile
    import urllib.request

    url = f"https://codeload.github.com/{repo}/tar.gz/{ref}"
    with urllib.request.urlopen(url, timeout=120) as resp, tarfile.open(fileobj=resp, mode="r|gz") as tf:
        for member in tf:
            if not member.isfile() or "/" not in member.name:
                continue
            rel = member.name.split("/", 1)[1]
            if rel == path:
                src = tf.extractfile(member)
                if src is None:
                    break
                with dest.open("wb") as out:
                    shutil.copyfileobj(src, out, 1 << 20)
                return
    raise FileNotFoundError(f"{path} not found in codeload tarball {repo}@{ref}")


def fetch(repo: str, ref: str, path: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    try:
        if shutil.which("gh"):
            try:
                with tmp.open("wb") as out:
                    subprocess.run(
                        [
                            "gh",
                            "api",
                            f"repos/{repo}/contents/{path}?ref={ref}",
                            "-H",
                            "Accept: application/vnd.github.raw",
                        ],
                        stdout=out,
                        stderr=subprocess.PIPE,
                        check=True,
                    )
                tmp.replace(dest)
                return
            except subprocess.CalledProcessError:
                tmp.unlink(missing_ok=True)
        _fetch_from_codeload(repo, ref, path, tmp)
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)


def restore_entry(entry: dict, root: Path) -> dict:
    # A manifest can be fetched from another project. Never permit a malicious
    # path or a pre-existing symlink to write outside the chosen scratch cache.
    root = root.resolve()
    dest = (root / entry["dest"]).resolve()
    if dest == root or not dest.is_relative_to(root):
        raise ValueError(f"Unsafe mirror destination: {entry['dest']}")
    if dest.exists() and sha256_file(dest) == entry["sha256"]:
        return {
            "id": entry["id"],
            "dest": entry["dest"],
            "group": entry["group"],
            "status": "present",
            "bytes": dest.stat().st_size,
            "sha256": entry["sha256"],
        }
    if "parts" in entry:
        tmp = dest.with_suffix(dest.suffix + ".assembling")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        try:
            with tmp.open("wb") as out:
                for part in entry["parts"]:
                    p = (root / "raw_parts" / Path(part).name).resolve()
                    if not p.is_relative_to(root):
                        raise ValueError(f"Unsafe mirror part destination: {part}")
                    fetch(entry["repo"], entry["ref"], part, p)
                    with p.open("rb") as src:
                        shutil.copyfileobj(src, out, 1 << 20)
                    p.unlink()
            got = sha256_file(tmp)
            if got != entry["sha256"]:
                raise ValueError(f"HASH MISMATCH for {entry['id']}: {got} != {entry['sha256']}")
            tmp.replace(dest)
        finally:
            tmp.unlink(missing_ok=True)
    else:
        fetch(entry["repo"], entry["ref"], entry["path"], dest)
        got = sha256_file(dest)
        if got != entry["sha256"]:
            dest.unlink(missing_ok=True)
            raise SystemExit(f"HASH MISMATCH for {entry['id']}: {got} != {entry['sha256']}")
    return {
        "id": entry["id"],
        "dest": entry["dest"],
        "group": entry["group"],
        "status": "restored",
        "bytes": dest.stat().st_size,
        "sha256": entry["sha256"],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--group", default="core", choices=["core", "external", "scored", "all"])
    ap.add_argument("--manifest", default=str(ROOT / "registry" / "core_data_manifest.json"),
                    help="Default: four SHA-pinned owner mirrors; use upstream_data_manifest.json explicitly for other groups")
    ap.add_argument("--target-dir", default=None, help="Override ignored scratch cache destination")
    args = ap.parse_args()

    man = json.loads(Path(args.manifest).read_text())
    root = Path(args.target_dir) if args.target_dir else data_dir()
    root.mkdir(parents=True, exist_ok=True)

    results = []
    for e in man["files"]:
        if args.group in ("all", e["group"]):
            r = restore_entry(e, root)
            results.append(r)
            print(f"{r['status']:>8}  {e['dest']:82s}  sha256={r['sha256'][:12]}…")

    try:
        storage_root = root.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        storage_root = str(root)
    receipt = {
        "schema_version": 2,
        "evidence_class": "OWNER-MIRROR-BYTE-INTEGRITY (not organizer authentication)",
        "manifest": str(Path(args.manifest)),
        "verified_files_count": len(results),
        "storage_root": storage_root,
        "files": results,
        "submission_authorized": False,
    }
    if not results:
        raise ValueError(f"No {args.group} assets in the selected manifest; nothing was verified")
    receipt_path = root / "restore_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(f"Verified {len(results)} owner-mirrored files; receipt written to {receipt_path}")


if __name__ == "__main__":
    main()
