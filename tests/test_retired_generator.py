import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def assert_generator_stops(script: str, message: str):
    before = {p.name: (p.stat().st_size, p.stat().st_mtime_ns)
              for p in (ROOT / 'docs/downloads').iterdir()}
    result = subprocess.run([sys.executable, str(ROOT / 'scripts' / script)],
                            cwd=ROOT, capture_output=True, text=True)
    after = {p.name: (p.stat().st_size, p.stat().st_mtime_ns)
             for p in (ROOT / 'docs/downloads').iterdir()}
    assert result.returncode != 0
    assert message in result.stderr
    assert before == after


def test_legacy_generator_cannot_write_a_new_file():
    assert_generator_stops('generate_submission.py', 'No TIFF generated or published')


def test_unvalidated_unique_generator_cannot_write_a_tiff():
    assert_generator_stops('generate_unique_submission.py', 'No TIFF generated: this demonstration generator is retired')


def test_h_rank_4_generator_cannot_recreate_quarantined_candidate():
    assert_generator_stops('generate_unique_submission_v2.py', 'No TIFF generated: H-Rank-4 is retired and quarantined')


def test_h_rank_4_promote_is_countermanded_and_tiff_is_quarantined():
    path = ROOT / 'evidence/quarantine/gemsdoe-karage2-hr4-intersection-20261029-nan.tif'
    correction = json.loads((ROOT / 'evidence/quarantine/gemsdoe-karage2-hr4-intersection-20261029-nan-countermand.json').read_text())
    original = json.loads((ROOT / 'evidence/quarantine/gemsdoe-karage2-hr4-intersection-20261029-nan-run-card.json').read_text())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == correction['raster_sha256'] == original['raster_sha256']
    assert not (ROOT / 'docs/downloads/gemsdoe-karage2-hr4-intersection-20261029-nan.tif').exists()
    assert correction['original_run_card_verdict'] == 'promote (RETRACTED)'
    assert correction['corrected_verdict'].startswith('negative')
    assert correction['holdout_dti'] is None and correction['holdout_ci95'] is None
    assert correction['leakage_canary'] == 'not run'
    assert correction['slot_authorized'] is False
    witness = correction['single_witness_followup']
    assert witness['status'] == 'DUPLICATE_STOP' and witness['registry_declared_complete'] is False
    assert witness['within_3px'] / witness['support_pixels'] > 0.70
    assert original['holdout']['candidate_dti'] is None
    assert original['verdict'] == 'promote'  # retained as historical evidence, not authorization
