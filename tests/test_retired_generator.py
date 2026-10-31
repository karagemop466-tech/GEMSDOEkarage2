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


def assert_imported_main_stops(module: str, message: str):
    before = {p.name: (p.stat().st_size, p.stat().st_mtime_ns)
              for p in (ROOT / 'docs/downloads').iterdir()}
    code = (f"import sys; sys.path.insert(0, {str(ROOT / 'scripts')!r}); "
            f"import {module}; {module}.main()")
    result = subprocess.run([sys.executable, '-c', code],
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


def test_unvalidated_hr4_placeholder_cannot_write_a_tiff():
    assert_generator_stops('generate_unique_submission_v2.py', 'No TIFF generated: this H-Rank-4 placeholder is retired')


def test_hf_prototype_cannot_regenerate_its_invalid_artifact():
    assert_generator_stops('generate_hypothesis_submission.py', 'H-F prototype is retired')


def test_unverified_hg_prototype_cannot_claim_or_write_an_experiment():
    assert_generator_stops('generate_hypothesis_submission_hg.py', 'H-G has no verified run')


def test_imported_hf_main_is_blocked_without_writing():
    assert_imported_main_stops('generate_hypothesis_submission', 'H-F prototype is retired')


def test_imported_hg_main_is_blocked_without_writing():
    assert_imported_main_stops('generate_hypothesis_submission_hg', 'H-G has no verified run')
