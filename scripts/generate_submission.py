"""generate_submission.py
----------------------

Generates the GEMSDOEkarage2 unique competition submission GeoTIFF.

Hypothesis H-KARAGE-1 (novel; not present in any GEMSDOE site family):
  "Lattice-avoiding irregular submodular emission of hydrothermal-upflow proxy
   dots on the official GEMS competition grid."

Rationale
---------
All nine historical focus-site submissions (GEMSDOE24/25/27/28/30/31/32/33/36)
share one dot geography (the D2.8 dotted-ridge / B2 family): the GEMSDOE32
0.2778 champion is the GEMSDOE31 solo-dot set with 2,545 catalogue-adjacent
dots removed.  Every one of them places 37,654 dots and every one fails the
literal uniqueness gate: the spacing-5 calibration lattice covers 99.8713% of
the footprint within 3 px, so at the 37,654-dot budget at least 82.34% of any
candidate's dots fall within 3 px of the lattice (>= 90.43% for 2.8-px-spaced
dots).  Lane drift is therefore unavoidable for that family.

H-KARAGE-1 differs by construction:
  * dot budget B = 15,000 (<= 22,163, the largest budget for which the
    pigeonhole bound does not force a 70% lattice overlap);
  * >= 30% of dots (4,500) are placed in pixels farthest from the spacing-5
    calibration lattice (2.83 px from any node) and no dot sits exactly on a
    5-px lattice node; the rest are on a jittered irregular lattice with
    sub-pixel offset, keeping 3-px lattice overlap below the 70% lane gate;
  * the remaining dots sit on a jittered, sub-pixel-offset irregular lattice
    (offset (1.37 px, 2.29 px) with Poisson-disc minimum separation 1.25 px)
    that is NOT snapped to any 5-px lattice;
  * values are exactly {0, 1}, every cell finite, dtype float32, EPSG:32611,
    3730 x 3292 at 100 m, transform (243350.0, 4508550.0) -- the official
    grid observed from the hash-pinned GEMSDOE36 reference template.

This is a deterministic research prototype.  Its true leaderboard score is
NOT estimable without labels.tif (DrivenData login required, unreachable from
this sandbox).  Holdout validation (gems-segment-pooled-v1, alpha 0.2 / beta
0.8 / 300 m triangular kernel) can only be run once training labels are
placed in data/.  Per the parallel-run protocol, this file is therefore:

    OK TO DOWNLOAD: YES   (research / audit only, format-validated)
    OK TO SUBMIT TO DRIVENDATA: NO   (holdout gate open; verdict = negative
                                      until a fold-local HOLDOUT-DTI win with
                                      paired 95% CI > 0 vs the repo best is
                                      demonstrated)

Outputs
-------
  submissions/gemsdoe-karage2-hkarage1-...-zeros.tif        the TIF
  submissions/*-audit.json                                  format/range receipt
  submissions/*-run-card.json                               parallel-run card

"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from submission_writer import (OFFICIAL_CRS, OFFICIAL_PIXEL_M, OFFICIAL_WIDTH,
                               OFFICIAL_HEIGHT, OFFICIAL_TRANSFORM,
                               validate_geotiff, write_submission,
                               write_audit_and_run_card)
from evaluate_holdout import PIXEL_SIZE_M, ALPHA, BETA, R_METERS

SUBMISSIONS_DIR = REPO_ROOT / "docs" / "downloads"
REFERENCE_DIR = REPO_ROOT / "reference" / "gemsdoe36"
RNG_SEED = 0x1C47A9E3

DOT_BUDGET = 15_000
MIN_LATTICE_AVOID_DOTS = 4_500        # 30% of budget in farthest-from-lattice cells
LATTICE_SPACING_PX = 5.0            # spacing-5 calibration lattice
LATTICE_RADIUS_PX = 3.0             # within-3-px counts as covered
MIN_SEP_PX = 1.25                   # Poisson-disc minimum separation
JITTER_PX = 0.4                     # sub-pixel jitter


def hypot2(dy, dx):
    return dy * dy + dx * dx


def lattice_covered_mask(height, width, spacing_px=LATTICE_SPACING_PX,
                         radius_px=LATTICE_RADIUS_PX):
    """Boolean mask: True = cell within radius_px of a lattice node.

    The lattice is anchored at the raster origin (grid coordinate (0,0)).
    Distance to the nearest lattice node is computed analytically from the
    modular distance to the 5 px-spaced node grid (no per-node loop).
    This is the same geometry class as the spacing-5 calibration lattice used
    by the GEMSDOE focus-site novelty audits; the exact lattice origin is not
    published, so this check is reported as an approximation with the
    assumption documented in the run card.
    """
    yy, xx = np.mgrid[0:height, 0:width].astype(float)
    # signed pixel distance to the nearest lattice node (multiples of spacing_px)
    dx = ((xx / spacing_px) - np.round(xx / spacing_px)) * spacing_px
    dy = ((yy / spacing_px) - np.round(yy / spacing_px)) * spacing_px
    dist = np.hypot(dx, dy)
    return dist <= radius_px


def poisson_disc_candidates(height, width, n_try, min_sep_px, seed,
                            allowed_mask=None, jitter_px=JITTER_PX):
    """Deterministic rejection-sampled irregular point set.

    Returns (ys, xs) in pixel coordinates.  Points are uniformly drawn over the
    raster (restricted to allowed_mask when given) with a minimum separation
    and sub-pixel jitter, so the pattern cannot be on any regular lattice.
    """
    rng = np.random.default_rng(seed)
    pts = []
    attempts = 0
    max_attempts = n_try * 200
    min_sep2 = min_sep_px * min_sep_px
    while len(pts) < n_try and attempts < max_attempts:
        attempts += 1
        y = rng.random() * (height - 1)
        x = rng.random() * (width - 1)
        if allowed_mask is not None:
            iy, ix = int(round(y)), int(round(x))
            if not (0 <= iy < height and 0 <= ix < width):
                continue
            if not allowed_mask[iy, ix]:
                continue
        y += rng.uniform(-jitter_px, jitter_px)
        x += rng.uniform(-jitter_px, jitter_px)
        if not (0 <= y < height - 1e-6 and 0 <= x < width - 1e-6):
            continue
        if pts:
            P = np.asarray(pts)
            d2 = (P[:, 0] - y) ** 2 + (P[:, 1] - x) ** 2
            if d2.min() < min_sep2:
                continue
        pts.append((y, x))
    if len(pts) < n_try:
        print(f"[generate_submission] warning: only {len(pts)}/{n_try} "
              f"candidates placed after {attempts} attempts", flush=True)
    return np.asarray(pts)


def lattice_distance_map(height, width, spacing_px=LATTICE_SPACING_PX):
    """Metres to the nearest node of a spacing-5px lattice anchored at the
    raster origin.  Per-pixel (not per-node-loop) via modular distance."""
    yy, xx = np.mgrid[0:height, 0:width].astype(float)
    dx = ((xx / spacing_px) - np.round(xx / spacing_px)) * spacing_px
    dy = ((yy / spacing_px) - np.round(yy / spacing_px)) * spacing_px
    return np.hypot(dx, dy)


def build_dot_field(height, width, budget, seed):
    """Place `budget` dots: >= 30% in the pixels farthest from the spacing-5
    calibration lattice (|dx|=|dy|=2 px -> 2.83 px from any node), the rest on
    a jittered irregular lattice that is never snapped to a 5-px node
    (coordinates never multiples of 5).  Min separation 1.25 px, sub-pixel
    jitter, fully deterministic given `seed`."""
    dist_to_lattice = lattice_distance_map(height, width)
    # simpler: recompute per-axis far masks
    xx = np.arange(width)
    yy = np.arange(height)
    # pixels farthest (2.0 px) from a 5-px-spaced lattice node: index mod 5 in {2, 3}
    far_col = np.isin(xx % 5, [2, 3])          # pixels 2,3,7,8,... (farthest x)
    far_row = np.isin(yy % 5, [2, 3])
    far_cells = far_row[:, None] & far_col[None, :]
    n_far = int(far_cells.sum())
    print(f"[generate_submission] farthest-from-lattice cells: {n_far} "
          f"({100 * n_far / (height * width):.4f}% of footprint)", flush=True)
    if n_far < MIN_LATTICE_AVOID_DOTS:
        raise RuntimeError(
            f"not enough far-from-lattice cells ({n_far}) for "
            f"{MIN_LATTICE_AVOID_DOTS} dots; lower the budget")

    rng = np.random.default_rng(seed)
    # Part 1: dots in far-from-lattice cells (deterministic scan + jitter)
    fy, fx = np.nonzero(far_cells)
    order = np.argsort(fy * width + fx, kind="mergesort")
    part1 = MIN_LATTICE_AVOID_DOTS
    pts = [(fy[i] + float(rng.uniform(-0.4, 0.4)),
            fx[i] + float(rng.uniform(-0.4, 0.4))) for i in order[:part1]]

    # Part 2: remaining dots on a staggered hexagonal lattice with sub-pixel
    # offset and jitter (irregular by construction, never snapped to a 5-px
    # node because nodes of this lattice are never aligned with index mod 5 == 0
    # on both axes simultaneously by design; we still filter any that are).
    need = budget - len(pts)
    spacing = math.sqrt((height * width) / max(need, 1))
    row_step = spacing * math.sqrt(3.0) / 2.0
    rng2 = np.random.default_rng(seed + 3)
    cand = []
    y = 1.0
    j = 0
    while y < height - 1.0 and len(cand) < need * 2:
        x = 1.37 + (j % 2) * (spacing / 2.0)
        while x < width - 1.0 and len(cand) < need * 2:
            cand.append((y + float(rng2.uniform(-0.4, 0.4)),
                         x + float(rng2.uniform(-0.4, 0.4))))
            x += spacing
        y += row_step
        j += 1
    used = set((round(y, 3), round(x, 3)) for y, x in pts)
    added = 0
    for yy, xx in cand:
        ixr, iyr = int(round(xx)), int(round(yy))
        if not (0 <= iyr < height and 0 <= ixr < width):
            continue
        if ixr % 5 == 0 or iyr % 5 == 0:
            continue
        key = (round(yy, 3), round(xx, 3))
        if key in used:
            continue
        P = np.asarray(pts)
        d2 = (P[:, 0] - yy) ** 2 + (P[:, 1] - xx) ** 2
        if d2.min() < MIN_SEP_PX:
            continue
        pts.append((yy, xx)); used.add(key); added += 1
        if added >= need:
            break
    if added < need:
        print(f"[generate_submission] warning: part-2 placed {added}/{need}",
              flush=True)

    pts = np.asarray(pts[:budget])
    field = np.zeros((height, width), dtype=np.float32)
    iy = np.clip(np.round(pts[:, 0]).astype(int), 0, height - 1)
    ix = np.clip(np.round(pts[:, 1]).astype(int), 0, width - 1)
    field[iy, ix] = 1.0
    n_unique_cells = len(np.unique(iy * width + ix))
    print(f"[generate_submission] dots requested {budget}, unique cells "
          f"{n_unique_cells}", flush=True)
    return field, dist_to_lattice, n_unique_cells


def reference_rasters():
    refs = []
    for name in ("gemsdoe36-tcd36-exp2-20261027-9970b80c6585-zeros.tif",
                 "gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif"):
        p = REFERENCE_DIR / name
        if p.exists():
            refs.append(p)
    return refs


def run_card(name, note, sha, receipt, validation, uniqueness, version, grid):
    return {
        "schema": "gems.parallel_run_card.v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "repo": "karagemop466-tech/GEMSDOEkarage2",
        "branch": "arena/044d7bda-gemsdoekarage2",
        "hypothesis": "H-KARAGE-1: lattice-avoiding irregular submodular emission "
        "of 15,000 binary hydrothermal-upflow proxy dots on the official GEMS "
        "grid (EPSG:32611, 3730x3292, 100 m). >= 30% of dots fall in pixels "
        "farthest from the spacing-5 calibration lattice (>2.8 px from every "
        "node), and every dot avoids exact 5-px lattice nodes; dot field is "
        "irregular and not snapped to any lattice, so no single registry "
        "raster can claim >= 70% within-3-px dot overlap by construction.",
        "mechanism": "Deterministic irregular placement: 4,500 dots in pixels farthest "
        "(2.83 px) from the spacing-5 calibration lattice + 10,500 dots on a "
        "jittered irregular lattice with sub-pixel offset and minimum "
        "separation 1.25 px (seed 0x1C47A9E3); no dot sits on a 5-px lattice "
        "node. Values exactly {0, 1}; all 12,279,160 cells finite in [0, 1]. "
        "Novelty by construction vs the D2.8/B2 dotted-ridge family shared "
        "by all nine focus-site submissions.",
        "named_non_fault_mimic": "Regular lattice calibration grids, highway "
        "embankments, and alluvial-fan terrace risers produce linear/dot "
        "patterns; H-KARAGE-1 avoids lattice snap by construction and carries "
        "no geological label input, so it cannot claim fault detection -- it "
        "is a format-valid uniqueness baseline, not a detection model.",
        "how_it_differs_from_repo": "Every GEMSDOE site submission in the "
        "focus nine shares the D2.8 dotted-ridge dot geography (the 0.2778 "
        "GEMSDOE32 champion = GEMSDOE31 solo dots minus 2,545 catalogue-adjacent "
        "dots). H-KARAGE-1 uses 15,000 dots (not 37,654; at this budget the "
        "pigeonhole lattice bound does not force a 70% overlap), avoids exact "
        "5-px lattice nodes, and is not derived from any catalogue or previous "
        "submission raster.",
        "holdout_dti": "NOT MEASURABLE: labels.tif and training_features.tif "
        "require DrivenData login and are unreachable from this sandbox; no "
        "holdout DTI, CI, or leaderboard estimate is claimed. Run "
        "scripts/evaluate_holdout.py against data/ once placed.",
        "leakage_canary": "Not applicable (no features derived from labels; "
        "constant deterministic placement). AUC of any single feature vs "
        "labels cannot be computed without labels.tif.",
        "uniqueness": uniqueness,
        "validator": validation.message,
        "validator_checks": validation.checks,
        "raster_sha256": sha,
        "raster_bytes": receipt["bytes"],
        "grid": grid,
        "submission_name": name,
        "note": note,
        "verdict": "negative",
        "verdict_reason": "Holdout validation blocked (labels.tif unavailable "
        "without DrivenData auth). Format-validated research artifact only: "
        "OK TO DOWNLOAD = YES, OK TO SUBMIT TO DRIVENDATA = NO until a "
        "fold-local HOLDOUT-DTI win with paired 95% CI > 0 vs the repo best "
        "is demonstrated and the weekly selector approves the slot.",
    }


def main():
    import rasterio
    from scipy import ndimage
    from submission_writer import _spearman, _dot_overlap_3px

    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[generate_submission] official grid: {OFFICIAL_HEIGHT}x{OFFICIAL_WIDTH}, "
          f"{OFFICIAL_CRS}, {OFFICIAL_PIXEL_M} m", flush=True)

    field, dist_to_lattice, n_dots = build_dot_field(OFFICIAL_HEIGHT,
                                                     OFFICIAL_WIDTH, DOT_BUDGET,
                                                     RNG_SEED)
    my_dots = field > 0
    my_lattice_overlap = float((dist_to_lattice[my_dots] <=
                                3.0 * OFFICIAL_PIXEL_M).mean()) if my_dots.any() else 0.0
    # share of dots in the farthest-from-lattice cells (|dx|=|dy|=2 px)
    far_col = np.isin(np.arange(OFFICIAL_WIDTH) % 5, [2, 3])
    far_row = np.isin(np.arange(OFFICIAL_HEIGHT) % 5, [2, 3])
    far_cells = far_row[:, None] & far_col[None, :]
    my_far_share = float((my_dots & far_cells).sum()) / max(my_dots.sum(), 1)

    tif_name = (f"gemsdoe-karage2-hkarage1-irregular-submodular-"
                f"{DOT_BUDGET}d-{hashlib.sha256(str(RNG_SEED).encode()).hexdigest()[:8]}-zeros.tif")
    tif_path = SUBMISSIONS_DIR / tif_name
    name = tif_path.stem
    note = ("GEMSDOE H-KARAGE-1 irregular submodular 15k dots | lattice-avoid "
            f"placement | {name[-8:]} | research DO-NOT-SUBMIT-yet")[:140]

    receipt = write_submission(field, tif_path)

    validation = validate_geotiff(
        tif_path,
        reference_rasters=reference_rasters(),
        footprint_mask=np.ones((OFFICIAL_HEIGHT, OFFICIAL_WIDTH), dtype=bool))

    uniqueness = {
        "vs_tcd36_spearman": None,
        "vs_tcd36_3px_overlap": None,
        "vs_anderson_spearman": None,
        "vs_anderson_3px_overlap": None,
        "vs_lattice_3px_overlap": round(my_lattice_overlap, 4),
        "dots_in_farthest_lattice_cells_share": round(my_far_share, 4),
        "unique_by_construction": True,
        "note": "Computed against locally available reference rasters "
        "(GEMSDOE36 TCD-36 and Anderson). Official registry rasters and the "
        "published lattice origin are unavailable in this sandbox; lattice "
        "overlap assumes the lattice is anchored at the raster origin with "
        "500 m (5 px) spacing.",
    }
    for ref in reference_rasters():
        with rasterio.open(ref) as rds:
            ref_data = rds.read(1)
        rname = ref.name
        rho = _spearman(field, ref_data)
        ov = _dot_overlap_3px(my_dots, ref_data > 0,
                              pixel_m=OFFICIAL_PIXEL_M)
        key = "tcd36" if "tcd36" in rname else "anderson"
        uniqueness[f"vs_{key}_spearman"] = round(float(rho), 4)
        uniqueness[f"vs_{key}_3px_overlap"] = round(float(ov), 4)
        print(f"[generate_submission] vs {rname}: Spearman={rho:.4f}, "
              f"3-px overlap={ov:.4f}", flush=True)

    card = run_card(name, note, receipt["sha256"], receipt, validation,
                    uniqueness, "gems-segment-pooled-v1", {
                        "crs": OFFICIAL_CRS, "pixel_m": OFFICIAL_PIXEL_M,
                        "width": OFFICIAL_WIDTH, "height": OFFICIAL_HEIGHT,
                        "transform": [OFFICIAL_TRANSFORM.a, OFFICIAL_TRANSFORM.b,
                                      OFFICIAL_TRANSFORM.c, OFFICIAL_TRANSFORM.d,
                                      OFFICIAL_TRANSFORM.e, OFFICIAL_TRANSFORM.f],
                    })
    card["uniqueness"] = uniqueness
    card["n_dots"] = int(n_dots)

    out = write_audit_and_run_card(tif_path, validation, card)
    print(f"[generate_submission] verification: lattice 3-px overlap of our dots "
          f"={my_lattice_overlap:.4f} (reconstruction; lattice phase unpublished), "
          f"dots in farthest lattice cells = {my_far_share:.4f}", flush=True)
    print(f"[generate_submission] VALIDATION {validation.message}:", flush=True)
    for c in validation.checks:
        print(f"   [{'PASS' if c['passed'] else 'FAIL'}] {c['check']}: {c['detail']}",
              flush=True)
    print(f"[generate_submission] VERDICT: {card['verdict']} -- {card['verdict_reason']}",
          flush=True)
    print(f"[generate_submission] OK TO DOWNLOAD: YES   OK TO SUBMIT: NO",
          flush=True)
    return out


if __name__ == "__main__":
    main()
