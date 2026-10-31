"""Mandatory stops cannot be erased by verdict strings or publication exceptions."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import build_hk3_pages as pages

ROOT = Path(__file__).resolve().parents[1]


def test_historical_hk3_promotion_is_preserved_but_not_eligible():
    historical = json.loads((ROOT / 'evidence/hk3/history/run_card-before-protocol-correction.json').read_text())
    assert historical['verdict'] == 'PROMOTE'
    assert historical['gates']['literal_rule_exception_applied'] is True
    assert historical['gates']['unique_literal_vs_all_registry_rasters'] is False
    from scripts.hk3_release_policy import publication_eligible
    assert not publication_eligible(historical)
    # Relabeling cannot make a stopped, incomplete card pass the common schema.
    historical['verdict'] = 'promote'
    assert not publication_eligible(historical)


def test_all_pages_fail_closed_even_if_the_verdict_is_forged():
    data = pages.gather()
    forged = copy.deepcopy(data)
    forged['card']['verdict'] = 'promote'
    forged['card']['protocol_stop_triggered'] = False
    forged['card']['gates']['literal_rule_exception_applied'] = False
    from scripts.hk3_release_policy import REQUIRED_GATES
    from test_readiness import good
    forged['card']['gates'].update({key: True for key in REQUIRED_GATES})
    forged['card']['release_evidence'] = good()  # matching-looking schema is not authenticated evidence
    for name, text in pages.render_all(forged).items():
        if name.endswith('.html'):
            release = json.loads((ROOT / 'evidence/halo/final_generation.json').read_text())
            expected = ('OK TO SUBMIT: 1 FILE · SEE RELEASE' if release['verdict']['ok_to_submit']
                        else 'OK TO SUBMIT: NO')
            assert expected in text
            assert 'DO NOT SUBMIT' in text or 'DO NOT RESUBMIT' in text


@pytest.mark.parametrize('command', ['features', 'e2', 'bridge', 'e3', 'card', 'anchors'])
def test_hk3_retired_commands_leave_cards_and_tif_unchanged(command):
    card = json.loads((ROOT / 'evidence/hk3/run_card.json').read_text())
    paths = [ROOT / card['raster']['file'], ROOT / 'evidence/hk3/run_card.json',
             ROOT / 'evidence/hk3/e2.json', ROOT / 'evidence/hk3/e3_generation.json']
    before = [hashlib.sha256(path.read_bytes()).digest() for path in paths]
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/hk3.py'), command],
                            cwd=ROOT, capture_output=True, text=True, timeout=20)
    assert result.returncode != 0
    assert 'HK3 is retired' in result.stderr
    assert before == [hashlib.sha256(path.read_bytes()).digest() for path in paths]


def test_direct_generation_entry_point_is_retired_before_data_or_writer(tmp_path):
    from scripts import hk3

    # The retired module no longer exposes a loader, writer, or experiment code.
    assert not hasattr(hk3, 'k2') and not hasattr(hk3, 'write_submission')
    with pytest.raises(RuntimeError, match='HK3 is retired'):
        hk3.cmd_e3('must-not-exist', 'Do not submit', .009, reuse_surface=True)
    assert not list(tmp_path.iterdir())


def test_nine_current_focus_summaries_have_no_submission_downloads():
    data = pages.gather()
    rendered = pages.render_all(data)
    for s in data['focus']:
        text = rendered[f"focus/{s['site']}.html"]
        assert s['file'] in text and s['sha256'] in text
        assert 'USER-REPORTED / UNVERIFIED' in text
        assert 'DO NOT RESUBMIT' in text and 'unavailable' in text
        assert not re.search(r'<a\b[^>]*\sdownload(?:[\s=>])', text)


def test_protocol_review_is_reproducible_and_not_a_new_score():
    from scripts.review_hk3_protocol import review, OUTPUT
    result = review()
    assert result == json.loads((ROOT / 'evidence' / OUTPUT).read_text())
    assert result == json.loads((ROOT / 'docs/evidence' / OUTPUT).read_text())
    assert result['holdout_dti'] is None and result['leaderboard_estimate'] is None
    assert result['verdict'] == 'negative'
    assert result['new_experiments_run'] == result['submission_slots_used'] == 0
    assert result['correlation_overlap_vs_registry']['max_final_dot_overlap_3px'] > .70
    assert result['validator_output']['values_in_0_1'] is True
    assert result['validator_output']['organizer_crs_shape_transform_match'] is None
    assert len(result['submission_note']) <= 140


def test_concurrent_publication_adapter_has_no_minimal_card_bypass():
    from scripts.hk3_release_policy import publication_eligible, REQUIRED_GATES
    from test_readiness import good
    partial = dict(verdict='PROMOTE', protocol_stop_triggered=False,
                   gates={key: True for key in REQUIRED_GATES})
    partial['gates']['literal_rule_exception_applied'] = False
    assert not publication_eligible(partial)
    clean = copy.deepcopy(partial)
    clean['release_evidence'] = good()
    assert publication_eligible(clean)  # synthetic schema, not authenticated evidence
    for key in REQUIRED_GATES:
        for bad in (None, False, 1, 'true', [], {}):
            changed = copy.deepcopy(clean)
            changed['gates'][key] = bad
            assert not publication_eligible(changed)
        changed = copy.deepcopy(clean)
        del changed['gates'][key]
        assert not publication_eligible(changed)
    for malformed in (None, [], True, {}, {'gates': []}):
        assert not publication_eligible(malformed)
    for key, value in (('protocol_stop_triggered', True), ('verdict', 'negative')):
        assert not publication_eligible(dict(clean, **{key: value}))
    clean['gates']['literal_rule_exception_applied'] = True
    assert not publication_eligible(clean)


def test_root_submission_status_does_not_reintroduce_retracted_approval():
    text = (ROOT / 'SUBMISSION_STATUS.md').read_text()
    assert 'NO APPROVED FILE' in text and 'DO NOT SUBMIT' in text
    assert 'will **not** trigger' not in text
    assert 'Verdict:** PROMOTE' not in text
