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
