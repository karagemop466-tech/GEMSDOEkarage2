import hashlib
import subprocess
from pathlib import Path
import pytest
import fetch_focus_registry as fetcher


def gitsha(body):
    return hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()


def test_equal_size_corrupt_cache_is_refetched(tmp_path, monkeypatch):
    destination=tmp_path/'GEMSDOE24/docs/one.tif'
    destination.parent.mkdir(parents=True);destination.write_bytes(b'bad!')
    calls=[]
    def run(args,stdout,**kwargs):
        calls.append(args);stdout.write(b'good')
    monkeypatch.setattr(subprocess,'run',run)
    # ROOT is used only to produce manifest-relative paths.
    monkeypatch.setattr(fetcher,'ROOT',tmp_path)
    result=fetcher.fetch_one('GEMSDOE24','immutable','docs/one.tif',4,gitsha(b'good'),tmp_path)
    assert calls and destination.read_bytes()==b'good'
    assert result['git_blob_sha']==gitsha(b'good')
    calls.clear()
    fetcher.fetch_one('GEMSDOE24','immutable','docs/one.tif',4,gitsha(b'good'),tmp_path)
    assert not calls


def test_wrong_blob_is_never_recorded_as_valid(tmp_path,monkeypatch):
    monkeypatch.setattr(fetcher,'ROOT',tmp_path)
    monkeypatch.setattr(fetcher.time,'sleep',lambda _:None)
    monkeypatch.setattr(subprocess,'run',lambda args,stdout,**kw:stdout.write(b'evil'))
    result=fetcher.fetch_one('GEMSDOE24','immutable','docs/one.tif',4,gitsha(b'good'),tmp_path)
    assert result['status']=='FAILED'
    assert not (tmp_path/'GEMSDOE24/docs/one.tif').exists()


def test_truncated_github_tree_fails_closed(monkeypatch):
    def fake(path):
        return {'sha':'pinned'} if '/commits/' in path else {'truncated':True,'tree':[]}
    monkeypatch.setattr(fetcher,'gh_json',fake)
    with pytest.raises(RuntimeError,match='Truncated'):
        fetcher.list_repo('GEMSDOE24')
