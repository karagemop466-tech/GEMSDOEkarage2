import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_format


@pytest.mark.parametrize('shared,strict,expected', [(True, True, 0), (True, False, 1), (False, True, 1)])
def test_local_range_diagnostic_never_authorizes(monkeypatch, tmp_path, shared, strict, expected):
    result = {'format_valid': shared, 'checks': {'variant_strict_whole_array_no_nan_allowed': {'pass': strict}}}
    monkeypatch.setattr(check_format, 'checked_import', lambda cache: lambda raster, template: result)
    out = tmp_path/'receipt.json'
    monkeypatch.setattr(sys, 'argv', ['check_format.py', str(tmp_path/'test.tif'), '--output', str(out)])
    assert check_format.main() == expected
    receipt = json.loads(out.read_text())
    assert receipt['strict_whole_array_range_pass'] == strict
    assert receipt['submission_authorized'] is False
    assert receipt['organizer_accepted'] is None
