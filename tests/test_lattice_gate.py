"""Regression tests for the 2026-10-29 literal lattice-gate audit.

These tests need no restored competition or registry bytes. They check:
  * the pigeonhole bound used in the decision memo (formula and worked values);
  * that the audit's overlap helper equals the shared writer's ``_dot_overlap_3px``;
  * that the committed receipt is internally consistent and fails closed.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lattice_gate_audit import (  # noqa: E402
    LIMIT,
    LATTICE_SHA256,
    max_dots_allowed,
    min_overlap_bound,
    overlap_from_distance,
)
from submission_writer import _dot_overlap_3px  # noqa: E402
from scipy import ndimage  # noqa: E402

RECEIPT = ROOT / "evidence/lattice-gate-audit-2026-10-29.json"
UNCOVERED = 6649  # footprint cells more than 3 px from every lattice dot (measured)


def test_pigeonhole_bound_matches_measured_worked_values():
    # 45,108 dots (HK3 saved file) against 6,649 uncovered cells: >= 85.26 % overlap.
    assert min_overlap_bound(45108, UNCOVERED) == pytest.approx(0.852598, abs=1e-6)
    # 37,654 dots (GEMSDOE32 owner file): >= 82.34 % overlap, above the 70 % stop.
    assert min_overlap_bound(37654, UNCOVERED) == pytest.approx(0.823418, abs=1e-6)


def test_max_dots_that_could_pass_is_uncovered_over_thirty_percent():
    assert max_dots_allowed(UNCOVERED) == 22163
    assert math.floor(UNCOVERED / (1 - LIMIT) + 1e-9) == 22163
    assert min_overlap_bound(0, UNCOVERED) == 0.0
    # Overlap can never be below zero, even for tiny sets fully in holes.
    assert min_overlap_bound(10, 100) == 0.0


def test_overlap_helper_equals_shared_writer_function():
    rng = np.random.default_rng(20261029)
    for _ in range(5):
        a = rng.random((60, 70)) < 0.05
        b = rng.random((60, 70)) < 0.05
        dist_b = ndimage.distance_transform_edt(~b, sampling=100.0)
        assert overlap_from_distance(dist_b, a) == pytest.approx(_dot_overlap_3px(a, b), abs=1e-12)


def test_overlap_helper_empty_candidate_is_zero():
    dist = np.zeros((4, 4))
    assert overlap_from_distance(dist, np.zeros((4, 4), dtype=bool)) == 0.0


@pytest.fixture(scope="module")
def receipt():
    if not RECEIPT.is_file():
        pytest.skip("committed lattice-gate receipt missing")
    return json.loads(RECEIPT.read_text())


def test_receipt_counts_and_pigeonhole_are_self_consistent(receipt):
    rows = receipt["per_raster"]
    assert receipt["registry_rasters"] == len(rows) == 440
    assert receipt["uncovered_footprint_cells"] == UNCOVERED
    assert receipt["max_dots_that_could_pass_literal_70pct_rule"] == max_dots_allowed(UNCOVERED)
    comparable = [r for r in rows if r["comparable_grid"]]
    assert receipt["registry_rasters_not_comparable_grid"] == len(rows) - len(comparable) == 1
    failing = [r for r in comparable if r["literal_stop_vs_lattice"]]
    assert receipt["registry_rasters_failing_literal_stop_vs_lattice"] == len(failing)


def test_receipt_flags_every_nine_site_file_as_stopped(receipt):
    nine = receipt["nine_site_best_files"]
    assert len(nine) == 9
    assert len({r["site"] for r in nine}) == 9
    for row in nine:
        assert row["literal_stop_vs_lattice"] is True
        assert row["measured_overlap_vs_lattice"] > LIMIT
        assert row["measured_overlap_vs_lattice"] >= row["min_possible_overlap_vs_lattice"] - 1e-9
    assert receipt["pass_fail_summary"]["any_nine_site_best_file_passes_literal_lattice_gate"] is False


def test_receipt_lattice_is_registered_and_self_overlap_is_one(receipt):
    lattice = [r for r in receipt["per_raster"] if r["sha256"] == LATTICE_SHA256]
    assert len(lattice) == 1
    assert lattice[0]["overlap_vs_lattice"] == pytest.approx(1.0)
    assert receipt["lattice_witness"]["dots_in_footprint"] == 206895


def test_receipt_records_lattice_avoiding_outlier_as_irregularity(receipt):
    # The only non-lattice registry raster under the 70 % line has 505 dots and 0 % overlap.
    # It passes by avoiding the lattice (edge-hole gaming), so the receipt must not count it as clearance.
    passing = [r for r in receipt["per_raster"] if r["comparable_grid"] and not r["literal_stop_vs_lattice"]
               and r["sha256"] != LATTICE_SHA256]
    assert [r["dots_in_footprint"] for r in passing] == [505]
    assert passing[0]["overlap_vs_lattice"] == 0.0
    assert "lattice-avoiding" in passing[0]["path"]
