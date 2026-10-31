"""DTI-optimal emission: turn a calibrated fault-probability field into dots.

Theory (derived 2026-10-31, verified against vendor/gems57/metric.py)
---------------------------------------------------------------------
With a binary dot field S, a truth set G (|G| = K) and the official metric

    TPw = sum_{g in G} max_{x in S} k(d(x,g))            (call it A)
    FPw = sum_{x in S} [1 - max_{g in G} k(d(x,g))]      (call it F)
    FNw = K - A
    DTI = A / (A + 0.2 F + 0.8 (K - A))

one extra dot at x changes A by dA (its *marginal* truth credit: only the truth
pixels for which it beats the credit already banked) and F by dF = 1 - q(x),
where q(x) = E[max_g k(d(x,g))].  Differentiating,

    dDTI > 0  <=>  dA * (1 - 0.2*DTI) > 0.2*DTI * dF
              <=>  dA > [0.2 DTI / (1 - 0.2 DTI)] * (1 - q(x))          (*)

Two consequences used below.

1.  Because A and F are both *linear* in the emitted value p(x) (the max is
    already resolved), a dot that is emitted should be emitted at p = 1:
    scaling p down scales dA and the credit by the same factor, so the ratio
    test (*) is unchanged while the absolute contribution shrinks.  Sub-unit
    soft values are only useful as a hedge, never as an optimum.

2.  The bar is *low*: at DTI = 0.28 it is 0.0588*(1-q).  So the winning move is
    not "be conservative", it is "cover more of the probability mass, but never
    twice" -- the second dot inside one kernel disk is almost pure false
    positive.  That is a submodular covering problem, solved greedily below.

Because the truth is hidden, the expectation is taken against a *modelled*
field pi(x) = P(pixel x is a hidden-truth pixel), giving

    A(S)  = sum_g pi(g) * max_{x in S} k(d(x,g))
    F(S)  = sum_{x in S} (1 - min(1, h(x))),   h(x) = sum_g pi(g) k(d(x,g))
    K     = sum_g pi(g)

and the greedy maximises the *expected* DTI A/(A + 0.2F + 0.8(K-A)).  K enters
only through the bar, so the emitted set is robust to how many hidden faults
there really are; only the reported expectation depends on it.
"""
from __future__ import annotations

import heapq
import numpy as np

ALPHA, BETA = 0.2, 0.8
R_PX = 3.0


def disk_offsets(radius: float = R_PX):
    r = int(np.ceil(radius))
    ys, xs = np.mgrid[-r:r + 1, -r:r + 1]
    d = np.hypot(ys, xs)
    m = (d < radius) & (d >= 0)
    m &= (d <= radius)
    m = d < radius            # k(d) = max(1 - d/R, 0); zero at exactly R
    return ys[m], xs[m], (1.0 - d[m] / radius)


OFF_Y, OFF_X, OFF_K = disk_offsets()
NOFF = len(OFF_K)


def _shifted_view(a, dy, dx):
    """Return the array a shifted so that out[y,x] = a[y+dy, x+dx], 0 outside."""
    H, W = a.shape
    out = np.zeros_like(a)
    y0, y1 = max(0, -dy), min(H, H - dy)
    x0, x1 = max(0, -dx), min(W, W - dx)
    if y0 >= y1 or x0 >= x1:
        return out
    out[y0:y1, x0:x1] = a[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    return out


def kernel_smooth(pi: np.ndarray) -> np.ndarray:
    """h(x) = sum_g pi(g) k(d(x,g)) -- expected kernel credit of a dot at x."""
    out = np.zeros_like(pi, dtype=np.float64)
    for dy, dx, k in zip(OFF_Y, OFF_X, OFF_K):
        out += k * _shifted_view(pi, dy, dx)
    return out


def expected_dti(pi: np.ndarray, dots: np.ndarray) -> dict:
    """Exact expected-DTI components of a binary dot set under the model pi."""
    A = 0.0
    cov = np.zeros_like(pi, dtype=np.float64)
    for dy, dx, k in zip(OFF_Y, OFF_X, OFF_K):
        np.maximum(cov, k * _shifted_view(dots.astype(np.float64), dy, dx), out=cov)
    A = float((pi * cov).sum())
    h = kernel_smooth(pi)
    q = np.minimum(1.0, h)
    F = float(np.sum(dots * (1.0 - q)))
    K = float(pi.sum())
    denom = A + ALPHA * F + BETA * (K - A)
    return dict(A=A, F=F, K=K, DTI=(A / denom if denom > 0 else 0.0),
                n=int(dots.sum()), coverage=(A / K if K > 0 else 0.0))


def _smooth_sum(pi: np.ndarray) -> np.ndarray:
    """h(x) = sum_g pi(g) k(d(x,g)), accumulated in place without big temporaries."""
    out = np.zeros(pi.shape, dtype=np.float64)
    H, W = pi.shape
    for dy, dx, k in zip(OFF_Y, OFF_X, OFF_K):
        y0, y1 = max(0, -dy), min(H, H - dy)
        x0, x1 = max(0, -dx), min(W, W - dx)
        if y0 >= y1 or x0 >= x1:
            continue
        out[y0:y1, x0:x1] += k * pi[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
    return out


def _cover_max(dots: np.ndarray) -> np.ndarray:
    """cov[g] = max_{x in dots} k(d(x,g))."""
    cov = np.zeros(dots.shape, dtype=np.float64)
    H, W = dots.shape
    d = dots.astype(np.float64)
    for dy, dx, k in zip(OFF_Y, OFF_X, OFF_K):
        y0, y1 = max(0, -dy), min(H, H - dy)
        x0, x1 = max(0, -dx), min(W, W - dx)
        if y0 >= y1 or x0 >= x1:
            continue
        np.maximum(cov[y0:y1, x0:x1], k * d[y0 + dy:y1 + dy, x0 + dx:x1 + dx],
                   out=cov[y0:y1, x0:x1])
    return cov


kernel_smooth = _smooth_sum


def expected_dti(pi: np.ndarray, dots: np.ndarray) -> dict:
    """Exact expected-DTI components of a binary dot set under the model pi."""
    pi = np.asarray(pi, dtype=np.float64)
    dots = np.asarray(dots, bool)
    cov = _cover_max(dots)
    A = float((pi * cov).sum())
    q = np.minimum(1.0, _smooth_sum(pi))
    F = float((dots * (1.0 - q)).sum())
    K = float(pi.sum())
    denom = A + ALPHA * F + BETA * (K - A)
    return dict(A=A, F=F, K=K, DTI=(A / denom if denom > 0 else 0.0),
                n=int(dots.sum()), coverage=(A / K if K > 0 else 0.0))


def greedy_emit(pi: np.ndarray, allowed: np.ndarray, max_dots: int = 250_000,
                candidate_top: int = 400_000, min_gain: float = 0.0,
                verbose_every: int = 0) -> tuple[np.ndarray, dict]:
    """Lazy-greedy (CELF) selection of dots maximising the expected DTI.

    ``pi``        modelled probability that a pixel is a hidden-truth pixel.
    ``allowed``   boolean mask of pixels where a dot may be placed.
    Returns (dots, diagnostics).
    """
    pi = np.asarray(pi, dtype=np.float64)
    allowed = np.asarray(allowed, bool)
    H, W = pi.shape
    q = np.minimum(1.0, _smooth_sum(pi))
    h = _smooth_sum(pi)
    cov = np.zeros((H, W), dtype=np.float64)
    A = 0.0
    F = 0.0
    K = float(pi.sum())
    chosen: list[int] = []
    trace: list[dict] = []

    flat_allowed = allowed.reshape(-1)
    cand = np.flatnonzero(flat_allowed)
    hflat = h.reshape(-1)
    if candidate_top and cand.size > candidate_top:
        keep = np.argpartition(-hflat[cand], candidate_top - 1)[:candidate_top]
        cand = cand[keep]
    cand = cand[np.argsort(-hflat[cand], kind="stable")].astype(np.int64)

    pi_f = pi.reshape(-1)
    q_f = q.reshape(-1)
    cov_f = cov.reshape(-1)
    offs = [(int(dy) * W + int(dx), float(k)) for dy, dx, k in zip(OFF_Y, OFF_X, OFF_K)]

    def dti_of(a: float, f: float) -> float:
        den = a + ALPHA * f + BETA * (K - a)
        return a / den if den > 0 else 0.0

    def marginal(fi: int) -> tuple[float, float]:
        y, x = divmod(fi, W)
        dA = 0.0
        if y < 2 or y >= H - 2 or x < 2 or x >= W - 2:
            for off, k in offs:
                g = fi + off
                if 0 <= g < pi_f.size:
                    p = pi_f[g]
                    if p > 0.0:
                        c = cov_f[g]
                        if k > c:
                            dA += p * (k - c)
        else:
            for off, k in offs:
                g = fi + off
                p = pi_f[g]
                if p > 0.0:
                    c = cov_f[g]
                    if k > c:
                        dA += p * (k - c)
        return dA, 1.0 - q_f[fi]

    heap = []
    ha = hflat[cand]
    qa = q_f[cand]
    for fi, hi, qi in zip(cand.tolist(), ha.tolist(), qa.tolist()):
        heap.append((-dti_of(hi, 1.0 - qi), fi))
    heapq.heapify(heap)

    n_sel = 0
    while heap and n_sel < max_dots:
        negv, fi = heapq.heappop(heap)
        dA, dF = marginal(fi)
        new = dti_of(A + dA, F + dF)
        if heap and -heap[0][0] >= new + 1e-12:
            heapq.heappush(heap, (-new, fi))
            continue
        cur = dti_of(A, F)
        if new <= cur + min_gain:
            break
        # commit: update coverage first, remembering the credit actually banked
        for off, k in offs:
            g = fi + off
            if 0 <= g < cov_f.size and k > cov_f[g]:
                cov_f[g] = k
        A += dA
        F += dF
        chosen.append(fi)
        n_sel += 1
        if verbose_every and n_sel % verbose_every == 0:
            trace.append(dict(n=n_sel, dti=dti_of(A, F)))

    dots = np.zeros(pi.size, dtype=bool)
    if chosen:
        dots[np.asarray(chosen, dtype=np.int64)] = True
    dots = dots.reshape(pi.shape)
    return dots, dict(n_dots=int(dots.sum()), expected_dti=dti_of(A, F), A=A, F=F, K=K,
                      coverage=(A / K if K else 0.0), candidates=int(cand.size),
                      heap_left=len(heap), trace=trace)
