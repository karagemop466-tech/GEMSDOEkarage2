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
    assert len(result['artifacts']) == 10
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


def test_hf_correction_reconciles_saved_bytes_and_withdraws_stale_claims():
    tif = ROOT / 'docs/downloads/gemsdoe-hf-alteration-curvature-intersection-20261030.tif'
    card = json.loads((ROOT / 'docs/downloads/gemsdoe-hf-alteration-curvature-intersection-20261030.run-card.json').read_text())
    sidecar = json.loads((ROOT / 'docs/downloads/gemsdoe-hf-alteration-curvature-intersection-20261030.audit.json').read_text())
    correction = json.loads((ROOT / 'evidence/hf-correction-2026-10-31.json').read_text())
    measured = mod.digest_file(tif)
    assert measured == 'e9ea035c8d12d848807c3b71875c8031ca8b49b33f21150ac62e4e7f67c04224'
    assert card['raster_sha256'] == correction['artifact']['sha256_in_current_run_card'] == measured
    assert card['correction_url'] == '../evidence/hf-correction-2026-10-31.json'
    public_correction = ROOT / 'docs/evidence/hf-correction-2026-10-31.json'
    assert public_correction.read_text() == (ROOT / 'evidence/hf-correction-2026-10-31.json').read_text()
    assert sidecar['superseding_correction'] == '../evidence/hf-correction-2026-10-31.json'
    assert (ROOT / 'docs/downloads' / sidecar['superseding_correction']).resolve() == public_correction.resolve()
    verification = correction['verification']
    assert verification['saved_tiff_recomputed']['whole_array_finite_in_range_0_1'] is True
    assert verification['saved_tiff_recomputed']['nan_pixels_all_raster'] == 0
    assert verification['saved_tiff_recomputed']['positive_pixels'] == 18000
    assert verification['owner_mirror_footprint']['outside_finite_count_derived_from_full_raster_finite_count'] == 7111787
    assert all(verification['hash_bindings'][key] for key in (
        'actual_tiff_matches_current_run_card',
        'actual_tiff_matches_saved_audit_sidecar',
        'precorrection_run_card_sha256_matches_prior_revision',
        'precorrection_audit_sidecar_sha256_matches_prior_revision',
        'precorrection_focus_sites_sha256_matches_prior_revision',
        'prior_revision_hashes_independently_checked_with_git_show'))
    assert card['holdout']['evidence_class'].startswith('LEGACY FIXED-FIELD DTI DIAGNOSTIC')
    assert card['holdout']['strict_hide_recover_oof'] is False
    assert card['holdout']['ci95'] is None
    assert card['correlation_and_overlap_vs_registry']['unique_gate_cleared'] is False
    assert card['validator']['strict_format_pass'] is False
    assert card['leakage_canary']['fault_proximity']['auc'] == 1.0
    assert card['leakage_canary']['fault_proximity']['leakage'] is True
    mapping = card['band_mapping_review']
    assert mapping['owner_mirror_names_by_index_1_based'] == {
        '4': 'geod_2ndinv', '5': 'iso_grav_anom_slope', '6': 'tc'}
    assert mapping['curvature_input_index_1_based'] == 12
    assert mapping['official_band_mapping_authenticated'] is False
    assert mapping['source_manifest_sha256'] == mod.digest_file(ROOT / mapping['source_manifest'])
    assert card['ok_to_submit'] is False and card['slot_authorized'] is False
    geological = correction['corrections']['geological_interpretation']
    assert geological['owner_mirror_manifest_sha256'] == mapping['source_manifest_sha256']
    assert geological['official_band_mapping_authenticated'] is False
    assert geological['claimed_radiometric_bands_1_based'] == {'K': 4, 'eTh': 6, 'eU_over_eTh_ratio': 5}
    assert geological['curvature_input_1_based'] == 12
    assert sidecar['sha256'] == correction['artifact']['sha256_measured'] == measured
    assert sidecar['format_validation']['diagnostics']['outside_nan'] == 0
    assert sidecar['format_validation']['diagnostics']['outside_finite'] == 7111787
    assert sidecar['format_validation']['passed'] is False
    assert 'not NaN' in sidecar['irregularities'][-1]
    focus = json.loads((ROOT / 'docs/data/focus-sites.json').read_text())
    row = next(r for r in focus if r.get('site') == 'NEW · GEMSDOEkarage2 H-F (this repo)')
    assert row['unique'] is None and row['submit'] is False and row['ok_to_submit'] is False
    assert 'not established' in row['unique_reason'].lower()
    archived = (ROOT / 'docs/archive-initial-dashboard.html').read_text()
    assert 'evidence/hf-correction-2026-10-31.json' in archived
    assert 'DO NOT SUBMIT' in archived
    inventory = mod.audit()
    artifact = next(r for r in inventory['artifacts'] if r['file'] == correction['artifact']['path'])
    assert artifact['checks']['superseding_correction_hash_bound'] is True
    assert artifact['status'] == 'VERIFIED_RESEARCH_ONLY'
    assert inventory['downloadable_approved_submission'] is None


def test_superseding_correction_is_confined_and_hash_bound(tmp_path, monkeypatch):
    args, card_path = make_fixture(tmp_path)
    root, stem, card_rel, _, _, _ = args
    tif = root / 'docs/downloads' / f'{stem}.tif'
    measured = mod.digest_file(tif)
    correction_rel = 'evidence/correction.json'
    monkeypatch.setitem(mod.REQUIRED_CORRECTIONS, f'docs/downloads/{stem}.tif', correction_rel)
    card = json.loads(card_path.read_text())
    card_path.write_text(json.dumps(card))
    missing = mod.audit_artifact(*args)
    assert missing['checks']['superseding_correction_hash_bound'] is False
    assert missing['status'] == 'FAIL_CLOSED'
    correction = {
        'schema': 'gems.historical-artifact-correction.v1',
        'artifact': {
            'path': f'docs/downloads/{stem}.tif',
            'sha256_measured': measured,
            'sha256_in_current_run_card': measured,
        },
        'verdict': 'negative', 'ok_to_submit': False, 'slot_authorized': False,
    }
    correction_path = root / 'evidence/correction.json'
    correction_path.write_text(json.dumps(correction))
    card = json.loads(card_path.read_text())
    card['superseding_correction'] = 'evidence/correction.json'
    card_path.write_text(json.dumps(card))
    result = mod.audit_artifact(*args)
    assert result['checks']['superseding_correction_hash_bound'] is True
    assert result['status'] == 'VERIFIED_RESEARCH_ONLY'
    correction['artifact']['sha256_measured'] = '0' * 64
    correction_path.write_text(json.dumps(correction))
    result = mod.audit_artifact(*args)
    assert result['checks']['superseding_correction_hash_bound'] is False
    assert result['status'] == 'FAIL_CLOSED'
    card['superseding_correction'] = '../docs/outside.json'
    card_path.write_text(json.dumps(card))
    result = mod.audit_artifact(*args)
    assert result['checks']['superseding_correction_hash_bound'] is False
    assert result['status'] == 'FAIL_CLOSED'
