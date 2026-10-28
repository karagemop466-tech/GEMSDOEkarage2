from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from refresh_sources import build_feed


def test_feed_reports_changed_and_unavailable_without_exposing_error_details():
    snapshot = {"observed_utc": "2026-10-27T00:00:00Z", "heads": {"GEMSDOE24": "a", "GEMSDOE25": "b", "GEMSDOE27": "c"}}
    def get(repo):
        if repo == "GEMSDOE25":
            return "changed"
        if repo == "GEMSDOE27":
            raise OSError("sensitive details should not be published")
        return "a"
    feed = build_feed(snapshot, get)
    assert feed["summary"] == {"total": 3, "changed": 1, "unavailable": 1}
    assert [r["status"] for r in feed["sources"]] == ["unchanged", "changed_since_review", "unavailable"]
    assert feed["sources"][2]["error"] == "OSError"
    assert "sensitive" not in str(feed)


def test_github_head_uses_guarded_bounded_fetch(monkeypatch):
    import refresh_sources
    calls = []
    def guarded_get(url, *, github_token=None):
        calls.append((url, github_token))
        return '{"sha": "' + 'a' * 40 + '"}'
    monkeypatch.setattr(refresh_sources, 'get', guarded_get)
    assert refresh_sources.github_head('GEMSDOE24', 'token') == 'a' * 40
    assert calls == [('https://api.github.com/repos/buffedlizard55-lab/GEMSDOE24/commits/main', 'token')]


def test_bad_github_payload_fails_to_unavailable(monkeypatch):
    import refresh_sources
    monkeypatch.setattr(refresh_sources, 'get', lambda *args, **kwargs: '[]')
    snapshot = {"observed_utc": "2026-10-27", "heads": {"GEMSDOE24": "a"}}
    feed = refresh_sources.build_feed(snapshot, refresh_sources.github_head)
    assert feed['sources'][0]['status'] == 'unavailable'
    assert feed['sources'][0]['error'] == 'TypeError'


def test_guard_blocks_cross_origin_redirect_before_forwarding_credentials():
    import pytest
    from urllib.request import Request
    from refresh_feed import SameOriginRedirect
    handler = SameOriginRedirect()
    original = Request('https://api.github.com/repos/example', headers={'Authorization': 'Bearer test'})
    with pytest.raises(ValueError, match='cross-origin'):
        handler.redirect_request(original, None, 302, 'Found', {}, 'https://example.com/other')
    redirected = handler.redirect_request(original, None, 302, 'Found', {}, 'https://api.github.com/other')
    assert redirected.full_url == 'https://api.github.com/other'
