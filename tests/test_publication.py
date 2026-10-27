from html.parser import HTMLParser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_run_card_is_negative_and_complete():
    card = json.loads((ROOT/'docs/data/run-card.json').read_text())
    assert card['verdict'] == 'negative'
    assert card['raster_sha256'] is None
    assert card['holdout']['dti'] is None
    assert card['holdout']['confidence_interval_95'] is None
    assert card['validator']['organizer_acceptance'] == 'unknown'
    assert len(card['note']) <= 140
    assert not card['weekly_slot_selected']


def test_published_audit_is_scoped_and_not_authorized():
    report = json.loads((ROOT/'docs/data/focus_audit.json').read_text())
    assert len(report['sites']) == 9
    assert len(report['comparisons']) == 72
    assert all(not s['submit'] and s['score_estimate'] is None for s in report['sites'])
    assert all('UNVERIFIED' in s['score_evidence'] for s in report['sites'])
    assert report['geometry']['uncovered'] == 6649


class LocalLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        for key in ('href', 'src'):
            if key in d:
                self.links.append(d[key])


def test_static_pages_local_targets_exist():
    for page in (ROOT/'docs').glob('*.html'):
        p = LocalLinks()
        p.feed(page.read_text())
        for href in p.links:
            if href.startswith(('#', 'https:', 'http:', 'mailto:')):
                continue
            path = href.split('#', 1)[0].split('?', 1)[0]
            assert (page.parent/path).is_file(), (page, href)


def test_current_negative_card_fails_prior_readiness_gate():
    # Preserve the earlier evidence-schema gate; current no-candidate data must
    # never be interpreted as promotion or slot authorization by that gate.
    from scripts.readiness import assess
    card = json.loads((ROOT/'docs/data/run-card.json').read_text())
    outcome = assess(card)
    assert outcome['verdict'] == 'negative'
    assert outcome['slot_authorized'] is False


def test_parallel_surface_recheck_is_a_negative_not_an_approval():
    report = json.loads((ROOT/'docs/data/parallel-surface-audit.json').read_text())
    card = json.loads((ROOT/'evidence/run_card.json').read_text())
    assert report['sha256'] == card['raster_sha256']
    assert report['support_overlap_fraction'] == 1.0
    assert report['single_band_float32'] and report['finite_whole_array']
    assert not report['organizer_template_authenticated']
    assert not report['submission_authorized']
    assert not report['holdout_reproduced_in_this_audit']


def test_parallel_surface_recheck_against_pinned_mirrors_when_available():
    import pytest
    cache = ROOT/'.cache/inputs'
    if not (cache/'r13_lattice_nan.tif').exists():
        pytest.skip('pinned mirrors not restored in lightweight CI')
    from scripts.audit_parallel_surface import audit
    report = audit(cache)
    assert report['support_overlap_fraction'] == 1.0
    assert report['positive_on_mirrored_catalogue'] == 0
    assert report['positive_outside_mirrored_footprint'] == 0
    assert report['min'] >= 0 and report['max'] <= 1
