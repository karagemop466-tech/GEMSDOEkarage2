"""The pre-placement stop must not be downgraded to conditional authorization."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_review_is_negative_and_evidence_based():
    card = json.loads((ROOT / 'docs/evidence/k2-protocol-review.json').read_text())
    assert card['verdict'] == 'negative' and card['submission_approved'] is False
    assert card['registry']['surface_stop_exceeded']
    assert card['registry']['final_max_overlap'] > 0.7
    assert not card['registry']['complete_accessible_scan']
    assert not card['validator_output']['prior_strict_format_pass']
    assert card['validator_output']['current_whole_array_finite_in_range']
    assert card['leaderboard_estimate'] is None


def test_stopped_final_cannot_generate():
    result = subprocess.run([sys.executable, 'scripts/k2.py', 'final'], cwd=ROOT,
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert 'prior surface registry stop; no TIFF generated' in result.stderr


def test_public_pages_make_negative_clear():
    for page in ('index.html', 'executive-summary.html'):
        text = (ROOT / 'docs' / page).read_text()
        assert 'K2 research raster' in text and 'NEGATIVE' in text and 'DO NOT SUBMIT' in text
