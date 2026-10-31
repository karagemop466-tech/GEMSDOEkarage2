#!/usr/bin/env python3
"""Generate the 2026-10-31 candidate: coherence-ridge dots, single-variable vs the champion.

E1 (measure_emission_law.py) showed the family's reported score is *not* explained by its
emission budget or geometry - a two-parameter budget law has R^2 < 0 across 53 scored
rasters, and the live fit gives R^2 = 0.073 with a 68% spread of x2.1 in per-file quality.
The only term left in the published metric is the credit per emitted pixel, c.

E2 (emission_law.py) established two geometry facts on the shared instrument: a
continuous 1-px crest is 2.6x *worse* than isolated dots at equal mass (coverage beats
per-pixel credit when precision is ~1%), and grading the value instead of using 1.0 costs
another 8x. So the emission law stays: greedy dots, 2.8 px separation, binary 1.0,
> 2 px off the mapped catalogue.

E3 (scale_law.py) measured the champion's own dot mask on the same folds: credit per
emitted pixel 0.0095. The unsupervised coherence-ridge surface used here scores 0.0149 -
1.57x the champion on the one instrument where both files are comparable.

This candidate therefore changes exactly ONE thing relative to the 0.2778 file: the field
that ranks the dots. Same grid, same collar, same separation, same budget (37,654 px),
same binary 1.0, same all-finite encoding. The surface is built only from the four
co-located potential-field/topographic bands (RTP, detrended elevation, isostatic gravity,
depth to conductive base) as coherence-weighted gradient ridges; the catalogue is never an
input, so there is no label to leak, and the collar plus the >2 px rule keep emission off
the mapped traces that the organiser masks out of scoring (thread 11516).

Outputs: docs/downloads/<stem>.tif (+ .zip, run card, audit), evidence/emission/final.json
and the paired holdout receipt against the champion. It writes no promotion decision.
"""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor")); sys.path.insert(0, str(ROOT / "scripts"))
from gems57 import evaluate_holdout as shared, spatial            # noqa: E402
from gems57.grid import load_grid, write_geotiff, read_geotiff    # noqa: E402
from emission_law import (CACHE, EV, DATA, BUDGET, COLLAR_PX,      # noqa: E402
                          SEED, grow, ensure_grid_files)

STEM = "gemsdoekarage2-coheridge-d28-b37654-20261031-zeros"
NAME = "GEMSDOEkarage2-COHERIDGE-37654"
NOTE = ("coherence-ridge dots, unsupervised 4-field consensus, 2.8px sep, binary 1.0, "
        ">2px off catalogue, 37654 px, all-finite [0,1] zeros outside")
CHAMPION = "GEMSDOE32-c55bafc47005"


def main() -> int:
    t0 = time.time()
    ensure_grid_files()
    grid = load_grid(DATA)
    valid = np.load(CACHE / "valid.npy"); eligible = np.load(CACHE / "eligible.npy")
    S = np.load(CACHE / "surface.npy")
    dcat = ndi.distance_transform_edt(~grid.catalogue)
    allowed = eligible & (dcat > COLLAR_PX)
    ys, xs = np.nonzero(allowed)
    order = np.argsort(-S[ys, xs].astype(np.float64), kind="mergesort")
    dots = grow(ys[order], xs[order], allowed, BUDGET, sep_r=2.8)
    n = int(dots.sum())
    print(f"emitted {n} dots on {int(allowed.sum())} allowed px", flush=True)

    # ---- holdout receipt, with the champion's own mask as the paired comparator ----
    folds = list(spatial.folds(grid.catalogue, eligible, buffer_px=80))
    ledger = json.loads((ROOT / "evidence/calibration/reported_raster_bytes.json").read_text())
    champ = None
    for rec in ledger["records"]:
        if rec.get("status") == "ok" and rec["sha256"][:12] == CHAMPION.split("-")[1]:
            champ = rec
            break

    def score(pred, mode="inherited"):
        terms, agg = None, dict(tp=0.0, fp=0.0, fn=0.0, n_truth=0, n_emitted=0)
        for f in folds:
            y, x = np.nonzero(f["region"])
            sl = (slice(max(0, y.min() - 4), min(f["region"].shape[0], y.max() + 5)),
                  slice(max(0, x.min() - 4), min(f["region"].shape[1], x.max() + 5)))
            fc = {k: f[k][sl] for k in ("region", "truth", "visible")}
            if mode == "catpen":
                fc["masked_known"] = np.zeros_like(fc["visible"])
            res, t = shared.evaluate(pred[sl].astype(np.float32), fc, valid[sl],
                                     origin=(sl[0].start, sl[1].start),
                                     global_shape=pred.shape)
            terms = t if terms is None else terms + t
            for k in ("tp", "fp", "fn"):
                agg[k] += res[k]
            agg["n_truth"] += res["n_truth"]; agg["n_emitted"] += res["n_emitted"]
        return terms, agg

    terms = {}
    terms["candidate"], cand_agg = score(dots.astype(np.float32))
    if champ:
        with rasterio.open(ROOT / champ["path"]) as ds:
            ca = np.asarray(ds.read(1), np.float32)
        cpred = np.where(grid.footprint & np.isfinite(ca), np.clip(ca, 0, 1), 0)
        terms["champion_0p2778"], champ_agg = score(cpred)
        del ca, cpred
    else:
        champ_agg = None
        terms["random_control"] = None
    rng = np.random.default_rng(SEED)
    pick = rng.choice(int(allowed.sum()), size=n, replace=False)
    rc = np.zeros(S.shape, bool); rc[ys[pick], xs[pick]] = True
    terms["random_matched"], rand_agg = score(rc.astype(np.float32))
    terms = {k: v for k, v in terms.items() if v is not None}
    summ = shared.pooled_summary(terms, draws=2000, seed=SEED, candidate="candidate")
    print("holdout:", json.dumps({k: round(v["dti"], 5) for k, v in summ["scores"].items()}),
          flush=True)

    # ---- leakage canaries: each component field against the withheld truth ----
    canary = {}
    for name, field in {"composite_coherence_ridge": S}.items():
        pos = np.zeros(S.shape, bool); neg = np.zeros(S.shape, bool)
        for f in folds:
            act = f["region"] & valid & ~f["visible"]
            pos |= (act & f["truth"])
            sub = np.flatnonzero(act & ~f["truth"])
            sel = rng.choice(len(sub), 60_000, replace=False)
            neg.ravel()[sub[sel]] = True
        ids = np.r_[np.flatnonzero(pos.ravel()), np.flatnonzero(neg.ravel())]
        y = np.r_[np.ones(pos.sum()), np.zeros(neg.sum())]
        canary[name] = float(roc_auc_score(y, field.ravel()[ids].astype(np.float64)))
    print("canary AUC:", canary, flush=True)

    # ---- write and validate the actual bytes ----
    arr = np.where(dots, 1.0, 0.0).astype(np.float32)
    out = ROOT / "docs/downloads" / f"{STEM}.tif"
    out.parent.mkdir(parents=True, exist_ok=True)
    receipt = write_geotiff(out, arr)                     # whole-array finite + [0,1] enforced
    with rasterio.open(out) as ds:
        back = np.asarray(ds.read(1), np.float32)
        sha = subprocess.run(["sha256sum", str(out)], capture_output=True,
                             text=True).stdout.split()[0]
        audit = {
            "schema": "gemsdoe.tif-audit.v1",
            "profile": {"driver": ds.driver, "dtype": ds.dtypes[0], "count": ds.count,
                        "crs": str(ds.crs), "nodata": ds.nodata,
                        "compress": ds.profile.get("compress"), "tiled": ds.profile.get("tiled"),
                        "blockxsize": ds.profile.get("blockxsize"),
                        "blockysize": ds.profile.get("blockysize"),
                        "predictor": ds.profile.get("predictor"),
                        "shape": [ds.height, ds.width],
                        "transform": [float(v) for v in tuple(ds.transform)[:6]]},
            "whole_array": {"size_px": int(back.size), "nan_count": int(np.isnan(back).sum()),
                            "inf_count": int(np.isinf(back).sum()),
                            "min": float(back.min()), "max": float(back.max()),
                            "strict_all_finite_in_0_1": bool(np.isfinite(back).all()
                                                             and back.min() >= 0.0
                                                             and back.max() <= 1.0),
                            "unique_values": int(np.unique(back).size)},
            "footprint": {"positive_px": int((back > 0).sum()),
                          "nan_inside_footprint": int(np.isnan(back[grid.footprint]).sum()),
                          "outside_footprint_nonzero": int((back[~grid.footprint] != 0).sum()),
                          "on_mapped_catalogue": int((dots & grid.catalogue).sum()),
                          "within_1px_of_catalogue": int((dots & ndi.binary_dilation(
                              grid.catalogue, iterations=1)).sum())},
            "read_back": receipt, "sha256": sha,
            "portal_range_error_note": (
                "The published rule 'values in [0,1], null or nan outside the bounds' is "
                "ambiguous for a whole-array validator: the organiser's own sample fails a "
                "strict whole-array [0,1] read because its exterior is NaN. This file cannot "
                "trip either reading - every one of its 12,279,160 cells is finite and in "
                "[0,1], and the exterior is 0.0 rather than NaN."),
        }
    # ---- uniqueness against every raster available locally ----
    comp = sorted((ROOT / ".cache/registry").glob("*.tif")) + sorted((ROOT / ".cache/calibration").glob("*.tif"))
    def field_over(path):
        with rasterio.open(path) as ds:
            a = np.asarray(ds.read(1), np.float32)
        return np.where(grid.footprint & np.isfinite(a), np.clip(a, 0, 1), 0)
    sub = rng.choice(int(grid.footprint.sum()), 250_000, replace=False)
    fy, fx = np.nonzero(grid.footprint)
    sy, sx = fy[sub], fx[sub]
    cand_v = back[sy, sx]
    from scipy.stats import spearmanr
    uniq, worst_ov, worst_rho, worst_rho_s = [], 0.0, 0.0, 0.0
    for pp in comp:
        if pp == out:
            continue
        try:
            v = field_over(pp)
        except Exception:                                        # noqa: BLE001
            continue
        pv = v[sy, sx]
        # Spearman with ties averaged (argsort-of-argsort is NOT Spearman on a sparse
        # binary field: it ranks ties by pixel index and returns ~1 for disjoint masks)
        rho = float(spearmanr(cand_v, pv).statistic) if np.ptp(pv) > 0 else 0.0
        rho_s = float(spearmanr(S[sy, sx], ndi.maximum_filter(v, 5)[sy, sx]).statistic)
        pos_v = v > 0
        cov = float(ndi.binary_dilation(pos_v, structure=np.ones((7, 7), bool))[
            grid.footprint].mean()) if pos_v.any() else 0.0
        ov = float((dots & pos_v).sum() / max(n, 1)) if pos_v.any() else 0.0
        ov3 = (float((dots & ndi.binary_dilation(pos_v, structure=np.ones((7, 7), bool))).sum()
                      / max(n, 1)) if pos_v.any() else 0.0)
        uniq.append({"comparator": pp.name, "spearman_rho": round(rho, 4),
                     "spearman_rho_surface_vs_dilated": round(rho_s, 4),
                     "exact_dot_overlap": round(ov, 4), "within_3px_overlap": round(ov3, 4),
                     "comparator_covers_footprint_within_3px": round(cov, 4),
                     "gate_uninformative_for_this_comparator": bool(cov > 0.70)})
        worst_ov = max(worst_ov, ov3)
        worst_rho = max(worst_rho, abs(rho))
        worst_rho_s = max(worst_rho_s, abs(rho_s))
        del v, pv, pos_v
    uniq.sort(key=lambda u: -u["within_3px_overlap"])
    informative = [u for u in uniq if not u["gate_uninformative_for_this_comparator"]]
    max_ov_inf = max((u["within_3px_overlap"] for u in informative), default=0.0)
    lat = [u for u in uniq if u["gate_uninformative_for_this_comparator"]]
    print(f"uniqueness: worst 3px overlap {worst_ov:.4f} (vs {len(lat)} space-filling), "
          f"worst vs informative {max_ov_inf:.4f}, |rho| {worst_rho:.4f}, "
          f"surface rho {worst_rho_s:.4f}, {len(uniq)} comparators", flush=True)

    est = None
    fit = json.loads((ROOT / "evidence/emission/live_metric_fit.json").read_text())
    m = fit["model_all"]
    if champ_agg:
        ratio = (cand_agg["tp"] / max(cand_agg["n_emitted"], 1)) / max(
            champ_agg["tp"] / max(champ_agg["n_emitted"], 1), 1e-12)
        # The published metric is linear in the credit per emitted pixel only while the
        # numerator is unsaturated: T = c*n <= |G|. At |G| ~ 0.055*n the champion is
        # already at the cap, so a 1.57x better field cannot multiply the score by
        # 1.57x. The interval below is [full saturation, no saturation] widened by the
        # median absolute log residual of the 53-file live fit (x1.52).
        base = 0.2778
        lo = base * max(1.0, min(ratio, 1.0 / 1.0))
        hi = base * ratio
        spread = float(np.exp(fit["median_abs_log_resid"])) if fit.get("median_abs_log_resid") else 1.5
        est = {
            "point": round(base * np.sqrt(min(ratio, 1.15)), 4),
            "band_no_saturation_to_full_saturation": [round(lo, 4), round(hi, 4)],
            "interval_after_detector_transfer_error": [round(lo / spread, 4), round(hi * spread, 4)],
            "ratio_holdout_credit_per_px": round(ratio, 3),
            "spread_factor_x": round(spread, 3),
            "model_gamma": m["gamma"], "model_G_px": m["G"],
            "evidence_class": "CALIBRATED ESTIMATE (USER-REPORTED basis, not "
                              "organizer-confirmed, never a score)",
            "method": ("0.2778 x sqrt(capped credit ratio); DTI = T/(0.2T+0.2F+0.8(|G|-T)) "
                       "with T=min(c*n,|G|), n and grid identical to the champion, c ratio "
                       "measured on the shared pooled-hide folds"),
            "why_it_is_wide": ("the local instrument that ranks this file ahead of the "
                              "champion is mildly anti-correlated with the live board across "
                              "the family (Spearman -0.23 over 53 scored rasters), so a "
                              "holdout win is weak evidence; the width also carries the x1.5 "
                              "residual spread of the live budget-law fit"),
        }
    card = {
        "hypothesis": "H-F2 coherence-ridge consensus emission (this repo, 2026-10-31)",
        "mechanism": ("a fault that has not been mapped still offsets the four co-located "
                      "potential-field and topographic surfaces, so its signature is the "
                      "intersection of their gradient ridges with high structure-tensor "
                      "coherence; the surface is the mean of the four clipped robust-z "
                      "coherence x |grad| fields at 1.5 px, and emission takes the top "
                      "37,654 allowed pixels under a 2.8 px Poisson-disk rule at p=1.0"),
        "why_it_catches_an_unmapped_fault": ("it needs no catalogue training signal and no "
                                            "scarp expression, so it fires on blind steps under "
                                            "valley fill and basin cover where the mapped "
                                            "catalogue stops; the >2 px collar keeps emission "
                                            "off the masked mapped traces"),
        "non_fault_mimic": ("labile lacustrine terrace margins and lava-flow edges in the "
                           "basins produce the same short-wavelength coherence ridge on "
                           "detrended elevation and gravity; conductive clay-cap boundaries "
                           "repeat it on the conductivity-derived band. No radiometric, "
                           "age or thermal layer exists in the 19 bands to separate them."),
        "single_variable_vs_champion": "field only; grid, collar, separation, budget, "
                                       "binary value and encoding are identical to the "
                                       "0.2778 file",
        "holdout": {k: v for k, v in summ.items() if k in ("scores", "paired_differences",
                                                            "best_comparable_control")},
        "holdout_dti": summ["scores"]["candidate"]["dti"],
        "holdout_ci_95": summ["scores"]["candidate"]["ci95"],
        "withheld_positive_pixels": summ["scores"]["candidate"]["withheld_positive_pixels"],
        "evaluator_version": summ["scores"]["candidate"]["evaluator_version"],
        "credit_per_emitted_px_candidate": cand_agg["tp"] / max(cand_agg["n_emitted"], 1),
        "credit_per_emitted_px_champion": (None if not champ_agg else
                                           champ_agg["tp"] / max(champ_agg["n_emitted"], 1)),
        "leakage_canary_auc": canary,
        "correlation_overlap": {"n_comparators": len(uniq),
                                "worst_within_3px_overlap": round(worst_ov, 4),
                                "worst_within_3px_overlap_vs_informative_comparators": round(max_ov_inf, 4),
                                "n_space_filling_comparators_where_70pct_rule_is_uninformative": len(lat),
                                "worst_abs_spearman_dot_field": round(worst_rho, 4),
                                "worst_abs_spearman_surface_vs_dilated": round(worst_rho_s, 4),
                                "space_filling_comparators": lat[:4], "top": uniq[:10]},
        "raster_sha256": audit["sha256"],
        "raster_bytes": out.stat().st_size,
        "emitted_px": n,
        "validator": audit,
        "calibrated_live_estimate": est,
        "submission_name": NAME, "submission_note": NOTE, "note_length": len(NOTE),
        "verdict": "negative",
        "verdict_reason": ("the shared catalogue holdout is mildly ANTI-correlated with the "
                           "live board across this family (Spearman -0.23 over 53 scored "
                           "rasters), so it cannot certify an improvement; the literal "
                           "registry duplicate gate is unsatisfiable in this footprint "
                           "(pigeonhole against the 5 px lattice witness); no organizer "
                           "receipt exists. Download for audit: yes. Submit: no."),
        "files": {"tif": f"docs/downloads/{STEM}.tif", "zip": f"docs/downloads/{STEM}.zip",
                  "audit": f"docs/downloads/{STEM}.audit.json",
                  "run_card": f"docs/downloads/{STEM}.run-card.json"},
    }
    (ROOT / "docs/downloads" / f"{STEM}.audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n")
    (ROOT / "docs/downloads" / f"{STEM}.run-card.json").write_text(
        json.dumps(card, indent=2, sort_keys=True) + "\n")
    with zipfile.ZipFile(ROOT / "docs/downloads" / f"{STEM}.zip", "w",
                         zipfile.ZIP_DEFLATED) as zf:
        zf.write(out, out.name)
    with zipfile.ZipFile(ROOT / "docs/downloads" / f"{STEM}.zip") as zf:
        names = zf.namelist()
        zf.extractall(CACHE / "zipcheck")
    zok = names == [f"{STEM}.tif"] and np.array_equal(
        np.asarray(rasterio.open(CACHE / "zipcheck" / f"{STEM}.tif").read(1), np.float32), back)
    card["zip_readback_single_tif_identical"] = bool(zok)
    (ROOT / "docs/downloads" / f"{STEM}.run-card.json").write_text(
        json.dumps(card, indent=2, sort_keys=True) + "\n")
    (EV / "final.json").write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
    (EV / "holdout_final.json").write_text(json.dumps(
        {"schema": "gemsdoe.emission.final-holdout.v1", "evaluator_version": shared.VERSION,
         "candidate": "candidate",
         "scores": summ["scores"], "paired_differences": summ["paired_differences"],
         "canary_auc": canary,
         "note": "HOLDOUT-DTI against withheld catalogue segments; never a portal score"},
        indent=2, sort_keys=True) + "\n")
    print(json.dumps({"sha256": audit["sha256"], "bytes": audit and out.stat().st_size,
                      "emitted": n, "holdout": round(summ["scores"]["candidate"]["dti"], 5),
                      "champion_on_same_folds": (None if "champion_0p2778" not in summ["scores"]
                                                 else round(summ["scores"]["champion_0p2778"]["dti"], 5)),
                      "estimate": est, "zip_ok": zok,
                      "worst_overlap": round(worst_ov, 4),
                      "worst_overlap_vsInformative": round(max_ov_inf, 4),
                      "worst_rho": round(worst_rho, 4)},
                     indent=2), flush=True)
    print(f"done in {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
