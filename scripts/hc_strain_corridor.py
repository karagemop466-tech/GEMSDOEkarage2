#!/usr/bin/env python3
"""H-C seismicity-aligned strain-rate corridor (experiment E1, 2026-10-31).

Pre-registered before any run (no parameter was tuned against the holdout):

  Layers   : geod_shearrate (band 7, GPS/InSAR-derived shear rate) and ieq_n100a15
             (band 16, earthquake intensity/density), both from the local
             training_features.tif (19 bands, EPSG:32611, 100 m).
  Signal   : S = z(bright-ridge response of shear rate, Hessian scales 1.5 and 3 px)
             + z(log1p(ieq)). Equal weights. Within the footprint eroded by 3 px.
  Dots     : local maxima of S in a 3x3 window (ridge centrelines), top N = 30,000 by S.
  Catalogue: no dot within 2 px (200 m) of catalogue faults. In the holdout only the
             VISIBLE catalogue is used (hide-and-recover; buffer 3 px).
  Output   : binary raster, 1.0 at dots, 0.0 inside the footprint, NaN outside
             (the organizer sample's exterior convention).

Footprint = labels.tif != -1. This equals the organizer sample's finite set (5,167,373 px).

Usage:
  .venv/bin/python scripts/hc_strain_corridor.py --out docs/downloads/<name>.tif
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import evaluate_holdout as eh  # noqa: E402
import submission_writer as sw  # noqa: E402

DATA = ROOT / ".cache" / "competition_data"
REGISTRY_DIR = ROOT / ".cache" / "registry"

N_DOTS = 30000
FLANK_PX = 2
BAND_SHEAR = 7       # geod_shearrate (1-based band index)
BAND_IEQ = 16        # ieq_n100a15


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def zscore(a: np.ndarray, mask: np.ndarray) -> np.ndarray:
    v = a[mask]
    mu, sd = float(v.mean()), float(v.std())
    out = np.zeros_like(a, dtype=np.float64)
    out[mask] = (a[mask] - mu) / (sd if sd > 0 else 1.0)
    return out


def ridge_response(field: np.ndarray, sigma: float) -> np.ndarray:
    """Bright-ridge measure: max(-lambda_min, 0) of the scale-normalised Hessian."""
    hxx = ndimage.gaussian_filter(field, sigma, order=(0, 2))
    hyy = ndimage.gaussian_filter(field, sigma, order=(2, 0))
    hxy = ndimage.gaussian_filter(field, sigma, order=(1, 1))
    tmp = np.sqrt((hxx - hyy) ** 2 + 4.0 * hxy ** 2)
    lam_min = 0.5 * (hxx + hyy - tmp)
    return np.maximum(-lam_min, 0.0) * sigma ** 2


def load_inputs(data_dir: Path = DATA):
    import rasterio

    with rasterio.open(data_dir / "training_features.tif") as s:
        shear = s.read(BAND_SHEAR).astype(np.float64)
        ieq = s.read(BAND_IEQ).astype(np.float64)
        nodata = s.nodata
        transform = s.transform
        crs = s.crs.to_string()
        shape = (s.height, s.width)
        feats_valid = np.isfinite(shear) & (shear != nodata) & np.isfinite(ieq) & (ieq != nodata)
    with rasterio.open(data_dir / "labels.tif") as s:
        labels = s.read(1)
    footprint = labels != -1
    if footprint.sum() != 5167373:
        raise ValueError(f"footprint {int(footprint.sum())} != 5167373 (GEMSDOE32 audit / sample)")
    return {
        "shear": shear, "ieq": ieq, "labels": labels, "footprint": footprint,
        "feats_valid": feats_valid, "transform": transform, "crs": crs, "shape": shape,
    }


def candidate_components(inp: dict) -> dict:
    """Catalogue-free part of the candidate: the signal map and its ridge-centreline dots."""
    fp = inp["footprint"]
    fill_shear = np.where(fp, inp["shear"], float(np.median(inp["shear"][fp])))
    ridge = np.maximum(ridge_response(fill_shear, 1.5), ridge_response(fill_shear, 3.0))
    seis = np.where(fp, np.log1p(np.where(fp, np.maximum(inp["ieq"], 0.0), 0.0)), 0.0)
    inner = ndimage.binary_erosion(fp, iterations=3)
    ridge_z = zscore(ridge, inner)
    seis_z = zscore(np.where(fp, seis, 0.0), inner)
    score = np.where(inner, ridge_z + seis_z, -np.inf)
    local_max = (score == ndimage.maximum_filter(score, size=3)) & inner
    cand = np.where(local_max, score, -np.inf)
    flat = cand.ravel()
    k = min(N_DOTS, int(np.isfinite(flat).sum()))
    pool = np.zeros(score.shape, dtype=bool)
    pool.flat[np.argpartition(flat, -k)[-k:]] = True
    pool &= np.isfinite(cand)
    return {"ridge": ridge, "seis": seis_z, "score": np.where(inner, score, 0.0),
            "pool": pool, "inner": inner}


def dots_for_catalogue(comp: dict, catalogue_positive: np.ndarray) -> np.ndarray:
    """Apply the 2 px flank exclusion against the given catalogue positives."""
    if catalogue_positive.any():
        dist_px = ndimage.distance_transform_edt(~catalogue_positive)
        far = dist_px > FLANK_PX
    else:
        far = np.ones(catalogue_positive.shape, dtype=bool)
    return comp["pool"] & far


def to_raster(dots: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    out = np.full(dots.shape, np.nan, dtype=np.float32)
    out[footprint] = 0.0
    out[dots & footprint] = 1.0
    return out


def holdout(inp: dict, comp: dict, flank_on: bool = True) -> dict:
    fp = inp["footprint"]
    gt = (inp["labels"] == 1) & fp
    folds = eh.make_quadrant_folds(*fp.shape)

    def build(visible, i):
        dots = dots_for_catalogue(comp, visible) if flank_on else comp["pool"]
        return np.where(fp, dots.astype(np.float64), 0.0)

    res = eh.pooled_dti_hide_and_recover(build, gt, folds, pixel_size_m=100.0,
                                         buffer_px=3.0, alpha=0.2, beta=0.8, R_m=300.0)
    res["evaluator_sha256"] = sha256_file(ROOT / "scripts" / "evaluate_holdout.py")
    res["withheld_positive_pixels"] = res["n_withheld_total"]
    res["ci95_status"] = ("NOT COMPUTED: 4 spatial quadrants give only a fold range; "
                          "fold_range is reported instead of a 95% CI")
    return res


def leakage_canary(inp: dict, comp: dict, features: dict[str, np.ndarray]) -> dict:
    """AUC of each feature alone for withheld catalogue positives vs the same blocks' background."""
    fp = inp["footprint"]
    gt = (inp["labels"] == 1) & fp
    folds = eh.make_quadrant_folds(*fp.shape)
    block_any = np.logical_or.reduce(folds)
    pos = gt & block_any
    neg = fp & block_any & ~gt
    out = {}
    for name, arr in features.items():
        y = np.concatenate([np.ones(int(pos.sum())), np.zeros(int(neg.sum()))])
        x = np.concatenate([arr[pos], arr[neg]])
        x = np.nan_to_num(x.astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
        auc = float(roc_auc_score(y, x))
        out[name] = {"auc": round(auc, 6), "auc_folded_abs": round(max(auc, 1 - auc), 6),
                     "leak_flag": bool(max(auc, 1 - auc) > 0.90)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="output GeoTIFF path (.tif)")
    ap.add_argument("--name", required=True)
    ap.add_argument("--note", required=True)
    ap.add_argument("--card", required=True, help="run-card JSON output path")
    ap.add_argument("--registry", default=str(REGISTRY_DIR))
    args = ap.parse_args()
    if len(args.note) > 140:
        raise SystemExit("note exceeds 140 characters")

    inp = load_inputs()
    comp = candidate_components(inp)
    fp = inp["footprint"]
    gt_full = (inp["labels"] == 1) & fp

    # --- holdout (protocol) and flank-agnostic diagnostic ----------------------------
    ho = holdout(inp, comp, flank_on=True)
    ho_noflank = holdout(inp, comp, flank_on=False)

    # --- leakage canary, each feature alone ------------------------------------------
    with rasterio.open(DATA / "training_features.tif") as s:
        all_bands = {f"band{i}": s.read(i).astype(np.float64) for i in range(1, s.count + 1)}
        names = [d.split(" - ")[0] for d in s.descriptions]
    canary_feats = {f"{names[i-1]}": all_bands[f"band{i}"] for i in range(1, 20)}
    canary_feats["hc_ridge"] = comp["ridge"]
    canary_feats["hc_seis_ieq"] = comp["seis"]
    canary_feats["hc_score"] = comp["score"]
    canary = leakage_canary(inp, comp, canary_feats)
    max_auc_name = max(canary, key=lambda k: canary[k]["auc_folded_abs"])

    # --- final dots (no visible restriction: full catalogue used for flank exclusion) --
    dots = dots_for_catalogue(comp, gt_full)
    raster = to_raster(dots, fp)
    n_dots = int(dots.sum())
    n_on_or_near_cat = int((ndimage.distance_transform_edt(~gt_full)[dots] <= FLANK_PX).sum())
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    receipt = sw.write_submission(raster, out_path, template_meta=sw.read_template(DATA / "sample_submission.tif"),
                                  nodata=None)

    # --- validator (shared writer) against the full registry ------------------------------
    refs = sorted(str(p) for p in Path(args.registry).glob("*.tif"))
    val = sw.validate_geotiff(out_path, template_meta=sw.read_template(DATA / "sample_submission.tif"),
                              reference_rasters=refs, footprint_mask=fp)
    overlaps = {}
    rhos = {}
    with rasterio.open(out_path) as s:
        cand = s.read(1)
    cand_dots = cand > 0
    for r in refs:
        with rasterio.open(r) as s:
            rd = s.read(1)
        if rd.shape != cand.shape:
            continue
        rd_dots = np.nan_to_num(rd, nan=0.0) > 0
        overlaps[Path(r).name] = round(float(sw._dot_overlap_3px(cand_dots, rd_dots)), 6)
        rhos[Path(r).name] = round(float(sw._spearman(np.nan_to_num(cand, nan=0.0), np.nan_to_num(rd, nan=0.0))), 6)
    max_overlap = max(overlaps.items(), key=lambda kv: kv[1]) if overlaps else (None, None)
    max_rho = max(rhos.items(), key=lambda kv: abs(kv[1])) if rhos else (None, None)

    uniq_checks = [c for c in val.checks if c["check"].startswith(("surface_", "dots_within_"))]
    format_pass = all(c["passed"] for c in val.checks if c not in uniq_checks and c["check"] != "uniqueness_vs_registry")
    uniq_pass = bool(uniq_checks) and all(c["passed"] for c in uniq_checks)
    canary_pass = not any(v["leak_flag"] for v in canary.values())
    # Promotion also needs a same-evaluator holdout win over an incumbent; none can be produced here,
    # so every outcome of this experiment is negative for submission purposes.
    verdict = "negative"

    card = {
        "schema": "gems.run_card.v1",
        "experiment": "E1",
        "lane": "H-C seismicity-aligned strain-rate corridor",
        "hypothesis": ("Blind active structure produces a shear-rate ridge that co-locates with "
                       "earthquake intensity; ridge centrelines off the catalogue are fault candidates."),
        "mechanism": ("Bright-ridge (Hessian) response of GPS/InSAR shear rate at 150 m and 300 m scales, "
                      "plus earthquake intensity density; 30,000 ridge-centreline maxima; 2 px catalogue flank exclusion."),
        "non_fault_mimic": ("Interpolation or smoothing seams of the geodetic shear-rate product, and "
                            "seismicity clustered at mining or injection sites rather than on faults."),
        "pre_registration": "Parameters fixed in the module docstring before the first run; not tuned on the holdout.",
        "holdout": {
            "label": "HOLDOUT-DTI",
            "evaluator": "scripts/evaluate_holdout.py::pooled_dti_hide_and_recover (fixed 2026-10-31)",
            "evaluator_sha256": ho["evaluator_sha256"],
            "alpha": 0.2, "beta": 0.8, "R_m": 300.0, "buffer_px": 3.0,
            "pooled_DTI": ho["pooled_DTI"],
            "withheld_positive_pixels": ho["withheld_positive_pixels"],
            "fold_DTIs": ho["fold_DTIs"],
            "fold_range": ho["fold_range"],
            "ci95": ho["ci95_status"],
            "diagnostic_flank_exclusion_off": {"pooled_DTI": ho_noflank["pooled_DTI"], "TPw": ho_noflank["TPw"],
                                               "FPw": ho_noflank["FPw"], "FNw": ho_noflank["FNw"]},
            "note": ("The holdout truth is the catalogue. The leaderboard evidence (0.2600 to 0.2778 by removing "
                     "catalogue-flank dots) points the other way, so this proxy cannot certify leaderboard performance."),
        },
        "leakage_canary": {"threshold_auc": 0.90, "max_feature": max_auc_name,
                           "max_auc_folded": canary[max_auc_name]["auc_folded_abs"], "features": canary,
                           "pass": canary_pass},
        "uniqueness": {
            "registry_dir": str(Path(args.registry).relative_to(ROOT)) if Path(args.registry).is_relative_to(ROOT) else args.registry,
            "registry_rasters_checked": len(overlaps),
            "max_dots_within_3px": {"file": max_overlap[0], "value": max_overlap[1]},
            "max_abs_spearman": {"file": max_rho[0], "value": max_rho[1]},
            "limit_dots_within_3px": 0.70, "limit_spearman": 0.90,
            "pass": uniq_pass,
            "full_440_registry_checked": False,
            "overlaps_by_file": overlaps,
            "spearman_by_file": rhos,
        },
        "raster": {
            "file": str(out_path.relative_to(ROOT)),
            "sha256": sha256_file(out_path),
            "bytes": out_path.stat().st_size,
            "n_dots": n_dots,
            "n_dots_within_2px_of_catalogue": n_on_or_near_cat,
        },
        "validator": {
            "message": val.message,
            "format_pass": format_pass,
            "checks": val.checks,
            "range_contract": "float32; in-footprint values in {0,1}; NaN outside footprint",
        },
        "submission": {"name": args.name, "note": args.note, "note_chars": len(args.note)},
        "exterior": "nan",
        "footprint": {
            "definition": "labels.tif != -1 (equals the organizer sample's finite set)",
            "pixels": int(fp.sum()),
            "finite_mask_sha256": hashlib.sha256(np.packbits(np.isfinite(raster)).tobytes()).hexdigest(),
        },
        "ok_to_submit": False,
        "approved_for_weekly_slot": False,
        "slot_authorized": False,
        "verdict": verdict,
        "verdict_reason": ("FAIL CLOSED: uniqueness/format gates and holdout are reported above. No organizer "
                           "receipt exists, so no leaderboard estimate is claimed. Promotion needs a "
                           "same-evaluator holdout win over an incumbent, which this session cannot produce."),
        "irregularities": [
            "labels.tif is byte-identical to existing_faults.tif (sha256 7ba308cc...).",
            "The owner-mirror sample_submission.tif has the same 60,988 positives as labels.tif; the official "
            "page says the example predicts total fault absence.",
            "pooled_dti_hide_and_recover over-counted false positives before 2026-10-31 (fixed; regression-tested).",
        ],
    }
    Path(args.card).write_text(json.dumps(card, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"verdict": verdict, "pooled_DTI": ho["pooled_DTI"], "n_dots": n_dots,
                      "uniq_pass": uniq_pass, "canary_pass": canary_pass, "max_overlap": max_overlap,
                      "max_rho": max_rho, "validator": val.message}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
