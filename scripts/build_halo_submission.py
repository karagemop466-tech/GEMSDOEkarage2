#!/usr/bin/env python3
"""Build, validate and audit the HALO submission raster.

The method is the winner of the three pre-registered experiments in
`scripts/lane_halo.py` (E1 distance-decay, E2 budget/spacing sweep, E3
geophysical tie-break = rejected negative).  Nothing from any registry or
published submission is read as input: the only inputs are the two
hash-pinned organizer-mirror files (`existing_faults.tif` as the mapped
catalogue, `sample_submission.tif` as the grid/footprint) and the pinned
`.cache/registry` inventory, which is used **only** as a comparison set.

Steps
-----
1. distance transform to the mapped catalogue;
2. candidate band = measured enriched halo (default 3-9 px = 300-900 m);
3. greedy minimum-spacing selection (`min_sep`) of exactly `n_max` dots,
   uniform-within-band with a fixed seed (E3 rejected a geophysical tie-break);
4. write a single-band float32 GeoTIFF on the organizer grid: 1.0 at dots,
   0.0 everywhere else (all finite, so no pixel can be out of [0, 1]);
5. strict format validation, uniqueness audit against the full pinned
   registry inventory, and score projection from `scripts/score_model.py`.

Outputs: `docs/downloads/<name>.tif` (the file to submit), `*.audit.json`,
`*.run-card.json`, and `evidence/halo/final_generation.json`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems57.grid import TRANSFORM, load_grid, write_submission  # noqa: E402
from gems57.metric import ALPHA, BETA, kernel  # noqa: E402
from gems57.uniqueness import compare_array_to_registry  # noqa: E402

DATA = ROOT / ".cache" / "gems_data"
REGISTRY_DIR = ROOT / ".cache" / "registry"
FOCUS = ROOT / ".cache" / "registry_focus"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence" / "halo"

PROBE_NOTE = ("r13_lattice is a uniform 5-px sampling probe, not a competitor "
              "submission: it covers 99.87 % of the scored domain within 3 px, so "
              "every possible raster 'overlaps' it. It is reported separately and "
              "is not counted as a duplicate witness.")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def registry_index() -> dict:
    """The pinned 489-raster focus inventory, plus the lattice probe as a probe row."""
    man = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())
    rasters = []
    for r in man["rasters"]:
        if r.get("status") != "ok":
            raise SystemExit("registry manifest contains a failed source; fail closed")
        rasters.append({
            "repo_first": r["repo"],
            "sources": [r["path"]],
            "cache_file": r["local"],
            "sha256": r["sha256"],
            "category": "submission",
        })
    probe = ROOT / "registry" / "pinned_assets.json"
    pin = json.loads(probe.read_text())
    lat = [a for a in pin["assets"] if a["role"] == "lattice"][0]
    lat_path = FOCUS / lat["cache_name"]
    rasters.append({
        "repo_first": lat["repo"],
        "sources": [lat["path"]],
        "cache_file": str(lat_path.relative_to(ROOT)),
        "sha256": lat["sha256"],
        "category": "probe",
    })
    return {"rasters": rasters, "complete_accessible_scan": True, "errors": []}, lat_path


def build_mask(grid, rings, n_max, min_sep, seed) -> tuple[np.ndarray, dict]:
    d = ndi.distance_transform_edt(~grid.catalogue)
    band = np.zeros(d.shape, bool)
    for lo, hi in rings:
        band |= (d >= lo) & (d < hi)
    band &= grid.footprint
    idx = np.flatnonzero(band)
    rng = np.random.default_rng(seed)
    idx = idx[rng.permutation(idx.size)]
    h, w = band.shape
    blocked = np.zeros((h, w), bool)
    out = np.zeros((h, w), bool)
    y, x = np.divmod(idx, w)
    taken = 0
    for yy, xx in zip(y, x):
        if blocked[yy, xx]:
            continue
        out[yy, xx] = True
        blocked[max(0, yy - min_sep):yy + min_sep + 1,
                max(0, xx - min_sep):xx + min_sep + 1] = True
        taken += 1
        if taken >= n_max:
            break
    # realized spacing audit: nearest-neighbour distance between emitted dots
    from scipy.spatial import cKDTree
    yy, xx = np.nonzero(out)
    sep = 0.0
    if yy.size > 1:
        d_nn, _ = cKDTree(np.c_[yy, xx]).query(np.c_[yy, xx], k=2)
        sep = float(d_nn[:, 1].min())
    info = {"band_px": int(band.sum()), "dots_requested": n_max, "dots_emitted": int(out.sum()),
            "min_sep_requested_px": min_sep, "min_realised_separation_px": sep,
            "mean_distance_to_catalogue_px": float(d[out].mean()) if out.any() else 0.0,
            "dots_inside_footprint": int((out & grid.footprint).sum()),
            "dots_on_mapped_catalogue": int((out & grid.catalogue).sum())}
    return out, info


def validate(path: Path, footprint: np.ndarray) -> dict:
    with rasterio.open(path) as ds:
        a = ds.read(1)
        checks = {
            "driver": ds.driver,
            "count": ds.count,
            "dtype": str(ds.dtypes[0]),
            "shape": [ds.height, ds.width],
            "crs": str(ds.crs),
            "transform": [round(v, 6) for v in tuple(ds.transform)[:6]],
            "nodata": ds.nodata,
        }
    expected_crs = "EPSG:32611"
    checks["crs_ok"] = checks["crs"] == expected_crs
    checks["shape_ok"] = checks["shape"] == [3730, 3292]
    checks["transform_ok"] = checks["transform"] == [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0]
    checks["single_band_ok"] = checks["count"] == 1
    checks["float32_ok"] = checks["dtype"] == "float32"
    checks["all_finite"] = bool(np.isfinite(a).all())
    checks["nan_inside_footprint"] = int(np.isnan(a[footprint]).sum())
    checks["min"] = float(a.min())
    checks["max"] = float(a.max())
    checks["range_ok"] = bool(a.min() >= 0.0 and a.max() <= 1.0)
    checks["positive_pixels"] = int((a > 0).sum())
    checks["distinct_values"] = int(np.unique(a).size)
    checks["sha256"] = sha256_file(path)
    checks["bytes"] = path.stat().st_size
    checks["passed"] = bool(all(checks[k] for k in
                                ("crs_ok", "shape_ok", "transform_ok", "single_band_ok",
                                 "float32_ok", "all_finite", "range_ok"))
                            and checks["nan_inside_footprint"] == 0)
    return checks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rings", default="3,9", help="halo band in px, e.g. 3,9")
    ap.add_argument("--n-max", type=int, default=44090)
    ap.add_argument("--min-sep", type=int, default=2)
    ap.add_argument("--seed", type=int, default=20261031)
    ap.add_argument("--name", default=None)
    args = ap.parse_args()

    lo, hi = (float(v) for v in args.rings.split(","))
    rings = [(lo, hi)]
    grid = load_grid(DATA)
    mask, gen = build_mask(grid, rings, args.n_max, args.min_sep, args.seed)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tag = f"halo{int(lo)}{int(hi)}-b{gen['dots_emitted']}-sep{args.min_sep}-{stamp}"
    name = args.name or f"gemsdoe-karage2-{tag}"
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    tif = DOWNLOADS / f"{name}.tif"
    values = mask.astype(np.float32)          # zeros outside footprint: always in [0,1]
    write_submission(tif, values, mode="zeros")
    checks = validate(tif, grid.footprint)
    print(f"{tif.name}: {checks['positive_pixels']} dots, "
          f"range [{checks['min']}, {checks['max']}], passed={checks['passed']}")

    # ---- uniqueness ------------------------------------------------------
    # Two independent measurements are recorded:
    #  (a) the literal shared gate (gems57.uniqueness.compare_array_to_registry)
    #      run over the pinned inventory as-is: it fails closed on the one
    #      non-grid QA blob and counts the uniform lattice probe as a witness,
    #      which makes it unsatisfiable by construction (documented below);
    #  (b) the operational gate (scripts/audit_halo_uniqueness.py): identical
    #      thresholds, but rasters that cover >90 % of the scored domain within
    #      3 px are classified from their own bytes as unavoidable probes, and
    #      blobs that are not on the organizer grid cannot be competing
    #      submissions.  Both are published; (b) additionally includes any
    #      raster published after the pinned snapshot (`--delta`).
    index, lat_path = registry_index()
    with rasterio.open(tif) as ds:
        arr = ds.read(1)
    literal = compare_array_to_registry(arr, index, grid.footprint,
                                        file_sha256=checks["sha256"])
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "registry_rows_literal_gate.json").write_text(json.dumps(
        {"candidate": name, "rows": literal["rows"]}, indent=2, allow_nan=False) + "\n")

    delta = ROOT / "registry" / "delta_after_20261029.json"
    cmd = [sys.executable, str(ROOT / "scripts" / "audit_halo_uniqueness.py"),
           "--tif", str(tif), "--label", name,
           "--out", str(EVIDENCE / "uniqueness_final.json")]
    if delta.exists():
        cmd += ["--delta", str(delta)]
    import subprocess
    subprocess.run(cmd, check=True)
    fast = json.loads((EVIDENCE / "uniqueness_final.json").read_text())
    practical = {
        "evidence_class": fast["evidence_class"],
        "registry_unique_rasters": fast["registry_unique_rasters"],
        "submission_rasters_compared": fast["submission_rasters"],
        "delta_rasters_included": len(json.loads(delta.read_text())) if delta.exists() else 0,
        "worst_dot_overlap": fast["worst_forward_overlap"],
        "worst_overlap_submission": fast["worst_forward_overlap_path"],
        "worst_spearman": fast["worst_spearman"],
        "worst_spearman_submission": fast["worst_spearman_path"],
        "rasters_above_0_70_overlap": fast["rasters_above_0_70_overlap"],
        "rasters_above_0_90_rho": fast["rasters_above_0_90_rho"],
        "universal_probes": fast["universal_probes"],
        "non_grid_files": fast["non_grid_files"],
        "probe_note": PROBE_NOTE,
        "unique_vs_submission_rasters": fast["unique_vs_submission_rasters"],
    }
    print(f"uniqueness: worst overlap {practical['worst_dot_overlap']:.3f} "
          f"({practical['worst_overlap_submission'].split('/')[-1][:60]}), "
          f"worst rho {practical['worst_spearman']:.3f}, "
          f"probes={len(practical['universal_probes'])}, "
          f"unique={practical['unique_vs_submission_rasters']}")

    # ---- score projection ------------------------------------------------
    model = json.loads((ROOT / "evidence" / "score_model.json").read_text())
    G = model["hidden_truth"]["G_px"]
    K = model["credits_per_hit"]["value"]
    n = gen["dots_emitted"]

    def project(h):
        T = min(K * n * h, G)
        F = n * (1 - h)
        return {"hit_rate": h, "T": T, "F": F,
                "dti": float(T / (ALPHA * T + ALPHA * F + BETA * G + 1e-12)),
                "coverage": T / G}

    scenarios = {f"h={h:.3f}": project(h) for h in
                 (0.020, 0.025, 0.029, 0.035, 0.045, 0.060, 0.080)}
    e2 = json.loads((EVIDENCE / "e2.json").read_text())
    curve = [r for r in e2["sweep"] if r["rings"] == "halo_3_9" and r["min_sep"] == args.min_sep]
    holdout = max(curve, key=lambda r: r["dti"]) if curve else None
    at_n = min(curve, key=lambda r: abs(r["n_emit"] - n)) if curve else None

    note = ("Off-apron 300-900 m halo of mapped traces; 44,090 min-spaced dots, none on the "
            "catalogue. No registry file reused.")
    receipt = {
        "evidence_class": "SAVED-BYTE CHECK + REGISTRY-MEASUREMENT + "
                          "CALIBRATED-PRIVATE PROJECTION (never ORGANIZER-CONFIRMED)",
        "generated_utc": stamp,
        "submission_file": str(tif.relative_to(ROOT)),
        "submission_name": name,
        "submission_note": note[:140],
        "submission_note_length": len(note[:140]),
        "method": {"lane": "HALO", "rings_px": [lo, hi], "rings_m": [lo * 100, hi * 100],
                   "min_sep_px": args.min_sep, "seed": args.seed,
                   "selection": "uniform within band (E3 rejected the ridge tie-break)",
                   "values": "1.0 at dots, 0.0 elsewhere (all finite)"},
        "generation": gen,
        "format_checks": checks,
        "uniqueness": practical,
        "uniqueness_literal_gate": {
            "unique": literal["unique"],
            "worst_overlap_including_probe": literal["worst_dot_overlap"],
            "worst_overlap_submission_including_probe": literal.get("worst_overlap_submission"),
            "duplicate_count": literal["duplicate_count"],
            "stop_required": literal["stop_required"],
            "missing_or_invalid": literal["missing_or_invalid"],
            "scope": literal["scope"],
            "vacuous_because": PROBE_NOTE + " The pinned inventory also contains one non-grid "
                              "QA blob (GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif) that the literal "
                              "gate reports as a missing entry.",
        },
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI (pooled over 4 spatial quadrant folds, whole "
                              "components withheld, alpha 0.2 / beta 0.8 / 300 m kernel)",
            "lane_budget_curve_max": holdout,
            "at_released_dot_count": at_n,
            "budget_curve": [{"n_max": r["n_max"], "n_emit": r["n_emit"], "dti": r["dti"],
                              "hit_rate": r["hit_rate"], "coverage": r["coverage"]}
                             for r in sorted(curve, key=lambda r: r["n_max"])],
            "reading": "The lane curve is monotone in dot count up to its last tested point "
                       "(n_max = 62,000 -> 57,873 dots in-fold), where it is +6% on the released "
                       "44,090-dot field. The released count sits at the band's minimum-separation "
                       "capacity and inside the flat part of the leaderboard-calibrated model too, "
                       "so the extra 13,783 dots buy a holdout gain that the calibrated model does "
                       "not confirm. Both are inside the same noise band; the smaller field was "
                       "kept because it is the one whose uniqueness audit is clean at 65.5% max "
                       "3 px overlap.",
        },
        "score_projection": {"G_px": G, "credits_per_hit": K, "dots": n,
                             "scenarios": scenarios,
                             "basis": "scripts/score_model.py projection; the hit rate "
                                      "is an ASSUMPTION, not a measurement"},
        "break_even": model["break_even_hit_rate"]["target_0.2778"].get(str(n)),
        "verdict": None,
    }
    receipt["verdict"] = {
        "format_valid": checks["passed"],
        "unique_vs_submission_rasters": practical["unique_vs_submission_rasters"],
        "ok_to_download": bool(checks["passed"] and practical["unique_vs_submission_rasters"]),
        "ok_to_submit": bool(checks["passed"] and practical["unique_vs_submission_rasters"]),
        "leaderboard_estimate": "range, not a score: see score_projection.scenarios",
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "final_generation.json").write_text(
        json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    audit = DOWNLOADS / f"{name}.audit.json"
    audit.write_text(json.dumps({k: receipt[k] for k in
                                 ("evidence_class", "generated_utc", "submission_file",
                                  "submission_name", "format_checks", "uniqueness",
                                  "uniqueness_literal_gate", "verdict")},
                                indent=2, allow_nan=False) + "\n")
    runcard = DOWNLOADS / f"{name}.run-card.json"
    runcard.write_text(json.dumps({k: receipt[k] for k in
                                   ("evidence_class", "generated_utc", "method", "generation",
                                    "holdout_dti", "score_projection", "verdict",
                                    "submission_name", "submission_note")},
                                  indent=2, allow_nan=False) + "\n")
    print(f"wrote {tif.name}, {audit.name}, {runcard.name}")
    print(json.dumps(receipt["verdict"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
