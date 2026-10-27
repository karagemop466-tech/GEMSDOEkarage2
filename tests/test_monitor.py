import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import refresh_feed as feed


def table(first='0.4544'):
    return f'''<html><table><thead><tr><th>Rank</th><th>Participant</th><th>Best<br>public<br>DW-Tversky</th></tr></thead>
    <tbody><tr><td>#1</td><td>Someone</td><td>{first}</td></tr><tr><td>#2</td><td>Else</td><td>0.34</td></tr></tbody></table></html>'''


def test_parse_organizer_table_uses_rank_and_label():
    assert feed.parse_leaderboard(table()) == '0.4544'


@pytest.mark.parametrize('html', ['<h1>Login</h1>', table('1.2'), table('0.4 / 0.5'),
    table().replace('#2', '#1')])
def test_bad_or_ambiguous_leaderboard_fails_closed(html):
    with pytest.raises(ValueError):
        feed.parse_leaderboard(html)


def test_unavailable_preserves_dated_snapshot_and_changed_heads(monkeypatch):
    old = {'leaderboard': {'status': 'snapshot', 'score_text': '0.5', 'checked_utc': '2026-01-01T00:00:00Z',
                           'source': 'official', 'evidence_class': 'public'}}
    man = {'assets': [{'role': 'focus', 'site': 'a', 'repo': 'owner/repo', 'ref': 'a'*40}]}
    def fake_get(url, **kwargs):
        if url == feed.LEADERBOARD:
            raise OSError('not reachable')
        return json.dumps({'sha': 'b'*40})
    monkeypatch.setattr(feed, 'get', fake_get)
    result = feed.refresh(old, man)
    assert result['leaderboard']['status'] == 'unavailable'
    assert result['leaderboard']['last_successful']['score_text'] == '0.5'
    assert result['sites'][0]['status'] == 'changed'


def test_github_only_does_not_relabel_snapshot(monkeypatch):
    old = {'leaderboard': {'status': 'snapshot', 'score_text': '0.1', 'checked_utc': '2026-01-01T00:00:00Z'}}
    man = {'assets': []}
    monkeypatch.setattr(feed, 'get', lambda *a, **kw: pytest.fail('unexpected network'))
    result = feed.refresh(old, man, github_only=True)
    assert result['leaderboard'] == old['leaderboard']


def test_redirect_guard_refuses_cross_host_and_downgrade():
    from urllib.request import Request
    guard = feed.SameOriginRedirect()
    req = Request('https://api.github.com/repos/owner/repo', headers={'Authorization': 'Bearer secret'})
    with pytest.raises(ValueError, match='cross-origin'):
        guard.redirect_request(req, None, 302, 'Found', {}, 'https://elsewhere.example/path')
    with pytest.raises(ValueError, match='cross-origin'):
        guard.redirect_request(req, None, 302, 'Found', {}, 'http://api.github.com/path')
    allowed = guard.redirect_request(req, None, 302, 'Found', {}, 'https://api.github.com/other')
    assert allowed.full_url == 'https://api.github.com/other'


def test_failure_diagnostics_do_not_expose_response_or_exception(monkeypatch):
    page = table('bad private text')
    monkeypatch.setattr(feed, 'get', lambda *a, **kw: page)
    result = feed.refresh({}, {'assets': []})['leaderboard']
    assert result['status'] == 'unavailable'
    assert result['error_reason'] == 'invalid rank-one value'
    assert result['diagnostics']['header_has_public_tversky']
    assert 'private text' not in json.dumps(result)
