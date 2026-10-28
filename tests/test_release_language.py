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
