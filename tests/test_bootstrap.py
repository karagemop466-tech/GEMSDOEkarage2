import base64
import hashlib
from pathlib import Path
import pytest
import bootstrap_research as boot


def fixture_item(data: bytes):
    return {
        "repo": "example/repo", "path": "pinned/data.bin", "ref": "a" * 40,
        "bytes": len(data), "git_blob": boot.blob_digest(data),
        "sha256": hashlib.sha256(data).hexdigest(), "cache_path": "inputs/data.bin",
    }


def test_fetch_checks_all_identities_and_reuses_cache(tmp_path, monkeypatch):
    data = b"pinned research bytes"
    item = fixture_item(data)
    calls = []
    def fake_gh(endpoint):
        calls.append(endpoint)
        return {"type": "file", "sha": item["git_blob"], "size": len(data), "encoding": "base64", "content": base64.b64encode(data).decode()}
    monkeypatch.setattr(boot, "gh_json", fake_gh)
    assert boot.fetch(item, tmp_path, item["cache_path"]) == "downloaded"
    assert (tmp_path / "inputs/data.bin").read_bytes() == data
    assert boot.fetch(item, tmp_path, item["cache_path"]) == "cached"
    assert len(calls) == 1
    (tmp_path / "inputs/data.bin").write_bytes(b"tampered")
    assert boot.fetch(item, tmp_path, item["cache_path"]) == "downloaded"
    assert len(calls) == 2


def test_blob_fallback_and_size_hash_fail_closed(tmp_path, monkeypatch):
    data = b"another binary"
    item = fixture_item(data)
    responses = iter([
        {"type": "file", "sha": item["git_blob"], "size": len(data), "encoding": "none"},
        {"sha": item["git_blob"], "encoding": "base64", "content": base64.b64encode(data).decode()},
    ])
    monkeypatch.setattr(boot, "gh_json", lambda _: next(responses))
    assert boot.fetch(item, tmp_path, item["cache_path"]) == "downloaded"
    (tmp_path / "inputs/data.bin").unlink()
    monkeypatch.setattr(boot, "gh_json", lambda _: {"type": "file", "sha": "wrong", "size": len(data)})
    with pytest.raises(ValueError, match="Git blob"):
        boot.fetch(item, tmp_path, item["cache_path"])
    assert not (tmp_path / "inputs/data.bin").exists()


def test_template_without_git_blob_still_requires_sha(tmp_path, monkeypatch):
    data = b"template"
    item = fixture_item(data)
    del item["git_blob"]
    monkeypatch.setattr(boot, "gh_json", lambda _: {"type": "file", "sha": "f" * 40, "size": len(data), "encoding": "base64", "content": base64.b64encode(data).decode()})
    assert boot.fetch(item, tmp_path, item["cache_path"]) == "downloaded"
    assert (tmp_path / "inputs/data.bin").read_bytes() == data


def test_cache_paths_cannot_escape(tmp_path):
    with pytest.raises(ValueError):
        boot.safe_destination(tmp_path, "../outside")
    with pytest.raises(ValueError):
        boot.safe_destination(tmp_path, str(Path("/") / "outside"))
