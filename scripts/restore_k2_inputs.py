#!/usr/bin/env python3
"""Restore hash-pinned inputs for the 2026-10-28 K2 session from GitHub mirrors.

Sources are owner mirrors on github.com (the only reachable host family for the
competition files; DrivenData requires login). SHA-256 pins come from the
committed manifests — a pin match proves byte integrity vs the mirror snapshot,
NOT organizer authentication.

Restores:
  * core data   (.cache/gems_data/)      from registry/core_data_manifest.json
  * pinned best (.cache/registry_focus/) from registry/pinned_assets.json
  * 440-raster focus registry            from registry/focus_registry_manifest.json
    (written to each entry's `local` path under .cache/registry/)

Usage: python scripts/restore_k2_inputs.py [--jobs 6] [--skip-registry]
"""
from __future__ import annotations
import argparse, concurrent.futures as cf, hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWNER = "buffedlizard55-lab"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def fetch(repo, ref, path, dest: Path, expect_sha=None):
    if dest.exists() and expect_sha and sha256(dest) == expect_sha:
        return ("present", str(dest))
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    with tmp.open("wb") as fh:
        subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}?ref={ref}",
                        "-H", "Accept: application/vnd.github.raw"],
                       stdout=fh, check=True, stderr=subprocess.PIPE)
    if expect_sha and sha256(tmp) != expect_sha:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"SHA256 MISMATCH {repo}/{path}")
    tmp.replace(dest)
    return ("restored", str(dest))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--skip-registry", action="store_true")
    a = ap.parse_args()

    core = json.loads((ROOT / "registry/core_data_manifest.json").read_text())
    gd = ROOT / ".cache/gems_data"; gd.mkdir(parents=True, exist_ok=True)
    for e in core["files"]:
        dest = gd / e["dest"]
        if dest.exists() and sha256(dest) == e["sha256"]:
            print("present ", e["dest"]); continue
        if "parts" in e:
            parts = []
            for part in e["parts"]:
                p = gd / Path(part).name
                fetch(e["repo"], e["ref"], part, p); parts.append(p)
            with dest.open("wb") as out:
                for p in parts:
                    out.write(p.read_bytes()); p.unlink()
            assert sha256(dest) == e["sha256"], e["dest"]
        else:
            fetch(e["repo"], e["ref"], e["path"], dest, e["sha256"])
        print("restored", e["dest"])

    pinned = json.loads((ROOT / "registry/pinned_assets.json").read_text())
    pf = ROOT / ".cache/registry_focus"; pf.mkdir(parents=True, exist_ok=True)
    for x in pinned["assets"]:
        fetch(x["repo"], x["ref"], x["path"], pf / x["cache_name"], x["sha256"])
    print(f"pinned assets ok ({len(pinned['assets'])})")

    if not a.skip_registry:
        man = json.loads((ROOT / "registry/focus_registry_manifest.json").read_text())
        jobs = []
        for r in man["rasters"]:
            if r.get("status") != "ok":
                continue
            jobs.append((f"{OWNER}/{r['repo']}", r["ref"], r["path"],
                         ROOT / r["local"], r["sha256"]))
        done = 0
        with cf.ThreadPoolExecutor(a.jobs) as ex:
            futs = [ex.submit(fetch, *j) for j in jobs]
            for f in cf.as_completed(futs):
                f.result(); done += 1
                if done % 50 == 0:
                    print(f"  registry {done}/{len(jobs)}", flush=True)
        print(f"registry ok ({done} rasters)")
    print("ALL PINNED INPUTS VERIFIED")


if __name__ == "__main__":
    main()
