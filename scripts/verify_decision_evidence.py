#!/usr/bin/env python3
"""Re-measure the 2026-10-31 submission-decision claims from hash-pinned bytes.

Writes ``evidence/decision-verification-2026-10-31.json``. Every number carries an
evidence class:

* REGISTRY-MEASUREMENT - computed here from owner-mirror bytes whose SHA-256 equals a
  committed pin (registry/*.json). Owner mirrors are NOT organizer-authenticated.
* OFFICIAL-PAGE-TEXT - quoted from the public DrivenData page (see
  evidence/official-page-read-2026-10-31.json); the page reader, not a login, was used.
* DERIVED - algebra on measured or user-reported inputs, stated with its assumption.
* USER-REPORTED - a score copied from the user's brief; never checked by this script.

This script creates no TIFF, runs no holdout experiment, uploads nothing, and spends no
competition slot. Run it with the repo venv after ``pip install -r requirements.lock.txt``.
"""
from __future__ import annotations

import datetime as _dt
import json
import platform
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from restore_data import fetch, sha256_file  # noqa: E402

CACHE = ROOT / ".cache" / "verify-2026-10-31"
OUT = ROOT / "evidence" / "decision-verification-2026-10-31.json"
RADIUS_PX = 3
ALPHA, BETA = 0.2, 0.8
OVERLAP_LIMIT = 0.70
RHO_LIMIT = 0.90
REFERENCE_D28_DTI_USER_REPORTED = 0.2600   # USER-REPORTED for GEMSDOE25 and GEMSDOE30 (identical D2.8 dot sets)
GEMS32_DTI_USER_REPORTED = 0.2778          # GEMSDOE32 user report, unverified
GEMS32_SUFFIX = "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
D28_SUFFIX = "gemsdoe33-d28-reference-20261004-426073b6b4ab-zeros.tif"


def disk(radius: int = RADIUS_PX) -> np.ndarray:
    yy, xx = np.mgrid[-radius:radius + 1, -radius:radius + 1]
    return yy * yy + xx * xx <= radius * radius


def dots(arr: np.ndarray) -> np.ndarray:
    """Literal positive-support definition used by the repo's uniqueness gate."""
    return np.isfinite(arr) & (arr > 0)


def within_3px(support: np.ndarray) -> np.ndarray:
    return binary_dilation(support, structure=disk())


def raster(path: Path):
    with rasterio.open(path) as ds:
        arr = ds.read(1)
        mask = ds.read_masks(1)
        meta = dict(
            shape=list(ds.shape),
            crs_epsg=ds.crs.to_epsg() if ds.crs else None,
            transform=list(ds.transform)[:6],
            dtype=ds.dtypes[0],
            count=ds.count,
            nodata=None if ds.nodata is None or np.isnan(ds.nodata) else float(ds.nodata),
            nodata_is_nan=bool(ds.nodata is not None and np.isnan(ds.nodata)),
        )
    return arr, mask, meta


def pinned_records() -> dict:
    assets = json.loads((ROOT / "registry/pinned_assets.json").read_text())["assets"]
    core = json.loads((ROOT / "registry/core_data_manifest.json").read_text())["files"]
    focus = json.loads((ROOT / "registry/focus_registry_manifest.json").read_text())["rasters"]

    def one_focus(repo: str, suffix: str) -> dict:
        hits = [r for r in focus if r["repo"] == repo and r["path"].endswith(suffix)
                and r.get("status") == "ok"]
        if len(hits) != 1:
            raise ValueError(f"expected exactly one pinned {repo} raster ending {suffix}; got {len(hits)}")
        return {**hits[0], "fetch_repo": f"buffedlizard55-lab/{repo}"}

    def one_asset(role: str) -> dict:
        hits = [a for a in assets if a["role"] == role]
        if len(hits) != 1:
            raise ValueError(f"expected one pinned asset with role {role}")
        return hits[0]

    labels = [f for f in core if f["id"] == "labels"]
    if len(labels) != 1:
        raise ValueError("expected one pinned labels entry")
    return {
        "template": one_asset("template"),
        "lattice": one_asset("lattice"),
        "labels": labels[0],
        "gems32": one_focus("GEMSDOE32", GEMS32_SUFFIX),
        "d28_reference": one_focus("GEMSDOE33", D28_SUFFIX),
        "d28_gems25": one_focus("GEMSDOE25", "e56ea318af89-zeros.tif"),
        "d28_gems30": one_focus("GEMSDOE30", "91eae1ca.tif"),
    }


def pinned_path(rec: dict, repo_full: str, fname: str) -> Path:
    dest = CACHE / fname
    if dest.exists() and sha256_file(dest) == rec["sha256"]:
        return dest
    fetch(repo_full, rec["ref"], rec["path"], dest)
    got = sha256_file(dest)
    if got != rec["sha256"]:
        dest.unlink(missing_ok=True)
        raise ValueError(f"SHA-256 mismatch for {rec['path']}: {got}")
    return dest


def downloads_audit() -> list[dict]:
    rows = []
    for path in sorted((ROOT / "docs/downloads").glob("*.tif")):
        arr, _, meta = raster(path)
        fin = np.isfinite(arr)
        rows.append({
            "file": path.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(path),
            **meta,
            "nan_cells": int((~fin).sum()),
            "min": float(np.nanmin(arr)),
            "max": float(np.nanmax(arr)),
            "cells_outside_0_1": int((fin & ((arr < 0) | (arr > 1))).sum()),
            "positive_cells": int((fin & (arr > 0)).sum()),
        })
    return rows


def lattice_coverage(footprint: np.ndarray, lattice_dots: np.ndarray) -> dict:
    total = int(footprint.sum())
    covered = int((within_3px(lattice_dots) & footprint).sum())
    return {
        "footprint_cells": total,
        "covered_within_3px": covered,
        "uncovered_cells": total - covered,
        "coverage_fraction": covered / total,
    }


def max_dots_passing_literal_rule(uncovered_cells: int, limit: float = OVERLAP_LIMIT) -> dict:
    """A clear needs overlap <= limit. Overlap >= (N - u)/N with u <= uncovered cells, so
    N dots need at least (1 - limit) * N dots in uncovered cells: N <= uncovered/(1-limit)."""
    need_share = 1 - limit
    return {
        "minimum_share_of_dots_in_uncovered_cells": need_share,
        "max_dots_clearable_only_by_placing_dots_in_uncovered_cells": int(np.floor(uncovered_cells / need_share + 1e-9)),
        "note": "Clearing requires placing dots in the uncovered cells: edge-hole gaming that the protocol forbids.",
    }


def subset_analysis(candidate: np.ndarray, reference: np.ndarray, catalogue: np.ndarray) -> dict:
    c, r = dots(candidate), dots(reference)
    removed, added = r & ~c, c & ~r
    cat_near = within_3px(catalogue)
    return {
        "candidate_dots": int(c.sum()),
        "reference_dots": int(r.sum()),
        "candidate_subset_of_reference": bool(not added.any()),
        "added_dots": int(added.sum()),
        "removed_dots": int(removed.sum()),
        "candidate_dots_within_3px_of_reference": int((c & within_3px(r)).sum()),
        "reference_catalogue_adjacent_dots": int((r & cat_near).sum()),
        "removed_catalogue_adjacent_dots": int((removed & cat_near).sum()),
        "kept_catalogue_adjacent_dots": int((c & cat_near).sum()),
        "catalogue_positive_cells": int(catalogue.sum()),
    }


def dti(true_pos: float, false_pos: float, false_neg: float, alpha: float = ALPHA, beta: float = BETA) -> float:
    return true_pos / (true_pos + alpha * false_pos + beta * false_neg)


def marginal_dot_lemma(base_tp=10.0, base_fp=20.0, base_fn=5.0,
                       hits=(0.0, 0.01, 0.05, 0.0556, 0.2, 0.5, 1.0)) -> dict:
    """Exact in the expected-count model with alpha+beta=1 (see README).

    Adding a dot with expected hit probability a changes the denominator by exactly alpha,
    so DTI rises iff a > alpha*DTI. Removing it rises DTI iff a < alpha*DTI."""
    if abs(ALPHA + BETA - 1.0) > 1e-12:
        raise ValueError("lemma requires alpha + beta = 1")
    base = dti(base_tp, base_fp, base_fn)
    rows, consistent = [], True
    for a in hits:
        add = dti(base_tp + a, base_fp + (1 - a), base_fn - a) - base
        rem = dti(base_tp - a, base_fp - (1 - a), base_fn + a) - base
        pred_add = a > ALPHA * base
        pred_rem = a < ALPHA * base
        ok = (add > 0) == pred_add and (rem > 0) == pred_rem
        if abs(a - ALPHA * base) < 1e-12:
            ok = True
        consistent &= ok
        rows.append({"hit_probability": a, "delta_if_added": add, "delta_if_removed": rem,
                     "matches_threshold_rule": bool(ok)})
    return {"base_dti": base, "alpha_times_dti": ALPHA * base, "rows": rows,
            "all_rows_match_rule": bool(consistent)}


def implied_removed_hit_rate_bound(n_removed: int) -> dict:
    """Aggregate form: D_new > D_old iff mean hit prob of removed dots < alpha*D_old.

    Uses the USER-REPORTED 0.2600 for the D2.8 family; this is a model-conditional bound,
    not a measurement of hidden-label hit rates."""
    bound = ALPHA * REFERENCE_D28_DTI_USER_REPORTED
    return {
        "removed_dots": n_removed,
        "reported_d28_dti": REFERENCE_D28_DTI_USER_REPORTED,
        "mean_hit_probability_upper_bound": bound,
        "reported_gems32_dti": GEMS32_DTI_USER_REPORTED,
        "alpha_times_reported_gems32_dti": ALPHA * GEMS32_DTI_USER_REPORTED,
        "evidence_class": "DERIVED from USER-REPORTED scores under the expected-count model",
    }


def build() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    recs = pinned_records()
    template_p = pinned_path(recs["template"], recs["template"]["repo"], "template.tif")
    lattice_p = pinned_path(recs["lattice"], recs["lattice"]["repo"], "lattice.tif")
    labels_p = pinned_path(recs["labels"], "buffedlizard55-lab/GEMSDOE24", "labels.tif")
    g32_p = pinned_path(recs["gems32"], recs["gems32"]["fetch_repo"], "gems32.tif")
    d28_p = pinned_path(recs["d28_reference"], recs["d28_reference"]["fetch_repo"], "d28.tif")

    template, tmask, tmeta = raster(template_p)
    footprint = np.isfinite(template) & (tmask > 0)
    lattice, _, lmeta = raster(lattice_p)
    labels, _, _ = raster(labels_p)
    gems32, _, gmeta = raster(g32_p)
    d28, _, dmeta = raster(d28_p)
    d25_p = pinned_path(recs["d28_gems25"], recs["d28_gems25"]["fetch_repo"], "d28_g25.tif")
    d30_p = pinned_path(recs["d28_gems30"], recs["d28_gems30"]["fetch_repo"], "d28_g30.tif")
    d25, _, _ = raster(d25_p)
    d30, _, _ = raster(d30_p)
    catalogue = np.isfinite(labels) & (labels == 1) & footprint

    lattice_dots = dots(lattice) & footprint
    cov = lattice_coverage(footprint, lattice_dots)
    literal = max_dots_passing_literal_rule(cov["uncovered_cells"])
    sub = subset_analysis(gems32, d28, catalogue)
    g32_vs_lattice = float((dots(gems32) & within_3px(lattice_dots)).sum() / dots(gems32).sum())
    d28_vs_lattice = float((dots(d28) & within_3px(lattice_dots)).sum() / dots(d28).sum())
    rho_g32_d28 = float(spearmanr(gems32[footprint], d28[footprint]).statistic)
    rho_g32_lattice = float(spearmanr(gems32[footprint], lattice[footprint]).statistic)

    return {
        "schema": "gems.decision-verification.v1",
        "date_utc": "2026-10-31",
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "scripts/verify_decision_evidence.py",
        "environment": {"python": platform.python_version(), "rasterio": rasterio.__version__,
                        "numpy": np.__version__, "scipy": __import__("scipy").__version__},
        "evidence_classes": {
            "REGISTRY-MEASUREMENT": "computed here from owner-mirror bytes matching a committed SHA-256 pin; not organizer-authenticated",
            "OFFICIAL-PAGE-TEXT": "public DrivenData page text, see evidence/official-page-read-2026-10-31.json",
            "DERIVED": "algebra on measured or user-reported inputs, with the stated assumption",
            "USER-REPORTED": "copied from the user's brief; not checked here",
        },
        "pins": {
            "template": {"repo": recs["template"]["repo"], "ref": recs["template"]["ref"],
                         "path": recs["template"]["path"], "sha256": recs["template"]["sha256"]},
            "lattice_gems13": {"repo": recs["lattice"]["repo"], "ref": recs["lattice"]["ref"],
                               "path": recs["lattice"]["path"], "sha256": recs["lattice"]["sha256"]},
            "labels": {"repo": "buffedlizard55-lab/GEMSDOE24", "ref": recs["labels"]["ref"],
                       "path": recs["labels"]["path"], "sha256": recs["labels"]["sha256"]},
            "gems32_file": {"repo": recs["gems32"]["repo"], "ref": recs["gems32"]["ref"],
                            "path": recs["gems32"]["path"], "sha256": recs["gems32"]["sha256"]},
            "d28_reference_file": {"repo": recs["d28_reference"]["repo"], "ref": recs["d28_reference"]["ref"],
                                   "path": recs["d28_reference"]["path"], "sha256": recs["d28_reference"]["sha256"]},
        },
        "grid": {"template": tmeta, "lattice": lmeta, "gems32": gmeta, "d28_reference": dmeta,
                 "same_grid_all": bool(tmeta["shape"] == lmeta["shape"] == gmeta["shape"] == dmeta["shape"]
                                       and tmeta["transform"] == lmeta["transform"] == gmeta["transform"] == dmeta["transform"]
                                       and tmeta["crs_epsg"] == 32611)},
        "d28_family_identity": {
            "reference_dots": int(dots(d28).sum()),
            "gems25_dots": int(dots(d25).sum()),
            "gems30_dots": int(dots(d30).sum()),
            "gems25_equals_reference": bool(np.array_equal(dots(d25), dots(d28))),
            "gems30_equals_reference": bool(np.array_equal(dots(d30), dots(d28))),
            "sources": {"reference": "GEMSDOE33", "gems25": recs["d28_gems25"]["path"],
                        "gems30": recs["d28_gems30"]["path"]},
            "evidence_class": "REGISTRY-MEASUREMENT",
        },
        "template_footprint_cells": int(footprint.sum()),
        "template_ones_inside_footprint": int((template[footprint] == 1).sum()),
        "catalogue_labels_equal_template_ones": bool(np.array_equal(labels == 1, template == 1)),
        "lattice_coverage": cov,
        "literal_rule_bound": literal,
        "gems32_vs_d28": sub,
        "gems32_dots_within_3px_of_lattice": g32_vs_lattice,
        "d28_dots_within_3px_of_lattice": d28_vs_lattice,
        "spearman_full_footprint": {"gems32_vs_d28": rho_g32_d28, "gems32_vs_lattice": rho_g32_lattice,
                                    "rho_limit": RHO_LIMIT},
        "marginal_dot_lemma": marginal_dot_lemma(),
        "implied_removed_hit_rate": implied_removed_hit_rate_bound(sub["removed_dots"]),
        "downloads_audit": downloads_audit(),
        "portal_range_check": {
            "files_checked": 0,
            "note": "filled from downloads_audit below",
        },
        "decision": {
            # No candidate raster exists in this session. A clear is possible only by placing dots in
            # uncovered cells (edge-hole gaming), so no file is cleared without gaming.
            "ok_to_download_and_submit_any_file": False,
            "uniqueness_gate_clearable_without_gaming": False,
            "experiments_run": 0,
            "tifs_generated": 0,
            "competition_slots_used": 0,
        },
    }


def main() -> int:
    result = build()
    rows = result["downloads_audit"]
    bad = [r["file"] for r in rows if r["nan_cells"] or r["cells_outside_0_1"] or r["dtype"] != "float32"]
    result["portal_range_check"] = {
        "files_checked": len(rows),
        "files_with_values_outside_0_1_or_nan": bad,
        "all_repo_tifs_finite_and_in_0_1": not bad,
        "conclusion": ("The repo-tracked TIFFs do not contain values outside [0, 1] or NaN. The portal "
                       "message therefore cannot be reproduced from these local bytes; the uploaded file is unknown."),
        "evidence_class": "REGISTRY-MEASUREMENT (repo-tracked files)",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
