import hashlib
import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import numpy as np
import pytest
import rasterio
from gems57 import grid, uniqueness
from gems57.gates import format_report
from gems57.submission_writer import write_submission
ROOT = Path(__file__).resolve().parents[1]


def load(name): return json.loads((ROOT/'evidence'/name).read_text(),parse_constant=lambda v:(_ for _ in ()).throw(ValueError(v)))


def test_all_committed_evidence_is_strict_json():
    for folder in (ROOT/'evidence', ROOT/'docs/evidence', ROOT/'registry'):
        for path in folder.glob('*.json'):
            json.loads(path.read_text(), parse_constant=lambda v:(_ for _ in ()).throw(ValueError(v)))


def test_run_card_has_required_keys_and_no_approval():
    c=load('run_card.json')
    for key in ('hypothesis','mechanism','non_fault_mimic','holdout','registry','raster_sha256','validator','submission_name','note','verdict'):
        assert key in c
    assert c['verdict']=='negative'
    assert c['approved_for_weekly_slot'] is False
    assert not c['unique_submission_verified']
    assert len(c['note'])<=140
    assert c['experiments_run']<=3 and c['submission_slots_used']==0
    assert c['holdout']['evidence_class']=='HOLDOUT-DTI'
    assert c['registry']['final_dot_check'].startswith('not run')


def test_download_bytes_grid_range_and_zip(tmp_path):
    c=load('run_card.json'); p=ROOT/c['raster']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==c['raster_sha256']
    with rasterio.open(p) as ds:
        a=ds.read(1)
        assert ds.count==1 and ds.shape==grid.SHAPE
        assert ds.crs.to_epsg()==32611 and ds.transform==grid.TRANSFORM
        assert ds.nodata is None
        assert np.isfinite(a).all() and a.min()>=0 and a.max()<=1
        assert (ds.dataset_mask()>0).all()
    # CI need not redownload private/large inputs: create a grid-only template,
    # not labels or hidden truth. This test certifies format, not provenance.
    sample=tmp_path/'sample.tif'
    grid.write_geotiff(sample,np.zeros(grid.SHAPE,np.float32))
    report=format_report(p,sample)
    assert report['ok'],report['problems']
    with zipfile.ZipFile(p.with_suffix('.zip')) as z:
        assert z.namelist()==[p.name]
        assert z.read(p.name)==p.read_bytes()
    receipt=json.loads(p.with_suffix('.json').read_text())
    assert receipt['sha256']==c['raster_sha256'] and not receipt['approved_for_weekly_slot']


@pytest.mark.parametrize('value',[float('nan'),float('inf'),-.001,1.001,-3.4e38])
def test_writer_rejects_invalid_values_without_silent_repair(value,tmp_path):
    a=np.zeros((3,4));a[1,2]=value
    with pytest.raises(ValueError,match='already be normalized'):
        write_submission(tmp_path/'bad.tif',a,tmp_path/'sample.tif',np.ones_like(a,bool),name='test',note='test')
    assert not list(tmp_path.iterdir())


def test_overlength_note_rejected(tmp_path):
    with pytest.raises(ValueError,match='note'):
        write_submission(tmp_path/'bad.tif',np.zeros((3,4)),tmp_path/'sample.tif',np.ones((3,4),bool),name='test',note='x'*141)


class Links(HTMLParser):
    def __init__(self): super().__init__();self.links=[];self.base=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='base':self.base=a.get('href')
        if tag in ('a','link','script'):
            if a.get('href') or a.get('src'):self.links.append(a.get('href') or a.get('src'))


def test_every_static_local_site_link_resolves():
    for page in (ROOT/'docs').rglob('*.html'):
        parser=Links();parser.feed(page.read_text())
        base=(page.parent/parser.base).resolve() if parser.base else page.parent
        for url in parser.links:
            part=urlsplit(url)
            if part.scheme or part.netloc or not part.path:continue
            assert (base/unquote(part.path)).exists(),(page,url)


def test_all_nine_site_summaries_exist_and_are_explicit():
    sources=load('sources.json')
    assert len(sources['sites'])==9
    for r in sources['sites']:
        text=(ROOT/'docs/sites'/f'{r["repo"]}.html').read_text()
        assert 'DO NOT RESUBMIT' in text and 'Not estimable' in text
        assert 'unverified' in text.lower()
        assert 'READ' in text
    homepage=(ROOT/'docs/index.html').read_text()
    # K2 crossed the literal pre-placement stop and remains quarantined; the
    # HK3 verdict on the homepage must match the HK3 run card byte-for-byte.
    assert 'prior literal-policy verdict for K2: NEGATIVE' in homepage
    assert 'DO NOT SUBMIT' in homepage
    assert 'docs/executive-summary.html' in (ROOT/'index.html').read_text()  # root redirect
    card=load('hk3/run_card.json')
    assert card['verdict']=='negative'
    # The old HALO receipt's submit flag conflicts with the literal lattice
    # overlap rule. The public homepage must fail closed until policy is resolved.
    assert 'SUBMISSION HOLD' in homepage
    assert '99.84%' in homepage and 'registered lattice witness' in homepage
    assert card['raster']['sha256'] in homepage and 'RESEARCH ONLY' in homepage



def test_shared_scientific_tools_unchanged():
    sources=load('sources.json')
    for rel,rec in sources['shared_tools'].items():
        assert rec['upstream_unchanged']
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==rec['sha256']


def test_historical_relationships_and_registry_stop_evidence():
    h=load('champion_forensics.json')
    assert h['d28_equals_site30'] and h['b2_equals_d28_distance_gt2']
    assert h['removed_d28_to_b2']==6436
    s=load('h1/surface_registry.json')
    assert s['stopped_early'] and not s['unique_cleared'] and s['checked']==len(s['rows'])
    assert any(r.get('duplicate_by_overlap') or r.get('duplicate_by_rho') for r in s['rows'])
    cert=load('saturation_certificate.json')
    assert not cert['universal_overlap_blocker']
    assert cert['uncovered_allowed_pixels']>0


def test_holdout_metadata_and_no_canary_failure():
    h=load('holdout.json')
    assert h['canary_pass'] and h['pooled']
    assert all(f['shared_train_truth_components']==0 for f in h['folds'])
    for score in h['scores'].values():
        assert score['evidence_class']=='HOLDOUT-DTI'
        assert score['evaluator_version']=='gems57-pooled-hide-v2'
        assert score['withheld_positive_pixels']==58259
        assert 0<=score['ci95'][0]<=score['dti']<=score['ci95'][1]<=1
    assert all(v['auc']<=.90 for f in h['canaries'] for v in f['features'].values())


def test_actual_footprint_and_catalogue_when_inputs_available():
    input_dir=ROOT/'.cache/gems_data'
    if not (input_dir/'sample_submission.tif').exists():
        pytest.skip('pinned mirror inputs not restored in this lightweight CI run')
    g=grid.load_grid(input_dir)
    c=load('run_card.json')
    with rasterio.open(ROOT/c['raster']) as ds:
        p=ds.read(1)
    assert not (p[g.catalogue]>0).any()
    assert not (p[~g.footprint]>0).any()
    assert np.isfinite(p[g.footprint]).all()
    assert int(g.catalogue.sum())==60988
    assert int(g.footprint.sum())==5167373


def test_browser_evidence_no_overflow_or_script_errors():
    b=load('browser_checks.json')
    assert not b['errors']
    assert not any(r.get('overflow') for r in b['rows'])
    assert any(r.get('sha256_matches') and r.get('download_http_status')==200 for r in b['rows'])
    assert {r.get('width') for r in b['rows'] if 'width' in r}=={320,390,1440}


def test_every_historical_raster_grid_was_checked():
    h=load('nine_site_best_files_audit.json')
    assert len(h['sites'])==9
    for row in h['sites']:
        assert row['template_grid_match']
        assert row['infinity_anywhere']==0
        assert row['transform']==list(grid.TRANSFORM)[:6]


def test_concurrent_selector_gate_keeps_actual_run_negative():
    import scripts.readiness as readiness
    adapted=load('h1/selector_input.json')
    result=readiness.assess(adapted)
    assert result['verdict']=='negative' and not result['slot_authorized']
    assert adapted['baseline_holdout_dti'] is None
    assert adapted['registry']['final_dots']==[]
    assert not adapted['registry']['coverage_complete']
    assert adapted['validator']['outside_nodata'] is None
    assert any('Raster validation' in r for r in result['reasons'])
    assert any('duplicate lane' in r for r in result['reasons'])
