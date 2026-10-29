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


def test_pinned_current_source_review_is_complete_but_not_a_raster_or_score_audit():
    report = json.loads((ROOT/'evidence/upstream-source-review-2026-10-29.json').read_text())
    feed = json.loads((ROOT/'docs/field-notes/data/source-feed.json').read_text())
    heads = {row['site']: row['current_head'] for row in feed['sources']}
    assert report['schema'] == 'gems.commit_pinned_upstream_review.v1'
    assert len(report['sites']) == 9
    assert report['tree_truncated_for_any_site'] is False
    assert report['binary_raster_contents_downloaded'] is False
    assert all(site['tree_truncated'] is False for site in report['sites'])
    assert all(len(site['current_head']) == len(site['current_tree_sha']) == 40 for site in report['sites'])
    assert all(site['current_head'] == heads[site['repo']] for site in report['sites'])
    assert all(site['current_tree_sha'] != site['current_head'] for site in report['sites'])
    assert all(site['recursive_tree_url'].endswith(f"/{site['current_tree_sha']}?recursive=1") for site in report['sites'])
    assert all(site['reviewed_sources'] and site['tree_blob_entries'] > 0 for site in report['sites'])
    assert all('no full raster download' in site['review_boundary'].lower() for site in report['sites'])


def test_official_page_observation_is_separate_from_candidate_receipts():
    report = json.loads((ROOT/'evidence/official-review-2026-10-29.json').read_text())
    board = report['sources'][1]
    assert board['first_place'] == {'rank': 1, 'participant': 'xiaofanhu', 'value': 0.4544}
    assert 'NOT A SUBMISSION-PAGE RECEIPT' in board['observation_type']
    assert 'No candidate leaderboard estimate' in report['release_conclusion']


def test_review_run_card_records_no_candidate_no_score_and_no_slot():
    card = json.loads((ROOT/'evidence/repo-review-run-card-2026-10-29.json').read_text())
    assert card['promotion_verdict'] == 'negative'
    assert card['experiments_run_this_review'] == 0
    assert card['raster_sha256'] is None
    assert card['submission_name'] is None and card['submission_note'] is None
    assert card['holdout_dti']['value'] is None
    assert card['validator']['candidate_created'] is False
    assert card['registry']['surface_before_placement_overlap_within_3px'] is None
    assert card['registry']['final_dots_overlap_within_3px'] is None
    assert card['slot_selection'].lower().startswith('not performed')


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
    card = json.loads((ROOT/'evidence/h1/run_card.json').read_text())
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
    assert 'scripts/build_hk3_pages.py --check' in workflow
    assert 'OK TO SUBMIT' in (ROOT/'docs/index.html').read_text()
