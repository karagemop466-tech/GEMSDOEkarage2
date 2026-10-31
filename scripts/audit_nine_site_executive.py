#!/usr/bin/env python3
"""Measure the nine focus-site best files on their pinned bytes (2026-10-31 executive audit).

Inputs (all SHA-pinned, all fetched from GitHub at the pinned ref):
  * .cache/focus/<file>.tif        -- nine best files (sha256 must equal docs/evidence/nine_site_best_files_audit.json)
  * .cache/competition_data/sample_submission.tif  -- official-grid template (sha 2176d08e...)
  * .cache/competition_data/labels.tif             -- USGS catalogue faults (sha 7ba308cc...)
  * .cache/registry/.../r13-lattice-s5 raster      -- registry raster, looked up in registry/focus_registry_manifest.json

Outputs: docs/evidence/nine-site-executive-20261031.json (tracked evidence; not a leaderboard score).

Every number is labelled by its source. Catalogue DTI is REPORT-ONLY: the official problem page
says the scored target is NEW faults not in the USGS database, so catalogue recovery is not a
leaderboard estimate.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate_holdout import dti_weighted_terms  # noqa: E402  (shared evaluator)
from check_uniqueness import read_tif  # noqa: E402  (shared reader)

OUT = ROOT / "docs/evidence/nine-site-executive-20261031.json"
PINNED = ROOT / "docs/evidence/nine_site_best_files_audit.json"
MANIFEST = ROOT / "registry/focus_registry_manifest.json"
SAMPLE = ROOT / ".cache/competition_data/sample_submission.tif"
LABELS = ROOT / ".cache/competition_data/labels.tif"
LATTICE_NAME = "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    pinned = json.loads(PINNED.read_text())
    man = json.loads(MANIFEST.read_text())
    lat_row = [r for r in man["rasters"] if r["path"].endswith(LATTICE_NAME) and r.get("status") == "ok"]
    if len(lat_row) != 1:
        raise SystemExit("lattice row not uniquely identified in manifest")
    lat_path = ROOT / lat_row[0]["local"]
    if sha256(lat_path) != lat_row[0]["sha256"]:
        raise SystemExit("lattice raster hash mismatch")

    tmpl, tmask, tgrid = read_tif(SAMPLE)
    foot = np.isfinite(tmpl) & (tmask > 0)
    ref_lat, _, _ = read_tif(lat_path, expected_grid=tgrid)
    lat_dots = (ref_lat > 0) & foot
    lat_halo = ndimage.distance_transform_edt(~lat_dots) <= 3.0
    lab, _, _ = read_tif(LABELS, expected_grid=tgrid)
    catalogue = (lab == 1) & foot
    gt = (lab != 0) & foot
    cat_halo = ndimage.distance_transform_edt(~catalogue) <= 3.0
    sample_tf = list(rasterio.open(SAMPLE).transform)[:6]

    rows = []
    for s in pinned["sites"]:
        local = ROOT / ".cache/focus" / Path(s["file"]).name
        file_sha = sha256(local)
        assert file_sha == s["sha256"], f"{s['site']} hash mismatch"
        with rasterio.open(local) as ds:
            a = ds.read(1).astype(np.float64)
            grid_ok = (ds.crs.to_string() == "EPSG:32611" and ds.shape == tmpl.shape
                       and list(ds.transform)[:6] == sample_tf)
            dtype = ds.dtypes[0]
            count = ds.count
        inside = a[foot]
        outside = a[~foot]
        finite_in = bool(np.isfinite(inside).all())
        in_range = bool(finite_in and inside.min() >= 0.0 and inside.max() <= 1.0)
        dots = (a > 0) & foot
        n_dots = int(dots.sum())
        p = np.where(foot, np.nan_to_num(a, nan=0.0), 0.0)
        cat = dti_weighted_terms(p, gt)
        rows.append({
            "site": s["site"],
            "leaderboard_name": s["leaderboard_name"],
            "reported_score_USER_REPORTED_UNVERIFIED": s["user_reported_value_not_verified"],
            "file": s["file"],
            "github_ref": s["github_ref"],
            "sha256": file_sha,
            "sha256_matches_pinned_github_bytes": True,
            "format": {
                "bands": count, "dtype": dtype, "crs_and_grid_match_official_template": bool(grid_ok),
                "nan_inside_footprint": int(np.isnan(inside).sum()),
                "finite_inside_footprint_in_0_1": in_range,
                "outside_footprint_values": "NaN" if np.isnan(outside).all() else
                    ("zeros" if np.all(outside[np.isfinite(outside)] == 0) else "mixed"),
                "outside_nan_count": int(np.isnan(outside).sum()),
            },
            "dots_inside_footprint": n_dots,
            "dots_within_3px_of_registry_lattice_r13": int((dots & lat_halo).sum()),
            "fraction_dots_within_3px_of_registry_lattice_r13": round(float((dots & lat_halo).sum()) / max(n_dots, 1), 6),
            "dots_on_usgs_catalogue": int((dots & catalogue).sum()),
            "dots_within_3px_of_usgs_catalogue": int((dots & cat_halo).sum()),
            "fraction_dots_within_3px_of_usgs_catalogue": round(float((dots & cat_halo).sum()) / max(n_dots, 1), 6),
            "catalogue_proxy_DTI_REPORT_ONLY": round(cat["DTI"], 6),
            "catalogue_proxy_evaluator": "scripts/evaluate_holdout.py::dti_weighted_terms (alpha 0.2, beta 0.8, R 300 m)",
            "catalogue_proxy_withheld_positive_pixels": int(gt.sum()),
            "uniqueness_pairwise_within_nine_pinned_file": pinned["pairwise"] and [
                {"vs": p2["b"] if p2["a"] == s["site"] else p2["a"],
                 "dots_within_3px_overlap_fraction": p2["a_dots_within_3px_of_b"] if p2["a"] == s["site"] else p2["b_dots_within_3px_of_a"],
                 "rho": p2["spearman_footprint"], "fails_70pct_or_rho_0_90": bool(p2["duplicate_flag_overlap_gt_70pct"] or p2["duplicate_flag_rho_gt_0_90"])}
                for p2 in pinned["pairwise"] if s["site"] in (p2["a"], p2["b"])
            ],
            "estimated_leaderboard_score": "UNAVAILABLE - no validated estimator; the catalogue proxy ranks the top reported file near the bottom",
        })

    top = max(rows, key=lambda r: r["reported_score_USER_REPORTED_UNVERIFIED"])

    # Observational association (n = 9, user-reported scores). NOT causal, NOT a projection.
    from scipy.stats import spearmanr
    reported = [r["reported_score_USER_REPORTED_UNVERIFIED"] for r in rows]
    halo = [r["fraction_dots_within_3px_of_usgs_catalogue"] for r in rows]
    rho, pval = spearmanr(reported, halo)

    # Same halo measurement for the HM1 research file (not a score, not a candidate for upload).
    hm1_path = ROOT / "docs/downloads/gemsdoekarage2-hm1-offcat-magridge-35079-20261031-DO-NOT-SUBMIT.tif"
    hm1, _, _ = read_tif(hm1_path, expected_grid=tgrid)
    hm1_dots = (hm1 > 0) & foot
    hm1_halo_frac = float((hm1_dots & cat_halo).sum()) / max(int(hm1_dots.sum()), 1)
    hm1_lat_frac = float((hm1_dots & lat_halo).sum()) / max(int(hm1_dots.sum()), 1)
    doc = {
        "schema_version": 1,
        "generated_by": "scripts/audit_nine_site_executive.py",
        "purpose": "Measured audit of the nine focus-site best files on pinned bytes. Not a leaderboard score.",
        "template_sha256": sha256(SAMPLE),
        "labels_sha256": sha256(LABELS),
        "lattice_registry_raster": {"path": lat_row[0]["path"], "repo": lat_row[0]["repo"], "sha256": lat_row[0]["sha256"],
                                    "dots_in_footprint": int(lat_dots.sum()),
                                    "footprint_cells_within_3px_of_lattice_fraction": round(float((lat_halo & foot).sum()) / foot.sum(), 6),
                                    "footprint_cells_outside_lattice_halo": int((foot & ~lat_halo).sum())},
        "footprint_cells": int(foot.sum()),
        "top_reported_file": top["site"],
        "sites": rows,
        "association_observed_not_causal": {
            "statistic": "Spearman rho, reported score vs fraction of dots within 3 px of USGS catalogue",
            "n": len(rows), "rho": round(float(rho), 4), "p_value": round(float(pval), 6),
            "caveat": "Reported scores are USER-REPORTED / UNVERIFIED; n = 9; association only. Extrapolating beyond the observed range is a projection, not a score.",
        },
        "reference_HM1_research_file": {
            "file": hm1_path.name, "dots": int(hm1_dots.sum()),
            "fraction_dots_within_3px_of_usgs_catalogue": round(hm1_halo_frac, 6),
            "fraction_dots_within_3px_of_registry_lattice_r13": round(hm1_lat_frac, 6),
            "status": "DO NOT SUBMIT - DUPLICATE_STOP (see docs/evidence/hm1/)",
        },
        "verdict_summary": {
            "any_file_passes_literal_uniqueness_gate": False,
            "reason": "All nine files place dots inside the 13GEMSDOE lattice 3-px halo at >= 99%; see fraction_dots_within_3px_of_registry_lattice_r13.",
            "upload_authorized": False,
        },
    }
    OUT.write_text(json.dumps(doc, indent=2, allow_nan=False) + "\n")
    print(json.dumps({r["site"]: [r["fraction_dots_within_3px_of_registry_lattice_r13"], r["catalogue_proxy_DTI_REPORT_ONLY"]] for r in rows}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
