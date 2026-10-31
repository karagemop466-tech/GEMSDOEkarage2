#!/usr/bin/env python3
"""Materialise the PINNED registry rasters into .cache/registry (git-ignored).

Why this exists: ``scripts/audit_full_registry.py`` compares a candidate against every
row of ``registry/focus_registry_manifest.json`` whose ``local`` file exists and whose
sha256 matches. ``fetch_focus_registry.py`` re-enumerates each repo's *live* ``main``
and would rewrite that pinned manifest, so it is unsuitable for a reproducible audit.
This script reads the existing manifest, streams each repository's codeload tarball at
its pinned ``ref`` ONCE, extracts only the listed paths, and verifies every sha256 and
byte count. Rows that fail are reported and left ``missing`` (fail-closed); nothing is
silently dropped and the manifest is never modified.

Usage:  python scripts/fetch_pinned_registry.py [--manifest registry/focus_registry_manifest.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", type=Path, default=ROOT / "registry" / "focus_registry_manifest.json")
    ap.add_argument("--owner", default="buffedlizard55-lab")
    a = ap.parse_args()

    manifest = json.loads(a.manifest.read_text())
    rows = manifest["rasters"]
    by_ref: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in rows:
        if r.get("status") == "ok":
            by_ref[(r["repo"], r["ref"])].append(r)

    report = {"ok": 0, "missing": 0, "hash_mismatch": 0, "failed_repo": []}
    for (repo, ref), items in sorted(by_ref.items()):
        wanted = {r["path"]: r for r in items}
        url = f"https://codeload.github.com/{a.owner}/{repo}/tar.gz/{ref}"
        try:
            with urllib.request.urlopen(url, timeout=300) as resp, tarfile.open(fileobj=resp, mode="r|gz") as tf:
                for member in tf:
                    if not member.isfile() or "/" not in member.name:
                        continue
                    rel = member.name.split("/", 1)[1]
                    if rel not in wanted:
                        continue
                    row = wanted.pop(rel)
                    dest = ROOT / row["local"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    src = tf.extractfile(member)
                    tmp = dest.with_suffix(dest.suffix + ".partial")
                    with tmp.open("wb") as out:
                        while True:
                            chunk = src.read(1 << 20)
                            if not chunk:
                                break
                            out.write(chunk)
                    if sha256(tmp) != row["sha256"]:
                        tmp.unlink()
                        report["hash_mismatch"] += 1
                        print(f"HASH MISMATCH {repo}@{ref[:8]} {rel}", file=sys.stderr)
                        continue
                    tmp.replace(dest)
                    report["ok"] += 1
        except Exception as exc:  # network / archive failure: record, keep going
            report["failed_repo"].append({"repo": repo, "ref": ref, "error": str(exc)[:200]})
            print(f"REPO FAILED {repo}@{ref[:8]}: {exc}", file=sys.stderr)
        report["missing"] += len(wanted)
        for rel in wanted:
            print(f"MISSING {repo}@{ref[:8]} {rel}", file=sys.stderr)
    print(json.dumps(report, indent=2))
    return 0 if report["hash_mismatch"] == 0 and not report["failed_repo"] and report["missing"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
