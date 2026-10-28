"""Current decision must reflect the recorded mandatory pre-placement stop."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_surface_stop_and_audit_are_negative():
    historical = json.loads((ROOT / 'evidence/k2/run_card.json').read_text())
    audit = json.loads((ROOT / 'evidence/k2/final_registry_audit.json').read_text())
    current = json.loads((ROOT / 'evidence/k2-protocol-review.json').read_text())
    assert 'overlap 1.0' in historical['correlation_overlap_vs_registry']['surface_before_placement']['vs_r13_lattice']
    assert audit['worst_dot_overlap'] > audit['overlap_limit']
    assert not audit['complete_accessible_scan'] and not audit['unique']
    assert current['verdict'] == 'negative' and current['slot_authorized'] is False
    assert current['raster_sha256'] == historical['raster_sha256']
    assert current == json.loads((ROOT / 'docs/evidence/k2-protocol-review.json').read_text())


def test_public_candidate_guidance_does_not_claim_portal_acceptance():
    for page in ('index.html', 'executive-summary.html', 'how-to-submit.html'):
        text = (ROOT / 'docs' / page).read_text()
        assert 'DO NOT SUBMIT' in text
        assert 'k2-protocol-review.json' in text
        assert 'cannot trigger' not in text
