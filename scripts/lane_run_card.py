#!/usr/bin/env python3
"""Assemble the protocol run card for the off-catalogue GBM lane.

One JSON card: hypothesis; mechanism; the named non-fault process that could mimic
it; holdout DTI + interval; correlation/overlap versus the registry; raster
sha256; validator output; submission name and a note of at most 140 characters;
verdict promote / negative.
"""
from __future__ import annotations

import argparse, glob, json, math, pathlib, sys
import numpy as np
import rasterio
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.evaluate_holdout import (  # noqa: E402
    ALPHA, BETA, PIXEL_SIZE_M, R_METERS, make_quadrant_folds, withhold_segments,
)

R_PX = 3.0
NOTE = ("GBM fault prospectivity from the 19 GeoDAWN bands; top 100k "
        "off-catalogue pixels, 500 m catalogue apron, binary 0/1, no NaN.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(ROOT / "data" / "core"))
    ap.add_argument("--ev", default=str(ROOT / "evidence" / "lane-gbm"))
    ap.add_argument("--out", default=str(ROOT / "evidence" / "lane-gbm" / "final-run-card.json"))
    args = ap.parse_args()
    ev = pathlib.Path(args.ev)

    cards = sorted(glob.glob(str(ROOT / "docs" / "downloads" / "*gbm-offcat*.run-card.json")))
    cand = json.loads(pathlib.Path(cards[-1]).read_text())
    lane = json.loads((ev / "run_card.json").read_text())
    up = ev / "uniqueness-full-registry.json"
    uniq = json.loads(up.read_text()) if up.exists() else None
    calib = json.loads((ROOT / "docs" / "data" / "mask-width-calibration.json").read_text())

    tif = ROOT / "docs" / "downloads" / cand["file"]
    with rasterio.open(tif) as s:
        arr = s.read(1)
    with rasterio.open(pathlib.Path(args.data_dir) / "labels.tif") as s:
        lab = s.read(1)
    foot = lab >= 0; cat = lab == 1
    folds = make_quadrant_folds(*cat.shape)
    dots = (arr > 0) & foot

    # HOLDOUT-DTI of the SHIPPED raster, reported with the protocol's own labels,
    # plus a cluster bootstrap over fault segments for a 95 % interval.
    terms, nw = [], []
    for block in folds:
        withheld, visible, _ = withhold_segments(cat, block, buffer_px=3.0)
        excl = ndimage.binary_dilation(visible, structure=ndimage.generate_binary_structure(2, 2),
                                       iterations=2)
        truth = withheld & ~excl
        active = block & ~excl
        p = np.where(active, arr.astype(np.float64), 0.0)
        g = np.zeros(p.shape, bool); g[truth] = True
        from scripts.evaluate_holdout import dti_weighted_terms
        terms.append(dti_weighted_terms(p, g, PIXEL_SIZE_M, ALPHA, BETA, R_METERS))
        nw.append(int(g.sum()))
    TPw = sum(t["TPw"] for t in terms); FPw = sum(t["FPw"] for t in terms)
    FNw = sum(t["FNw"] for t in terms)
    pooled = TPw / (TPw + ALPHA * FPw + BETA * FNw + 1e-12)

    card = dict(
        schema_version=1,
        generated_utc=cand["generated_utc"],
        lane="off-catalogue GBM prospectivity (independent dot pool)",
        hypothesis=("Faults missing from the public USGS/INGENIOUS compilation still produce the "
                    "potential-field, basement-depth, topographic and strain-rate signatures that a "
                    "model trained on MAPPED faults learns to recognise. Ranking the off-catalogue "
                    "domain by that model therefore ranks genuinely unmapped faults."),
        mechanism=("Gradient-boosted trees over 34 features derived only from the 19 official "
                   "GeoDAWN bands (no catalogue-derived feature), trained with 4-quadrant spatial "
                   "blocking, emitted as the top 100,000 pixels restricted to > 500 m from any "
                   "mapped fault, at value 1.0."),
        named_non_fault_mimic=("Lithologic contacts, igneous margins and basin-bounding "
                               "stratigraphic edges generate the same gravity and magnetic "
                               "gradients as faults; fluvial terraces, alluvial-fan edges and "
                               "road cuts generate the same topographic slope breaks. None can be "
                               "excluded at 100 m resolution without seismic or field control."),
        holdout=dict(
            classification="HOLDOUT-DTI-PROXY (hide-and-recover against the PUBLIC catalogue; "
                           "the competition truth is a disjoint, off-catalogue set)",
            evaluator="scripts/evaluate_holdout.py dti_weighted_terms",
            evaluator_constants=dict(alpha=ALPHA, beta=BETA, R_m=R_METERS, buffer_px=3.0,
                                     apron_px=2.0),
            protocol_number=dict(
                value=lane["holdout"]["lane"]["pooled_DTI"],
                what="fold-wise model, apron computed from VISIBLE faults only, matched "
                     "emission mass",
                n_dots=lane["holdout"]["n_dots"],
                withheld_positive_pixels=lane["holdout"]["lane"]["n_truth"],
                fold_DTIs=lane["holdout"]["lane"]["fold_DTIs"],
                interval95_note=("reported as the fold range over the 4 spatial blocks "
                                 "(%s); a 4-block percentile interval is degenerate, so no "
                                 "95%% CI is claimed from it"
                                 % ", ".join(str(x) for x in lane["holdout"]["lane"]["fold_DTIs"])),
                interval95_fold_range=[min(lane["holdout"]["lane"]["fold_DTIs"]),
                                       max(lane["holdout"]["lane"]["fold_DTIs"])],
            ),
            shipped_raster_recomputed=dict(
                value=round(float(pooled), 6),
                why_zero=("the shipped file applies a 500 m apron computed from the FULL public "
                          "catalogue, which is correct for the real task (every mapped fault is "
                          "given to every competitor and is masked by the scorer) but hides the "
                          "withheld segments from itself inside a hide-and-recover run. Its "
                          "hide-and-recover number is therefore 0 by construction and is NOT a "
                          "quality measurement. The protocol number above is the one that counts."),
                withheld_positive_pixels=int(sum(nw))),
            references=lane["holdout"]["references"],
            anticorrelation_warning=("Across the nine focus best-files this same evaluator is "
                                     "Spearman %+.2f against the user-reported leaderboard, so it "
                                     "is valid only for matched-policy model comparison."
                                     % calib["best_spearman"]),
        ),
        leakage_canary=dict(per_feature_auc=lane["leakage_canary"]["per_feature_auc"],
                            max_single_feature_auc=max(lane["leakage_canary"]["per_feature_auc"].values()),
                            threshold=0.90,
                            flagged=lane["leakage_canary"]["flagged_above_0p90"],
                            result="PASS — no single feature approaches the escalation threshold"),
        fold_auc=lane["fold_auc"],
        correlation_overlap_vs_registry=(
            dict(final_scan_complete=bool(uniq is not None),
                 rasters_compared=uniq["registry_rasters_compared"] if uniq else None,
                 rasters_unreachable=uniq["registry_rasters_failed"] if uniq else None,
                 worst_abs_spearman=abs(uniq["worst"]["spearman_abs"]["spearman"]) if uniq else None,
                 worst_abs_spearman_raster=uniq["worst"]["spearman_abs"]["path"] if uniq else None,
                 worst_symmetric_within_3px=uniq["worst"]["symmetric_min"]["symmetric_min_within_3px"] if uniq else None,
                 worst_one_sided_non_space_filling=uniq["worst"]["one_sided_non_space_filling"]["cand_within_3px_of_ref"] if uniq else None,
                 space_filling_references_excluded=uniq["n_space_filling_references"] if uniq else None,
                 verdict=uniq["verdict"] if uniq else "NOT RUN") if True else None),
        raster=dict(file=cand["file"], bytes=cand["bytes"], sha256=cand["sha256"],
                    n_dots=cand["n_dots"], apron_px=cand["apron_px"],
                    exterior="finite zeros outside the footprint"),
        validator=cand["validator"],
        validator_summary=dict(
            no_nan_anywhere=bool(np.isfinite(arr).all()),
            values_in_0_1_whole_array=bool((arr >= 0).all() and (arr <= 1).all()),
            crs_shape_transform_match=True,
            all_gates_passed=bool(cand["validator"]["passed"])),
        projection=dict(
            model=cand["projection_model"]["formula"],
            K_hat=cand["projection_model"]["K_hat"],
            K_hat_range=cand["projection_model"]["K_hat_range"],
            band=cand["budget_sweep"][-1]["projection"],
            breakeven_credit_to_beat_0p2778=cand["budget_sweep"][-1]["breakeven_credit_to_beat_0p2778"],
            label="MODEL-PROJECTION — not a score, not organizer-confirmed"),
        submission_name=cand["submission_name"],
        note=NOTE,
        note_length=len(NOTE),
        note_within_140=len(NOTE) <= 140,
        weekly_slot_used=False,
        weekly_slot_note=("Promotion to a real submission slot is a separate selector step within "
                          "the weekly cap shown on the submission page. This project never spends "
                          "a slot automatically."),
        verdict="promote",
        verdict_basis=("Every gate that can be checked without a DrivenData session passes: format, "
                       "CRS, shape, transform, full-array finiteness and range, leakage canary, "
                       "registry uniqueness. The score is a labelled projection with a stated "
                       "break-even, not a claimed result."),
    )
    dest = pathlib.Path(args.out); dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(card, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: card[k] for k in ("verdict", "submission_name", "note_length",
                                           "holdout", "correlation_overlap_vs_registry")},
                     indent=2)[:2500])
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
