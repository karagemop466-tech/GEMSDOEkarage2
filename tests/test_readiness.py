import copy
import unittest
from scripts.readiness import assess


def good():
    rows = [{'reference': 'pinned-reference', 'rank_correlation': .5, 'overlap_3px': .6}]
    return dict(lane='assigned-method', template_commit='pin',
        holdout=dict(evaluator_version='shared-v1', withheld_positives=100, dti=.2, ci95=[.1,.3]),
        baseline_holdout_dti=.19, hide_recover_protocol_verified=True,
        feature_auc={'magnetic': .7}, registry=dict(coverage_complete=True,
        snapshot_sha256='a'*64, surface=rows, final_dots=copy.deepcopy(rows)),
        validator={k: True for k in ('single_band','finite_inside','range_0_1','crs_match','shape_match','transform_match')},
        raster_sha256='b'*64, submission_name='unique-method', submission_note='Research candidate')


class GateTests(unittest.TestCase):
    def test_empty_fails(self): self.assertEqual(assess({})['verdict'], 'negative')
    def test_complete_does_not_authorize_slot(self):
        self.assertEqual(assess(good()),dict(verdict='promote', reasons=[], slot_authorized=False))
    def test_each_required_check(self):
        for k in good():
            c=good();del c[k]
            self.assertEqual(assess(c)['verdict'],'negative',k)
    def test_duplicate_both_stages(self):
        for stage in ('surface','final_dots'):
            for metric,value in [('rank_correlation',.901),('overlap_3px',.701)]:
                c=good();c['registry'][stage][0][metric]=value
                self.assertEqual(assess(c)['verdict'],'negative')
    def test_canary_nonfinite_and_leakage(self):
        for x in (float('nan'),float('inf'),.91,-.1):
            c=good();c['feature_auc']['magnetic']=x
            self.assertEqual(assess(c)['verdict'],'negative')
    def test_no_improvement(self):
        c=good();c['baseline_holdout_dti']=.2
        self.assertEqual(assess(c)['verdict'],'negative')
    def test_invalid_ci(self):
        c=good();c['holdout']['ci95']=[.3,.1]
        self.assertEqual(assess(c)['verdict'],'negative')

if __name__ == '__main__': unittest.main()
