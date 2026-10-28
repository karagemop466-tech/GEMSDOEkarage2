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


def test_h1_and_h2_remain_distinct_negative_receipts():
    h1 = json.loads((ROOT / 'docs/evidence/h1/run_card.json').read_text())
    h2 = json.loads((ROOT / 'docs/evidence/run_card_h2.json').read_text())
    assert h1['verdict'] == h2['verdict'] == 'negative'
    assert not h1['approved_for_weekly_slot'] and not h2['approved_for_weekly_slot']
    assert h1['registry']['final_dot_check'].startswith('not run')
    assert h2['registry']['final_dot_check'].startswith('not run')
    assert h1['raster_sha256'] != h2['raster_sha256']
    home = (ROOT / 'docs/index.html').read_text()
    assert 'evidence/h1/run_card.json' in home and 'evidence/run_card_h2.json' in home


def test_current_k2_release_card_is_negative_under_literal_registry_gate():
    card = json.loads((ROOT / 'docs/evidence/k2-review-2026-10-28.json').read_text())
    assert card['verdict'] == 'negative'
    assert card['ok_to_submit'] is False
    assert card['holdout']['classification'].startswith('HOLDOUT-DTI')
    assert card['holdout']['evaluator_version']
    assert card['holdout']['withheld_positives'] > 0
    assert len(card['holdout']['confidence_interval_95']) == 2
    assert card['correlation_overlap_vs_registry']['final_worst_overlap'] > 0.70
    assert card['correlation_overlap_vs_registry']['final_scan_complete'] is False
    assert len(card['note']) <= 140
    assert card['holdout']['leaderboard_estimate'] is None
    for page in ('index.html', 'executive-summary.html', 'how-to-submit.html'):
        text = (ROOT / 'docs' / page).read_text()
        assert 'DO NOT SUBMIT' in text
        assert 'literal' in text.lower() or 'uniqueness' in text.lower()
