"""Published research downloads must be exact saved bytes, never slot-approved."""
from __future__ import annotations

import json
from pathlib import Path
import zipfile

import numpy as np
import rasterio
from rasterio.transform import from_origin

from scripts import audit_public_downloads as mod

ROOT = Path(__file__).resolve().parents[1]


def make_fixture(tmp_path):
    downloads = tmp_path / 'docs/downloads'
    downloads.mkdir(parents=True)
    stem = 'negative-research'
    tif = downloads / f'{stem}.tif'
    transform = from_origin(243350, 4508550, 100, 100)
    array = np.zeros((5, 6), np.float32)
    array[2, 3] = 1
    with rasterio.open(tif, 'w', driver='GTiff', height=5, width=6,
                       count=1, dtype='float32', crs='EPSG:32611', transform=transform) as ds:
        ds.write(array, 1)
    grid = dict(shape=[5, 6], crs='EPSG:32611', transform=list(transform)[:6])
    (tmp_path / 'evidence').mkdir()
    (tmp_path / 'evidence/geometry-audit.json').write_text(json.dumps({'template': grid}))
    card_path = tmp_path / 'evidence/card.json'
    card = dict(raster=f'docs/downloads/{stem}.tif', raster_sha256=mod.digest_file(tif),
                submission_name=stem, note='Negative research only', verdict='negative')
    card_path.write_text(json.dumps(card))
    (tmp_path / 'evidence/selector.json').write_text(json.dumps(dict(verdict='negative',
        slot_authorized=False, source_run_card='evidence/card.json')))
    with zipfile.ZipFile(tif.with_suffix('.zip'), 'w') as out:
        out.write(tif, tif.name)
    args = (tmp_path, stem, 'evidence/card.json', 'evidence/selector.json', True, grid)
    return args, card_path


def test_current_saved_downloads_are_hash_bound_but_no_file_is_approved():
    result = mod.audit()
    assert result == json.loads((ROOT / 'evidence/public_downloads_audit.json').read_text())
    assert result == json.loads((ROOT / 'docs/evidence/public_downloads_audit.json').read_text())
    assert result['inventory_status'] == 'PASS_RESEARCH_ONLY'
    assert result['verdict'] == 'negative'
    assert result['downloadable_approved_submission'] is None
    assert result['score_estimate'] is None
    hk3 = json.loads((ROOT / 'evidence/hk3/run_card.json').read_text())
    assert len(result['artifacts']) == 7
    blocked = [r for r in result['artifacts'] if r['kind'] == 'blocked_candidate']
    assert len(blocked) == 1 and blocked[0]['raster_sha256'] == hk3['raster']['sha256']
    assert blocked[0]['status'] == 'VERIFIED_RESEARCH_ONLY'
    assert blocked[0]['ok_to_submit'] is False and blocked[0]['slot_authorized'] is False
    for key in ('current_release_decision_hash_bound', 'current_release_decision_negative',
                'literal_registry_stop_recorded', 'registry_incompleteness_disclosed',
                'historical_selector_marked_superseded'):
        assert blocked[0]['checks'][key] is True
    for record in result['artifacts']:
        assert record['ok_to_submit'] is False
        assert record['slot_authorized'] is False
        assert record['checks']['whole_array_finite'] and record['checks']['range_0_1']
        assert record['checks']['card_sha_matches_saved_bytes']
        assert record['checks']['mirror_transform_match']


def test_candidate_fails_closed_when_selector_or_card_disagree(tmp_path):
    import shutil
    args, card_path = make_fixture(tmp_path)
    root, stem, card_rel, selector_rel, has_zip, grid = args
    # research card + "candidate" kind => the PROMOTE requirement fails closed
    bad = mod.audit_artifact(root, stem, card_rel, selector_rel, has_zip, grid, 'candidate')
    assert bad['status'] == 'FAIL_CLOSED' and bad['ok_to_submit'] is False
    # a PROMOTE card whose selector is negative must also fail closed
    card = json.loads(card_path.read_text())
    card.update(verdict='PROMOTE', gates={'a': True, 'unique_literal_vs_all_registry_rasters': True}, holdout={'evidence_class': 'HOLDOUT-DTI'})
    card_path.write_text(json.dumps(card))
    still = mod.audit_artifact(root, stem, card_rel, selector_rel, has_zip, grid, 'candidate')
    assert still['status'] == 'FAIL_CLOSED' and still['checks']['selector_explicit_candidate'] is False
    # matching selector bound to the saved bytes => verified candidate
    (root / selector_rel).write_text(json.dumps(dict(verdict='candidate_approved_by_automated_gates', ok_to_submit=True,
        slot_authorized=False, source_run_card=card_rel, raster_sha256=card['raster_sha256'])))
    good = mod.audit_artifact(root, stem, card_rel, selector_rel, has_zip, grid, 'candidate')
    assert good['status'] == 'VERIFIED_CANDIDATE_FOR_UPLOAD' and good['ok_to_submit'] is True
    # a second candidate in the inventory is refused
    second = tmp_path / 'docs/downloads/second.tif'
    shutil.copyfile(root / f'docs/downloads/{stem}.tif', second)
    with __import__('zipfile').ZipFile(second.with_suffix('.zip'), 'w') as out:
        out.write(second, second.name)
    import pytest
    mp = pytest.MonkeyPatch()
    try:
        mp.setattr(mod, 'ARTIFACTS', ((stem, card_rel, selector_rel, True, 'candidate'), ('second', card_rel, selector_rel, True, 'candidate')))
        mp.setattr(mod, 'ROOT', root)
        result = mod.audit(root)
    finally:
        mp.undo()
    assert result['inventory_status'] == 'FAIL_CLOSED' and result['downloadable_approved_submission'] is None


def test_b4_literal_followup_is_bound_to_saved_tif_and_negative_registry():
    b4 = json.loads((ROOT / 'evidence/b4/literal_followup.json').read_text())
    prior = json.loads((ROOT / 'evidence/b4/final_registry_audit.json').read_text())
    assert b4['candidate_sha256'] == mod.digest_file(ROOT / b4['candidate_file'])
    assert prior['candidate_file_sha256'] == b4['candidate_sha256']
    assert prior['unique'] is False and prior['worst_dot_overlap'] == 1.0
    assert b4['candidate_dots_within_3px_of_lattice'] == b4['candidate_positive_pixels_inside_footprint'] == 51914
    assert b4['candidate_overlap_fraction'] == 1.0
    assert b4['minimum_overlap_at_this_budget_from_counting_bound'] > 0.70
    assert b4['slot_authorized'] is False


def test_fixture_integrity_and_missing_selector_fail_closed(tmp_path):
    args, _ = make_fixture(tmp_path)
    good = mod.audit_artifact(*args)
    assert good['status'] == 'VERIFIED_RESEARCH_ONLY'
    assert good['diagnostics']['positive_pixels'] == 1
    selector = tmp_path / 'evidence/selector.json'
    selector.write_text('{"verdict":"promote", "slot_authorized":true}')
    bad = mod.audit_artifact(*args)
    assert bad['status'] == 'FAIL_CLOSED' and bad['ok_to_submit'] is False
    assert bad['checks']['selector_explicit_negative'] is False


def test_tampered_tif_card_and_extra_zip_member_are_not_verified(tmp_path):
    args, card_path = make_fixture(tmp_path)
    tif = tmp_path / 'docs/downloads/negative-research.tif'
    with rasterio.open(tif, 'r+') as ds:
        ds.write(np.full((5, 6), 1.01, np.float32), 1)
    changed = mod.audit_artifact(*args)
    assert changed['status'] == 'FAIL_CLOSED'
    assert changed['checks']['range_0_1'] is False
    assert changed['checks']['card_sha_matches_saved_bytes'] is False
    # Even a matching hash in an edited run card cannot make an invalid raster valid.
    card = json.loads(card_path.read_text())
    card['raster_sha256'] = mod.digest_file(tif)
    card_path.write_text(json.dumps(card))
    assert not mod.audit_artifact(*args)['checks']['range_0_1']
    zip_path = tif.with_suffix('.zip')
    with zipfile.ZipFile(zip_path, 'a') as out:
        out.writestr('second.tif', b'not a GeoTIFF')
    assert mod.inspect_zip(zip_path, tif, card['raster_sha256']) is False


def test_unreadable_tif_or_malformed_card_stays_research_negative(tmp_path):
    args, card_path = make_fixture(tmp_path)
    tif = tmp_path / 'docs/downloads/negative-research.tif'
    tif.write_bytes(b'corrupt')
    result = mod.audit_artifact(*args)
    assert result['status'] == 'FAIL_CLOSED'
    assert result['checks']['tif_readable'] is False
    assert result['ok_to_submit'] is False
    card_path.write_text('[]')
    assert mod.audit_artifact(*args)['checks']['card_readable'] is False


def test_unknown_published_raster_is_never_silently_allowed(tmp_path, monkeypatch):
    args, _ = make_fixture(tmp_path)
    monkeypatch.setattr(mod, 'ARTIFACTS', ((args[1], args[2], args[3], True),))
    extra = tmp_path / 'docs/downloads/new-unreviewed.tif'
    extra.write_bytes(b'not cleared')
    result = mod.audit(tmp_path)
    assert result['inventory_status'] == 'FAIL_CLOSED'
    assert result['unexpected_downloads'] == ['new-unreviewed.tif']
    assert result['downloadable_approved_submission'] is None
