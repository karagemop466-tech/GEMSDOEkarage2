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


def test_current_leaderboard_snapshot_matches_monitor_but_is_not_a_local_score():
    review = json.loads((ROOT/'evidence/official-review-2026-10-29.json').read_text())
    monitor = json.loads((ROOT/'docs/data/monitor.json').read_text())
    board = next(s for s in review['sources'] if s['url'].endswith('/leaderboard/'))
    first = board['first_place']
    cited = board['user_cited_0_3195']
    assert review['observed_date_utc'] == '2026-10-29'
    assert first == {'rank': 1, 'participant': 'xiaofanhu', 'value': 0.4544}
    assert cited == {'rank': 47, 'participant': 'kpomazi', 'value': 0.3195}
    assert 'not a file-linked submission-page receipt' in board['observation_type']
    assert monitor['leaderboard']['score_text'] == f"{first['value']:.4f}"
    assert monitor['leaderboard']['rank'] == first['rank']
    assert monitor['leaderboard']['checked_utc'] == review['observed_utc']
    assert monitor['leaderboard']['limitations'].startswith('Public rows only')
    assert len(monitor['sites']) == 9
    homepage = (ROOT/'docs/index.html').read_text()
    assert '0.4544' in homepage and 'rank 47' in homepage
    assert 'GITHUB METADATA ONLY' in homepage
    assert 'No latest-head raster/score audit is claimed' in homepage
    assert 'Three-pass review' in homepage


def test_public_summary_marks_latest_refresh_failure_and_hr4_negative():
    page = (ROOT/'docs/executive-summary.html').read_text()
    assert 'LAST SUCCESSFUL SNAPSHOT' in page
    assert '9 of 9 unavailable' in page
    assert 'PR #74 H-Rank-4 is not a candidate' in page
    assert '81.32%' in page
    assert 'do not download or submit its TIFF' in page
    assert (ROOT/'docs/evidence/hr4-main-merge-reaudit-2026-10-29.json').is_file()


def test_review_card_records_no_experiment_no_raster_and_current_metadata_scope():
    card = json.loads((ROOT/'evidence/2026-10-29-repo-review-run-card.json').read_text())
    monitor = json.loads((ROOT/'docs/data/monitor.json').read_text())
    assert card['verdict'] == 'negative'
    assert card['experiments_run'] == card['new_tiffs_created'] == 0
    assert not card['slot_authorized'] and card['submission_slots_used'] == 0
    assert card['holdout']['dti'] is None and card['holdout']['ci95'] is None
    assert card['raster_sha256'] is None and card['proposed_submission_name'] is None
    assert card['proposed_submission_note'] is None
    assert card['focus_source_refresh']['changed'] == 9
    assert card['focus_source_refresh']['unavailable'] == 0
    assert card['focus_source_refresh']['latest_heads'] == {
        row['site']: row['latest_ref'] for row in monitor['sites']}
    review = (ROOT/'research/2026-10-29-scorecard-and-monitor-review.md').read_text()
    assert all(head in review for head in card['focus_source_refresh']['latest_heads'].values())
    assert card['current_public_leaderboard_snapshot']['first_place']['value'] == 0.4544
    assert card['current_public_leaderboard_snapshot']['user_cited_0_3195']['rank'] == 47


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


def test_pages_deployment_renders_the_summary_after_github_feed_refresh():
    workflow = (ROOT/'.github/workflows/pages.yml').read_text()
    deploy = workflow.split('  deploy:\n', 1)[1]
    feed = deploy.index('python scripts/refresh_feed.py --github-only')
    sources = deploy.index('python scripts/refresh_sources.py')
    render = deploy.index('python scripts/build_hk3_pages.py')
    copy = deploy.index('cp -a docs/. "$RUNNER_TEMP/gems-pages/docs/"')
    assert feed < sources < render < copy
    assert 'DrivenData' not in deploy[feed:render]
