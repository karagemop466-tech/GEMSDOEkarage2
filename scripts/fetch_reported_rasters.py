#!/usr/bin/env python3
"""Fetch every reported-score raster named in the operator ledger.

The repository has nine pinned focus rasters and a 489-entry download manifest, but
the score ledger the operator supplies names ~40 submissions across ~35 sibling
sites. Those bytes are the only way to test any claim of the form "the live score of
this family is driven by X", because X has to be measured on files with *different*
scores. This script resolves each ledger name to a file in that repository's
``docs/downloads`` tree, downloads it, verifies it is a single-band float32 raster on
the pinned template grid, and records the sha256 of the bytes actually fetched.

Nothing here authorizes an upload. It is an evidence-collection tool: the ledger it
reads is user-reported, and every number it writes is an unverified input.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "registry/reported_scores_20261031.json"
CACHE = ROOT / ".cache/calibration"
OUT = ROOT / "evidence/calibration/reported_raster_bytes.json"
TEMPLATE = ROOT / ".cache/gems_data/example_submission.tif"


def norm(name: str) -> str:
    """Comparable key: no separators, lowercase, extension off."""
    name = re.sub(r"\.(tif|tiff|zip)$", "", name.lower())
    return re.sub(r"[^a-z0-9]", "", name)


def gh_json(args: list[str]) -> object:
    res = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip()[:300])
    return json.loads(res.stdout)


def tree_for(repo: str, ref: str | None) -> list[dict]:
    if ref is None:
        ref = gh_json([f"repos/{repo}"])["default_branch"]
    data = gh_json([f"repos/{repo}/git/trees/{ref}?recursive=1"])
    return [{"path": e["path"], "sha": e["sha"], "size": e.get("size")}
            for e in data.get("tree", []) if e["type"] == "blob"]


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    ledger = json.loads(LEDGER.read_text())
    tpl = rasterio.open(TEMPLATE)
    tpl_meta = (tpl.width, tpl.height, tpl.crs.to_string(), list(tpl.transform))

    records = []
    for site in ledger["sites"]:
        repo = site["repo"]
        try:
            blobs = [b for b in tree_for(repo, site.get("ref"))
                     if b["path"].endswith((".tif", ".tiff"))]
        except Exception as exc:  # noqa: BLE001
            records.append({"repo": repo, "status": f"tree failed: {exc}"})
            continue
        index = {norm(Path(b["path"]).name): b for b in blobs}
        for name, score in site["scores"].items():
            key = norm(name)
            blob = index.get(key)
            if blob is None:  # substring match, longest candidate wins
                cands = [b for k, b in index.items() if key and key in k]
                blob = max(cands, key=lambda b: len(norm(Path(b['path']).name))) if cands else None
            if blob is None:
                records.append({"repo": repo, "name": name, "score": score,
                                "status": "not found in docs tree"})
                continue
            dest = CACHE / re.sub(r"[^A-Za-z0-9._-]", "_", f"{repo.split('/')[-1]}-{Path(blob['path']).name}")
            if not dest.exists() or dest.stat().st_size != blob.get("size"):
                ref = site.get("ref") or gh_json([f"repos/{repo}"])["default_branch"]
                raw = subprocess.run(
                    ["gh", "api", f"repos/{repo}/contents/{blob['path']}?ref={ref}",
                     "-H", "Accept: application/vnd.github.raw"],
                    capture_output=True)
                if raw.returncode != 0:
                    records.append({"repo": repo, "name": name, "score": score,
                                    "status": f"raw failed: {raw.stderr.decode()[:120]}"})
                    continue
                dest.write_bytes(raw.stdout)
                time.sleep(0.15)
            try:
                with rasterio.open(dest) as src:
                    arr = np.asarray(src.read(1))
                    grid_ok = (src.width, src.height, src.crs.to_string(),
                               list(src.transform)) == tuple(tpl_meta)
                    rec = {
                        "repo": repo, "name": name, "score": score,
                        "path": str(dest.relative_to(ROOT)),
                        "git_path": blob["path"],
                        "bytes": dest.stat().st_size,
                        "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
                        "dtype": arr.dtype.str, "nodata": src.nodata,
                        "grid_ok": bool(grid_ok),
                        "finite_px": int(np.isfinite(arr).sum()),
                        "nan_px": int(np.isnan(arr).sum()) if arr.dtype.kind == "f" else 0,
                        "positive_px": int((arr > 0).sum()),
                        "mass": float(np.nansum(arr)),
                        "min": float(np.nanmin(arr)), "max": float(np.nanmax(arr)),
                        "unique_values": int(np.unique(arr[np.isfinite(arr)]).size),
                        "status": "ok",
                    }
            except Exception as exc:  # noqa: BLE001
                rec = {"repo": repo, "name": name, "score": score,
                       "status": f"read failed: {exc}"}
            records.append(rec)
            print(json.dumps({k: rec.get(k) for k in
                              ("repo", "name", "score", "positive_px", "status")}),
                  flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"schema": "gemsdoe.reported-raster-bytes.v1",
                               "template_grid": {"width": tpl_meta[0], "height": tpl_meta[1],
                                                 "crs": tpl_meta[2], "transform": tpl_meta[3]},
                               "n_records": len(records),
                               "n_ok": sum(1 for r in records if r.get("status") == "ok"),
                               "warning": ("scores are USER-REPORTED and unverified; these "
                                           "bytes are the owner's published rasters, not "
                                           "organizer receipts"),
                               "records": records}, indent=2, sort_keys=True) + "\n")
    n_ok = sum(1 for r in records if r.get("status") == "ok")
    print(f"\n{n_ok}/{len(records)} rasters fetched and read; wrote {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
