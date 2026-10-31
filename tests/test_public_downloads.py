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


def test_current_saved_downloads_are_hash_bound_and_research_only():
    result = mod.audit()
    assert result == json.loads((ROOT / 'evidence/public_downloads_audit.json').read_text())
    assert result == json.loads((ROOT / 'docs/evidence/public_downloads_audit.json').read_text())
    assert result['inventory_status'] == 'PASS_RESEARCH_ONLY'
    assert result['downloadable_approved_submission'] is None
    assert result['score_estimate'] is None and result['slot_authorized'] is False
    assert all(r['exterior_convention'].startswith('not assessed') for r in result['artifacts'])
    hk3 = json.loads((ROOT / 'evidence/hk3/run_card.json').read_text())
    # 12 registered research artifacts (main 11 incl. GBSP, + H-C E1 NaN exterior).
    assert len(result['artifacts']) == 13  # 11 on main (incl. GBSP) + H-C E1 + blind-geothermal registered on merge
    ha_name = 'gemsdoekarage2-hA-intersection-propensity-aad3569983ab'
    ha = next(r for r in result['artifacts'] if r['file'].endswith(ha_name + '.tif'))
    ha_card = json.loads((ROOT / 'evidence/hA-intersection/run_card.json').read_text())
    assert ha['status'] == 'VERIFIED_RESEARCH_ONLY'
    assert ha['ok_to_submit'] is False and ha['slot_authorized'] is False
    assert ha_card['holdout'] is None and ha_card['leaderboard_estimate'] is None
    assert ha_card['organizer_confirmed_score'] is None
    assert ha_card['gates']['shared_uniqueness_gate_vs_lattice'] == 'DUPLICATE_STOP'
    assert ha_card['gates']['frac_dots_within_3px_of_lattice'] == 1.0
    assert ha_card['registry_scope'].startswith('lattice witness only')
    hr4 = json.loads((ROOT / 'evidence/hr4-intersection/run_card.json').read_text())
    assert hr4['verdict'] == 'negative' and hr4['holdout'] is None
    assert hr4['gates']['shared_uniqueness_gate_vs_lattice'] == 'DUPLICATE_STOP'
    assert hr4['gates']['frac_dots_within_3px_of_lattice'] > 0.70
    assert hr4['leaderboard_estimate'] is None and hr4['organizer_confirmed_score'] is None
    found = [r for r in result['artifacts'] if r['raster_sha256'] == hk3['raster']['sha256']]
    assert len(found) == 1 and found[0]['kind'] == 'research'
    assert found[0]['checks']['current_assessment_negative_and_hash_bound'] is True
    assessment = json.loads((ROOT / 'evidence/hk3/current_release_assessment.json').read_text())
    assert assessment == json.loads((ROOT / 'docs/evidence/hk3/current_release_assessment.json').read_text())
    assert assessment['leakage_canary_passed'] is False
    assert assessment['validator_output']['portal_acceptance'] is None
    assert assessment['submission_name'] is None and assessment['submission_note'] is None
    for record in result['artifacts']:
        assert record['status'] == 'VERIFIED_RESEARCH_ONLY'
        assert record['ok_to_submit'] is False and record['slot_authorized'] is False
        assert record['checks']['whole_array_finite'] and record['checks']['range_0_1']
        assert record['checks']['card_sha_matches_saved_bytes']
        assert record['checks']['mirror_transform_match']


def test_stale_unverified_tif_is_not_published_as_a_submission():
    stale = ROOT / 'docs/downloads/gemsdoe-karage2-gw-nfs-h1-20261029-zeros.tif'
    assert not stale.exists()
    for name in ('index.html', 'executive-summary.html'):
        page = (ROOT / 'docs' / name).read_text()
        assert 'OK TO SUBMIT: NO' in page
        assert 'gw-nfs-h1-20261029-zeros' not in page
    assert 'docs/index.html' in (ROOT / 'index.html').read_text()
    report = mod.audit()
    assert report['downloadable_approved_submission'] is None
    assert all(r['ok_to_submit'] is False for r in report['artifacts'])


def test_forged_candidate_and_selector_always_fail_closed(tmp_path, monkeypatch):
    args, card_path = make_fixture(tmp_path)
    root, stem, card_rel, selector_rel, has_zip, grid = args
    for gates in ({}, {'a': True}, {'unique_literal_vs_all_registry_rasters': True},
                  {'unique_literal_vs_all_registry_rasters': False, 'literal_rule_exception_applied': True}):
        card = json.loads(card_path.read_text())
        card.update(verdict='PROMOTE', gates=gates, holdout={'evidence_class': 'HOLDOUT-DTI'})
        card_path.write_text(json.dumps(card))
        (root / selector_rel).write_text(json.dumps(dict(verdict='candidate_approved_by_automated_gates',
            ok_to_submit=True, slot_authorized=False, source_run_card=card_rel, raster_sha256=card['raster_sha256'])))
        result = mod.audit_artifact(root, stem, card_rel, selector_rel, has_zip, grid, 'candidate')
        assert result['status'] == 'FAIL_CLOSED' and result['ok_to_submit'] is False
        assert result['checks']['independent_release_verification_implemented'] is False
    monkeypatch.setattr(mod, 'ARTIFACTS', ((stem, card_rel, selector_rel, True, 'candidate'),))
    result = mod.audit(root)
    assert result['inventory_status'] == 'FAIL_CLOSED'
    assert result['downloadable_approved_submission'] is None
    assert result['slot_authorized'] is False


def test_external_gdal_sidecar_is_rejected_even_if_tiff_hash_is_unchanged(tmp_path):
    args, _ = make_fixture(tmp_path)
    tif = tmp_path / 'docs/downloads/negative-research.tif'
    before = mod.digest_file(tif)
    # A sidecar not covered by the TIFF hash can change GDAL's interpreted mask.
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=False):
        with rasterio.open(tif, 'r+') as ds:
            mask = np.full((5, 6), 255, dtype=np.uint8)
            mask[0, 0] = 0
            ds.write_mask(mask)
    assert tif.with_suffix('.tif.msk').is_file()
    assert mod.digest_file(tif) == before
    report = mod.audit_artifact(*args)
    assert report['status'] == 'FAIL_CLOSED' and report['ok_to_submit'] is False
    assert report['checks']['tif_readable'] is False
    assert report['checks']['self_contained_tiff'] is False
    assert 'companion' in report['diagnostics']['error'].lower()


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
    selector.write_text(json.dumps({'verdict': 'negative', 'slot_authorized': False,
                                    'source_run_card': 'evidence/card.json', 'ok_to_submit': True}))
    contradictory = mod.audit_artifact(*args)
    assert contradictory['status'] == 'FAIL_CLOSED'
    assert contradictory['checks']['selector_explicit_negative'] is False


def test_negative_assessment_must_be_hash_bound_and_confined_to_evidence(tmp_path):
    args, card_path = make_fixture(tmp_path)
    root, stem, card_rel, selector_rel, _, _ = args
    card = json.loads(card_path.read_text())
    selector_path = root / selector_rel
    selector = json.loads(selector_path.read_text())
    selector['current_release_assessment'] = 'evidence/current-release.json'
    selector_path.write_text(json.dumps(selector))
    assessment_path = root / selector['current_release_assessment']
    assessment = dict(status='negative_research_only', ok_to_submit=False, slot_authorized=False,
                      candidate=f'docs/downloads/{stem}.tif', raster_sha256=card['raster_sha256'],
                      source_run_card=card_rel)
    assessment_path.write_text(json.dumps(assessment))
    valid = mod.audit_artifact(*args)
    assert valid['status'] == 'VERIFIED_RESEARCH_ONLY'
    assert valid['checks']['current_assessment_negative_and_hash_bound'] is True
    for key, value in [('raster_sha256', 'wrong'), ('status', 'approved'),
                       ('source_run_card', 'elsewhere.json'), ('slot_authorized', True)]:
        altered = dict(assessment, **{key: value})
        assessment_path.write_text(json.dumps(altered))
        bad = mod.audit_artifact(*args)
        assert bad['status'] == 'FAIL_CLOSED'
        assert bad['checks']['current_assessment_negative_and_hash_bound'] is False
    assessment_path.write_text(json.dumps(assessment))
    selector['current_release_assessment'] = '../outside.json'
    selector_path.write_text(json.dumps(selector))
    escaped = mod.audit_artifact(*args)
    assert escaped['status'] == 'FAIL_CLOSED'
    assert escaped['checks']['current_assessment_negative_and_hash_bound'] is False


def test_negative_card_with_a_hidden_approval_flag_fails_closed(tmp_path):
    args, card_path = make_fixture(tmp_path)
    card = json.loads(card_path.read_text())
    card['approved_for_weekly_slot'] = True
    card_path.write_text(json.dumps(card))
    result = mod.audit_artifact(*args)
    assert result['status'] == 'FAIL_CLOSED'
    assert result['checks']['card_verdict_negative'] is False


def test_misleading_download_metadata_fails_closed(tmp_path):
    args, _ = make_fixture(tmp_path)
    tif = tmp_path / 'docs/downloads/negative-research.tif'
    metadata = {'sha256': mod.digest_file(tif), 'promoted': False,
                'approved_for_weekly_slot': False, 'ok_to_submit': False}
    metadata_path = tif.with_suffix('.json')
    metadata_path.write_text(json.dumps(metadata))
    assert mod.audit_artifact(*args)['status'] == 'VERIFIED_RESEARCH_ONLY'
    metadata['ok_to_submit'] = True
    metadata_path.write_text(json.dumps(metadata))
    result = mod.audit_artifact(*args)
    assert result['status'] == 'FAIL_CLOSED'
    assert result['checks']['metadata_research_only_and_hash_bound'] is False


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
