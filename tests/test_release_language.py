"""Public guidance must not convert a failed research artifact into a submission."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_historical_card_lattice_failure_is_visible():
    card = json.loads((ROOT / 'docs/downloads/gemsdoe-karage2-hkarage1-irregular-submodular-15000d-6a3f542a-zeros-run-card.json').read_text())
    assert card['uniqueness']['vs_lattice_3px_overlap'] > 0.70
    for page in ('index.html', 'how-to-submit.html'):
        text = (ROOT / 'docs' / page).read_text()
        assert '100%' in text and '70%' in text
        assert 'NO' in text
    assert '(submission raster)' not in (ROOT / 'docs/index.html').read_text()
    assert 'Download the validated TIF' not in (ROOT / 'docs/how-to-submit.html').read_text()


def test_h1_remains_negative():
    card = json.loads((ROOT / 'docs/evidence/run_card.json').read_text())
    assert card['verdict'] == 'negative'
    assert not card['approved_for_weekly_slot']
    assert card['registry']['final_dot_check'].startswith('not run')


def test_current_k2_release_card_is_negative_under_literal_registry_gate():
    card = json.loads((ROOT / 'docs/evidence/release-review-run-card-2026-10-28.json').read_text())
    assert card['verdict'] == 'negative'
    assert card['submission_approved'] is False
    assert card['holdout']['evidence_class'] == 'HOLDOUT-DTI'
    assert card['holdout']['evaluator_version']
    assert card['holdout']['withheld_positive_pixels'] > 0
    assert len(card['holdout']['ci95']) == 2
    assert card['correlation_overlap_vs_registry']['literal_all_registry_result'].startswith('FAIL')
    assert card['correlation_overlap_vs_registry']['calibration_spacing5_lattice_overlap_within_3px'] > 0.70
    assert card['correlation_overlap_vs_registry']['calibration_ctx_ridge_overlap_within_3px'] > 0.70
    assert len(card['note']) <= 140
    assert card['leaderboard_estimate'].startswith('Unavailable')
    for page in ('index.html', 'executive-summary.html', 'how-to-submit.html'):
        text = (ROOT / 'docs' / page).read_text()
        assert 'DO NOT SUBMIT' in text
        assert 'literal' in text.lower() or 'uniqueness' in text.lower()
