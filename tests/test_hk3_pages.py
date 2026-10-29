import copy
import json
from pathlib import Path

import pytest

from scripts import build_hk3_pages

ROOT = Path(__file__).resolve().parents[1]


def test_leaderboard_uses_latest_dated_verified_source_claim():
    verification, source = build_hk3_pages.latest_official_verification()
    snapshot = build_hk3_pages.parse_current_leaderboard_snapshot(verification, source)

    assert snapshot["observed_date"] == verification["verified_on"] == "2026-10-29"
    assert snapshot["participant"] == "xiaofanhu"
    assert snapshot["value"] == 0.4544
    assert snapshot["evidence_class"].startswith("ORGANIZER-PUBLISHED PUBLIC SNAPSHOT")
    assert snapshot["evidence_file"] == "evidence/official-verification-2026-10-29.json"

    rendered = build_hk3_pages.render_all(build_hk3_pages.gather())["index.html"]
    assert "In the latest saved verification dated 2026-10-29" in rendered
    assert "xiaofanhu: 0.4544" in rendered
    assert "evidence/official-verification-2026-10-29.json" in rendered
    assert "On 2026-10-28, the" not in rendered


def test_leaderboard_snapshot_fails_closed_on_stale_or_inconsistent_evidence():
    verification, source = build_hk3_pages.latest_official_verification()

    stale = copy.deepcopy(verification)
    stale["verified_on"] = "2026-10-28"
    with pytest.raises(ValueError, match="filename/date mismatch"):
        build_hk3_pages.parse_current_leaderboard_snapshot(stale, source)

    mismatched_quote = copy.deepcopy(verification)
    claim = next(c for c in mismatched_quote["claims"] if c.get("id") == "OV-08")
    claim["quote"] = "| #1 ... another_user ... 34 submissions | 0.1111 |"
    with pytest.raises(ValueError, match="claim and quoted"):
        build_hk3_pages.parse_current_leaderboard_snapshot(mismatched_quote, source)


def test_official_verification_filename_must_match_its_date(tmp_path, monkeypatch):
    payload = json.loads((ROOT / "evidence/official-verification-2026-10-29.json").read_text())
    wrong_path = tmp_path / "official-verification-2026-10-28.json"
    wrong_path.write_text(json.dumps(payload))
    monkeypatch.setattr(build_hk3_pages, "EV", tmp_path)

    with pytest.raises(ValueError, match="filename/date mismatch"):
        build_hk3_pages.latest_official_verification()

    wrong_path.unlink()
    invalid_date = tmp_path / "official-verification-2026-13-40.json"
    invalid_date.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="Invalid official-verification filename date"):
        build_hk3_pages.latest_official_verification()
