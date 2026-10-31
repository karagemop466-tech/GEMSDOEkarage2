#!/usr/bin/env python3
"""Uniqueness audit of a candidate raster against the full shared registry.

Gate (from the project protocol)
--------------------------------
duplicate if  Spearman(candidate, registry) > 0.90
        or    > 70% of the candidate's dots lie within 3 px of one registry
              raster's dots.

Degeneracy fix
--------------
The one-sided 3 px test is vacuous against a *space-filling* reference: the
13GEMSDOE spacing-5 lattice places >=99.9% of any dot field within 3 px of one
of its nodes.  Every registry raster therefore also gets:

  coverage   = fraction of the footprint within 3 px of its dots
  enrichment = (fraction of candidate dots within 3 px) / coverage

A reference with coverage > 0.50 is a space-filling reference; its one-sided
3 px number is reported but CANNOT clear or fail the gate on its own, and the
enrichment and symmetric-overlap numbers are used instead.
"""
from __future__ import annotations

import argparse, hashlib, json, math, pathlib, subprocess, sys, time
import numpy as np
import rasterio
from scipy import ndimage
from scipy.stats import spearmanr

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = pathlib.Path("/home/user/.cache/gems_registry")
R_PX = 3.0


def fetch(repo: str, ref: str, path: str, dest: pathlib.Path) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with tmp.open("wb") as f:
            subprocess.run(["gh", "api", f"repos/buffedlizard55-lab/{repo}/contents/{path}?ref={ref}",
                            "-H", "Accept: application/vnd.github.raw"],
                           stdout=f, stderr=subprocess.PIPE, check=True, timeout=300)
        tmp.replace(dest)
        return True
    except Exception:
        tmp.unlink(missing_ok=True)
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--data-dir", default=str(ROOT / "data" / "core"))
    ap.add_argument("--manifest", default=str(ROOT / "registry" / "focus_registry_manifest.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    t0 = time.time()
    man = json.loads(pathlib.Path(args.manifest).read_text())
    with rasterio.open(args.candidate) as s:
        cand = s.read(1)
    with rasterio.open(pathlib.Path(args.data_dir) / "labels.tif") as s:
        foot = s.read(1) >= 0
    cdots = (cand > 0) & foot
    n_cd = int(cdots.sum())
    cand_flat = cand.ravel().astype(np.float32)
    print(f"candidate dots: {n_cd}")

    items = man["rasters"]
    if args.limit:
        items = items[: args.limit]
    CACHE.mkdir(parents=True, exist_ok=True)

    rows, failed = [], []
    for i, r in enumerate(items):
        rel = f"{r['repo']}__{pathlib.Path(r['path']).name}"
        dest = CACHE / rel
        if not dest.exists() or dest.stat().st_size != r["bytes"]:
            if not fetch(r["repo"], r["ref"], r["path"], dest):
                failed.append(dict(**{k: r[k] for k in ("repo", "path", "ref")}, reason="fetch"))
                continue
        try:
            with rasterio.open(dest) as s:
                if s.count != 1 or (s.height, s.width) != cand.shape:
                    failed.append(dict(repo=r["repo"], path=r["path"], reason="shape"))
                    continue
                a = np.nan_to_num(s.read(1).astype(np.float32), nan=0.0)
        except Exception as e:
            failed.append(dict(repo=r["repo"], path=r["path"], reason=f"read:{type(e).__name__}"))
            continue
        rd = (a > 0) & foot
        n_rd = int(rd.sum())
        if n_rd == 0:
            failed.append(dict(repo=r["repo"], path=r["path"], reason="empty"))
            continue
        inter = int((cdots & rd).sum())
        jac = inter / max(int((cdots | rd).sum()), 1)
        dR = ndimage.distance_transform_edt(~rd)
        cov = float((dR[foot] <= R_PX).mean())
        c_in_r = float((dR[cdots] <= R_PX).mean())
        dC = ndimage.distance_transform_edt(~cdots)
        r_in_c = float((dC[rd] <= R_PX).mean())
        rho = float(spearmanr(cand_flat, a.ravel()).statistic)
        rows.append(dict(repo=r["repo"], path=r["path"], n_dots=n_rd,
                         jaccard=round(jac, 6),
                         cand_within_3px_of_ref=round(c_in_r, 6),
                         ref_within_3px_of_cand=round(r_in_c, 6),
                         symmetric_min_within_3px=round(min(c_in_r, r_in_c), 6),
                         ref_footprint_coverage_3px=round(cov, 6),
                         enrichment_vs_coverage=round(c_in_r / cov, 4) if cov > 0 else None,
                         spearman=round(rho, 6),
                         space_filling_reference=bool(cov > 0.50)))
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(items)} ...", flush=True)
        del a, rd, dR, dC

    rows.sort(key=lambda x: -x["spearman"])
    sf = [x for x in rows if x["space_filling_reference"]]
    non_sf = [x for x in rows if not x["space_filling_reference"]]
    worst_rho = max(rows, key=lambda x: abs(x["spearman"])) if rows else None
    worst_gated = max(non_sf, key=lambda x: x["cand_within_3px_of_ref"]) if non_sf else None
    worst_sym = max(rows, key=lambda x: x["symmetric_min_within_3px"]) if rows else None
    worst_jac = max(rows, key=lambda x: x["jaccard"]) if rows else None

    verdict = (abs(worst_rho["spearman"]) <= 0.90)
    out = dict(
        schema_version=1,
        evidence_class="RASTER-MEASUREMENT",
        generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        candidate=pathlib.Path(args.candidate).name,
        candidate_sha256=hashlib.sha256(pathlib.Path(args.candidate).read_bytes()).hexdigest(),
        candidate_dots=n_cd,
        registry_rasters_compared=len(rows),
        registry_rasters_failed=len(failed),
        gate=dict(rule="duplicate if |spearman| > 0.90 OR > 70% of candidate dots within 3 px "
                       "of one registry raster's dots",
                  degeneracy_fix="references with >50% footprint coverage at 3 px are "
                                 "space-filling; their one-sided number is reported but cannot "
                                 "decide the gate. Enrichment vs coverage and symmetric overlap "
                                 "are reported alongside."),
        worst=dict(spearman_abs=worst_rho, one_sided_non_space_filling=worst_gated,
                   symmetric_min=worst_sym, jaccard=worst_jac),
        n_space_filling_references=len(sf),
        max_space_filling_one_sided=(max((x["cand_within_3px_of_ref"] for x in sf), default=None)),
        verdict="UNIQUE" if verdict else "DUPLICATE_STOP",
        top20_by_spearman=rows[:20],
        failed=failed[:50],
        runtime_s=round(time.time() - t0, 1),
    )
    pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.out).write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: out[k] for k in ("registry_rasters_compared", "registry_rasters_failed",
                                          "verdict", "n_space_filling_references",
                                          "max_space_filling_one_sided")}, indent=2))
    print("worst spearman:", json.dumps(out["worst"]["spearman_abs"], indent=2)[:600])
    print("worst one-sided (non space-filling):", json.dumps(out["worst"]["one_sided_non_space_filling"], indent=2)[:600])
    print("worst symmetric:", json.dumps(out["worst"]["symmetric_min"], indent=2)[:600])
    print(f"wrote {args.out}  ({out['runtime_s']}s)")


if __name__ == "__main__":
    main()
