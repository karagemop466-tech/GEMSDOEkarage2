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
