import numpy as np
import pytest
from scipy import ndimage as ndi
from gems57 import metric, spatial, evaluate_holdout as evaluator
from gems57.uniqueness import dot_overlap
from run_experiment import physical_features, candidate_surface, normalized

@pytest.mark.parametrize('seed', range(8))
def test_metric_matches_bruteforce(seed):
    rng = np.random.default_rng(seed)
    p = rng.random((9, 11)) * (rng.random((9, 11)) < .2)
    truth = rng.random((9, 11)) < .08
    a, b = metric.dti_exact(p, truth), metric.dti_bruteforce(p, truth)
    for k in ('tp', 'fp', 'fn', 'dti'):
        assert a[k] == pytest.approx(b[k], abs=1e-10)


def test_triangular_boundary_and_empty_truth():
    assert metric.kernel([0, 1.5, 3, 4]).tolist() == [1, .5, 0, 0]
    assert metric.dti_exact(np.zeros((7,7)), np.zeros((7,7),bool))['dti'] == 0
    assert metric.dti_exact(np.ones((7,7)), np.zeros((7,7),bool))['fp'] == 49


def test_known_pixels_masked_exactly_not_as_buffer():
    p = np.zeros((9,9)); truth=np.zeros((9,9),bool); known=np.zeros((9,9),bool)
    p[4,4] = p[4,5] = 1; truth[4,5]=True; known[4,4]=True
    result=metric.dti_exact(p,truth,known=known)
    assert result['dti']==pytest.approx(1)
    assert result['n_emitted']==1


def test_holdout_keeps_whole_components_out_of_training():
    cat=np.zeros((100,100),bool); cat[10:90,25]=True; cat[70:90,70]=True
    eligible=np.ones_like(cat)
    folds=list(spatial.folds(cat,eligible,buffer_px=5))
    assert sum(f['truth'].sum() for f in folds) == cat.sum()
    for f in folds:
        assert not (f['train'] & f['held_all']).any()
        assert not (f['visible'] & f['held_all']).any()
        assert f['receipt']['shared_train_truth_components']==0
        if f['train'].any():
            assert ndi.distance_transform_edt(~(f['region']|f['held_all']))[f['train']].min()>5
        # Moving truth cannot alter the predeclared evaluation quadrant.
        assert np.array_equal(f['region'], list(spatial.folds(np.zeros_like(cat),eligible,buffer_px=5))[f['fold']]['region'])


def test_pooled_terms_and_truth_count_guard():
    terms=np.array([[1,2,3,4],[2,1,2,4]],float)
    result=evaluator.pooled_summary({'candidate':terms,'control':terms.copy()},draws=100,candidate='candidate')
    s=result['scores']['candidate']
    assert s['dti']==pytest.approx(3/(3+.2*3+.8*5))
    assert s['withheld_positive_pixels']==8
    assert result['paired_differences']['control']['delta']==0
    wrong=terms.copy();wrong[0,3]+=1
    with pytest.raises(ValueError,match='same integer truth count'):
        evaluator.pooled_summary({'candidate':terms,'control':wrong},candidate='candidate')


def test_directional_overlap_uses_inclusive_three_pixels():
    mine=np.zeros((15,15));other=np.zeros_like(mine)
    mine[5,5]=1;other[5,8]=1
    assert dot_overlap(mine,other)==1
    other[5,8]=0;other[5,9]=1
    assert dot_overlap(mine,other)==0


def test_opposition_is_physical_not_label_driven():
    y,x=np.mgrid[:50,:50]; valid=np.ones((50,50),bool)
    fields=physical_features(np.stack([x,-x,y]).astype(np.float32),valid)
    same=physical_features(np.stack([x,x,y]).astype(np.float32),valid)
    assert np.all(fields['opposition_s2'][10:40,10:40]>.99)
    assert np.all(same['opposition_s2'][10:40,10:40]==0)
    out=candidate_surface(normalized(fields,valid))
    assert np.isfinite(out).all() and out.min()>=0 and out.max()<=1
    assert out.max()>0


def test_exact_pruning_improvement_condition():
    rng=np.random.default_rng(1946)
    for _ in range(30):
        p=(rng.random((10,10))<.22).astype(float)
        truth=rng.random((10,10))<.1
        pruned=p*(rng.random((10,10))>.3)
        before,after=metric.dti_exact(p,truth),metric.dti_exact(pruned,truth)
        dt,df=before['tp']-after['tp'],before['fp']-after['fp']
        den=before['tp']+.2*before['fp']+.8*before['fn']
        margin=.2*before['tp']*(dt+df)-den*dt
        if abs(margin)>1e-9:
            assert (after['dti']>before['dti']) == (margin>0)


def test_gems57_h1_evaluator_preserves_fractional_predictions():
    # The upstream GEMSDOE32 top-level CLI is binary-only; this is the
    # distinct shared evaluator used by H1, not an H1 holdout rerun.
    p = np.zeros((9, 9), float)
    p[4, 4] = .25
    truth = np.zeros((9, 9), bool)
    truth[4, 4] = True
    fold = {'region': np.ones_like(truth), 'visible': np.zeros_like(truth), 'truth': truth}
    result, terms = evaluator.evaluate(p, fold, np.ones_like(truth), block_side=4)
    assert result['tpw'] == pytest.approx(.25)
    assert result['fnw'] == pytest.approx(.75)
    assert result['dti'] == pytest.approx(.25 / (.25 + .8 * .75))
    assert terms[:, 0].sum() == pytest.approx(.25)
