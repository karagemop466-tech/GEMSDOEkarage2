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


def test_pages_workflow_keeps_legacy_and_actions_url_layouts_consistent():
    workflow = (ROOT/'.github/workflows/pages.yml').read_text()
    assert 'cp index.html "$RUNNER_TEMP/gems-pages/index.html"' in workflow
    assert 'cp -a docs/. "$RUNNER_TEMP/gems-pages/docs/"' in workflow
    assert 'path: ${{ runner.temp }}/gems-pages' in workflow
    assert 'path: docs\n' not in workflow
    assert 'docs/index.html' in (ROOT/'index.html').read_text()


def test_current_scorecard_uses_claim_named_byte_audited_files():
    # The earlier audit measured NaN siblings for these five claims. Ensure the
    # current UI, generated pages and pinned hashes instead point to the exact
    # files named by the published user-reported historical claims.
    expected = {
        'GEMSDOE24': 'gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-allfinite.tif',
        'GEMSDOE25': 'gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-zeros.tif',
        'GEMSDOE27': 'gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-allfinite.tif',
        'GEMSDOE28': 'gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-allfinite.tif',
        'GEMSDOE31': 'gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif',
        'GEMSDOE32': 'gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif',
    }
    report = json.loads((ROOT/'docs/data/focus_audit.json').read_text())
    manifest = json.loads((ROOT/'registry/pinned_assets.json').read_text())
    assets = {s['site']: s for s in manifest['assets'] if s['role'] == 'focus'}
    for row in report['sites']:
        asset = assets[row['site']]
        assert row['filename'] == Path(asset['path']).name
        assert row['sha256'] == asset['sha256']
        assert row['github_ref'] == asset['ref']
        assert row['score_claim_source'] == 'https://buffedlizard55-lab.github.io/GEMSDOE28/'
        assert row['filename'] in (ROOT/'docs'/'experiment-index.html').read_text()
        detail = (ROOT/'docs'/'sites'/f"{row['site']}.html").read_text()
        assert row['filename'] in detail and row['sha256'] in detail
        assert row['nan_in_footprint'] == 0
    for site, filename in expected.items():
        assert Path(assets[site]['path']).name == filename
    previous = json.loads((ROOT/'evidence/nine_site_best_files_audit.json').read_text())
    assert 'NaN-padded variants' in previous['later_review_annotation']['note']
