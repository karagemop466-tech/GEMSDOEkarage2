#!/usr/bin/env python3
"""Adapt real receipts to the concurrent session's unchanged evidence-schema gate.

This does not evaluate a model or place dots. Missing incumbent/final-dot/lane
inputs remain missing; they are never replaced by optimistic defaults.
"""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.readiness import assess

def load(name): return json.loads((ROOT/'evidence'/name).read_text())
def main():
    run, hold, registry, validator = [load(n) for n in ('run_card.json','holdout.json','surface_registry.json','validator.json')]
    report=validator['template_report']
    source=hold['scores']['candidate']
    surface_rows=[dict(reference=f"{r['repo']}/{r['submission']}",rank_correlation=r.get('spearman_full_footprint'),
                       overlap_3px=r.get('my_dots_within_3px_of_theirs')) for r in registry['rows'] if 'error' not in r]
    features={name:max(f['features'][name]['auc'] for f in hold['canaries']) for name in hold['canaries'][0]['features']}
    adapted=dict(
        lane='',  # Prompt had no actual assigned lane paragraph. Provisional H1 is not a supplied assignment.
        proposed_lane=run['hypothesis'],
        template_commit='73485f27cf230af770167397c2b72cb9ce3b3f25',
        metric=dict(alpha=.2,beta=.8,kernel_radius_m=300,kernel='triangular'),
        holdout=dict(evidence_class='HOLDOUT-DTI',evaluator_version=source['evaluator_version'],
                     withheld_positives=source['withheld_positive_pixels'],dti=source['dti'],ci95=source['ci95'],
                     paired_delta_ci95=None), # No compatible incumbent; do not substitute a primitive.
        baseline_holdout_dti=None,
        hide_recover_protocol_verified=all(f['shared_train_truth_components']==0 and f['buffer_px']==80 for f in hold['folds']),
        feature_auc=features,
        registry=dict(coverage_complete=False,
                      snapshot_sha256=hashlib.sha256((ROOT/'registry/focus_registry_manifest.json').read_bytes()).hexdigest(),
                      surface=surface_rows, final_dots=[]),
        validator=dict(single_band=report['bands']==1,finite_inside=report['nan_pixels']==0 and report['infinity_pixels']==0,
                       range_0_1=run['validator']['range'][0]>=0 and run['validator']['range'][1]<=1,
                       crs_match=report['ok'],shape_match=report['ok'],transform_match=report['ok'],
                       outside_nodata=report['ok']),
        raster_sha256=run['raster_sha256'],submission_name=run['submission_name'],submission_note=run['note'],
        note='Adapter consumes committed measured receipts; it does not authenticate their origin or reconstruct unavailable inputs.')
    result=assess(adapted)
    result.update(evidence_type='EVIDENCE-SCHEMA-ASSESSMENT, not a model score',
                  source_run_card='evidence/run_card.json',slot_authorized=False)
    if result['verdict']!='negative':
        raise ValueError('This negative stopped run must never be promoted by the adapter')
    for name,value in [('selector_input.json',adapted),('selector_result.json',result)]:
        (ROOT/'evidence'/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
