"""Regression guards for the 2026-10-31 HX analysis.

These pin the three quantitative claims the public pages depend on, so a later
edit cannot silently drift them: the forward metric reproduces the champion's
reported score, the apron/score rank relation stays negative and near-perfect,
and the published candidate's estimate stays below the incumbent (which is why
it is not promoted).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import score_estimator as se

ROOT = Path(__file__).resolve().parents[1]


def test_forward_model_reproduces_champion_score():
    # Components from evidence/calibration/leaderboard_calibration.json (B2 operating point).
    dti = se.forward_dti(37654, 5073.287555555577, 1038.48891571688)
    assert dti == pytest.approx(0.2778, abs=5e-5)


def test_required_hit_rate_is_monotone_and_bracketed():
    low = se.required_hit_rate(0.2778, 38000)
    high = se.required_hit_rate(0.4544, 38000)
    assert low is not None and high is not None
    assert 0.02 < low < high < 0.08
    T, M = se.model_state(38000, low)
    assert se.forward_dti(38000, T, M) == pytest.approx(0.2778, abs=2e-4)


def test_registry_prior_bounds():
    prior = se.registry_prior()
    assert prior["n"] == 7
    assert 0.18 < prior["mean"] < 0.26
    assert prior["max"] <= 0.2478


def test_nine_site_apron_relationship_is_negative_and_strong():
    data = json.loads((ROOT / "evidence/hx2/nine_site_measurements.json").read_text())
    assert data["apron_score_relationship"]["n"] == 9
    assert data["apron_score_relationship"]["spearman_rho"] < -0.95
    top = data["sites"][0]
    assert top["site"] == "GEMSDOE32" and top["reported_score_unverified"] == 0.2778


def test_published_candidate_card_is_consistent_and_not_promoted():
    card = json.loads((ROOT / "docs/downloads"
                       "/gemsdoe-karage2-hx2-lineament-apron3-36k-20261031-zeros.run-card.json").read_text())
    assert card["verdict"] == "negative"
    assert card["ok_to_download"] is True and card["ok_to_submit"] is False
    assert card["slot_authorized"] is False and card["approved_for_weekly_slot"] is False
    assert len(card["note"]) <= 140
    est = card["estimate"]
    assert est["central"] < 0.2778, "the central estimate must stay below the incumbent"
    assert est["not_supported_above"] <= 0.30, "no claim above the prior ceiling is supported"
    assert est["range_80pct"][0] <= est["central"] <= est["range_80pct"][1]
    uniq = card["uniqueness"]
    assert uniq["literal_worst_row"]["witness_is_degenerate"] is True
    assert uniq["verdict"] == "UNIQUE_PASS"
    assert uniq["discriminating_worst_row"]["our_dots_within_3px"] < 0.70
    assert card["format"]["positive_pixels"] == card["dots"] == 36000
    assert card["format"]["min"] == 0.0 and card["format"]["max"] == 1.0
