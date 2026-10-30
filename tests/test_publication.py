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


def test_renderer_selects_newest_date_matched_official_observation():
    from scripts.build_hk3_pages import latest_official_observation
    observation, filename = latest_official_observation()
    assert filename == 'official-review-2026-10-30.json'
    assert observation['observed_date_utc'] == '2026-10-30'


def test_current_leaderboard_snapshot_matches_monitor_but_is_not_a_local_score():
    review = json.loads((ROOT/'evidence/official-review-2026-10-30.json').read_text())
    historical = json.loads((ROOT/'evidence/official-review-2026-10-29.json').read_text())
    monitor = json.loads((ROOT/'docs/data/monitor.json').read_text())
    board = next(s for s in review['sources'] if s['url'].endswith('/leaderboard/'))
    first = board['first_place']
    cited = board['user_cited_0_3195']
    assert review['observed_date_utc'] == '2026-10-30'
    assert first == {'rank': 1, 'participant': 'xiaofanhu', 'value': 0.4544}
    assert cited == {'rank': 48, 'participant': 'kpomazi', 'value': 0.3195}
    assert board['rank_47'] == {'rank': 47, 'participant': 'like60986', 'value': 0.3217}
    assert board['rank_50'] == {'rank': 50, 'participant': 'twang', 'value': 0.3169}
    assert historical['observed_date_utc'] == '2026-10-29'
    assert next(s for s in historical['sources'] if s['url'].endswith('/leaderboard/'))['user_cited_0_3195']['rank'] == 47
    assert 'not a file-linked submission-page receipt' in board['observation_type']
    assert monitor['leaderboard']['score_text'] == f"{first['value']:.4f}"
    assert monitor['leaderboard']['rank'] == first['rank']
    assert monitor['leaderboard']['checked_utc'] == review['observed_utc']
    assert monitor['leaderboard']['user_cited_0_3195']['rank'] == cited['rank']
    assert monitor['leaderboard']['limitations'].startswith('Public rows only')
    assert monitor['leaderboard']['evidence_class'].startswith('ORGANIZER-PUBLISHED PUBLIC LEADERBOARD SNAPSHOT')
    assert monitor['note'].startswith('GitHub metadata only; leaderboard is a dated manual public-page observation')
    assert len(monitor['sites']) == 9
    homepage = (ROOT/'docs/index.html').read_text()
    assert '0.4544' in homepage and 'rank 48' in homepage
    assert '2026-10-30' in homepage
    assert 'evidence/official-review-2026-10-30.json' in homepage
    assert 'GITHUB METADATA ONLY' in homepage
    assert 'No latest-head raster/score audit is claimed' in homepage
    assert 'Three-pass review' in homepage


def test_review_cards_record_historical_and_current_metadata_scopes():
    historical = json.loads((ROOT/'evidence/2026-10-29-repo-review-run-card.json').read_text())
    current = json.loads((ROOT/'evidence/live-source-review-card-2026-10-30.json').read_text())
    monitor = json.loads((ROOT/'docs/data/monitor.json').read_text())
    assert historical['verdict'] == 'negative'
    assert historical['experiments_run'] == historical['new_tiffs_created'] == 0
    assert historical['submission_slots_used'] == 0
    assert historical['current_public_leaderboard_snapshot']['user_cited_0_3195']['rank'] == 47
    assert current['classification'] == 'REPOSITORY REVIEW ONLY; NO GEOLOGICAL EXPERIMENT'
    assert current['verdict'] == 'negative'
    assert current['experiments_run'] == current['new_tiffs_created'] == 0
    assert not current['slot_authorized'] and current['submission_slots_used'] == 0
    assert current['holdout']['evidence_class'] == 'NOT RUN; NO HOLDOUT-DTI'
    assert current['holdout']['evaluator_version'] is None
    assert current['holdout']['dti'] is None and current['holdout']['ci95'] is None
    assert current['registry_correlation_overlap']['candidate_surface_spearman'] is None
    assert current['registry_correlation_overlap']['complete_registry_verified'] is False
    assert current['raster_sha256'] is None and current['submission_name'] is None
    assert current['submission_note'] is None and current['leaderboard_estimate'] is None
    assert current['validator_output']['status'] == 'NOT RUN: no new candidate raster'
    assert current['validator_output']['downloadable_approved_submission'] is None
    assert current['test_results']['status'] == 'PASS'
    assert current['github_source_refresh']['changed'] == 9
    assert current['github_source_refresh']['unavailable'] == 0
    assert current['github_source_refresh']['latest_heads'] == {
        row['site']: row['latest_ref'] for row in monitor['sites']}
    assert current['public_leaderboard_observation']['user_cited_0_3195']['rank'] == 48
    assert current['public_leaderboard_observation']['evidence_class'].startswith('ORGANIZER-PUBLISHED PUBLIC LEADERBOARD SNAPSHOT')


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
    assert 'docs/executive-summary.html' in (ROOT/'index.html').read_text()  # root redirect
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
