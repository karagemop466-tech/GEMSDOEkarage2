"""Tests for scripts/uniqueness_gate_calibration.py (2026-10-29).

The calibration reuses the shared comparator in scripts/check_uniqueness.py; these
tests do not fork it. They run on small synthetic grids so they do not need the
git-ignored competition cache. The committed receipt is checked for internal
consistency and for the fail-closed decision it records.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

import uniqueness_gate_calibration as cal  # noqa: E402
from check_uniqueness import centered_ranks, check_comparator  # noqa: E402

RECEIPT = ROOT / "evidence/uniqueness-gate-calibration-2026-10-29.json"


def test_pigeonhole_bound_arithmetic_is_exact():
    # Pass iff 10*matched <= 7*n with matched = n - u, i.e. 3n <= 10u.
    for u in (0, 1, 2, 3, 10, 6649):
        bound = cal.max_passing_positive_cells(u)
        assert bound == (10 * u) // 3
        assert 3 * bound <= 10 * u        # the bound passes with all u unmatched cells used
        assert 3 * (bound + 1) > 10 * u   # one more positive cell can never pass
    assert cal.max_passing_positive_cells(6649) == 22163
    with pytest.raises(ValueError):
        cal.max_passing_positive_cells(-1)


def _synthetic(size=80, spacing=5):
    foot = np.ones((size, size), dtype=bool)
    lattice = np.zeros((size, size), dtype=np.float32)
    lattice[2::spacing, 2::spacing] = 1.0
    return foot, lattice


def test_spacing5_witness_flags_random_dot_sets_as_duplicates():
    foot, lattice = _synthetic()
    rng = np.random.default_rng(7)
    idx = np.flatnonzero(foot.ravel())
    for n in (20, 200):
        sel = rng.choice(idx, size=n, replace=False)
        support = np.zeros(foot.size, bool)
        support[sel] = True
        support = support.reshape(foot.shape)
        ranks, norm = centered_ranks(support.astype(np.float32)[foot])
        res = check_comparator(ranks, norm, support & foot, lattice, foot)
        # Random placement is not a copy, yet the literal gate still flags it.
        assert res["duplicate"] is True
        assert res["overlap_fraction"] > 0.70


def test_witness_that_leaves_cells_uncovered_leaves_room_only_for_small_sets():
    foot, lattice = _synthetic(size=60, spacing=9)  # sparse witness: many uncovered cells
    pos = (lattice > 0) & foot
    near = distance_transform_edt(~pos) <= 3.0
    uncovered = int((foot & ~near).sum())
    assert uncovered > 0
    # A candidate placed only in uncovered cells passes (zero overlap) at small n.
    cells = np.flatnonzero((foot & ~near).ravel())[:5]
    support = np.zeros(foot.size, bool)
    support[cells] = True
    support = support.reshape(foot.shape)
    values = support.astype(np.float32)
    ranks, norm = centered_ranks(values[foot])
    res = check_comparator(ranks, norm, support & foot, lattice, foot)
    assert res["matches_within_3px"] == 0
    assert res["duplicate"] is False


def test_committed_receipt_is_internally_consistent_and_fail_closed():
    doc = json.loads(RECEIPT.read_text(), parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
    assert doc["schema"] == cal.SCHEMA
    assert doc["upload_authorized"] is False and doc["submission_generated"] is False
    wl = doc["witness_lattice"]
    assert wl["uncovered_footprint_cells"] == wl["vendored_certificate_uncovered"]
    assert doc["pigeonhole_bound"]["max_passing_positive_cells"] == cal.max_passing_positive_cells(
        wl["uncovered_footprint_cells"])
    assert len(doc["focus_files_vs_lattice"]) == 9
    assert {r["site"] for r in doc["focus_files_vs_lattice"]} == {
        "GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
        "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"}
    assert all(r["duplicate_by_literal_gate"] is True for r in doc["focus_files_vs_lattice"])
    # Every positive count above the bound must be a duplicate in the receipt's own null rows.
    for row in doc["null_controls"]:
        if row["n_positive_cells"] > doc["pigeonhole_bound"]["max_passing_positive_cells"]:
            assert row["duplicate_by_literal_gate"] is True
    assert doc["null_controls_min_overlap"] == min(r["overlap_fraction"] for r in doc["null_controls"])
    assert doc["witness_lattice"]["vendored_certificate_universal_blocker"] is False
