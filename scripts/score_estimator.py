#!/usr/bin/env python3
"""Score estimator for DOE GEMS submissions: forward metric algebra + registry prior.

Two independent estimates, deliberately kept apart.

1. ``forward_dti`` -- exact arithmetic on the organizer metric
   ``DTI = T / (alpha*T + alpha*F + beta*G)`` with alpha 0.2, beta 0.8,
   F = n - M.  Given (n dots, truth credit T, dot-hit mass M, hidden truth size G)
   the value is *computed*, not extrapolated.  ``G`` is calibrated from the public
   13GEMSDOE r13 lattice submission (score 0.0904) by
   ``scripts/calibrate_leaderboard.py``: G ~ 12,406 px (interval 12,397-12,414).

2. ``registry_prior`` -- an empirical posterior over *what a new independent
   submission of a given budget class actually scores*, fitted to the
   USER-REPORTED leaderboard values of methodologically independent submissions
   named in the project prompt.  This is a prior, not a measurement of our file.

Nothing here writes a "score".  Every number carries the label
``LEADERBOARD-CALIBRATED ESTIMATE`` or ``EMPIRICAL REGISTRY PRIOR``.

Usage
-----
    python scripts/score_estimator.py --dots 38000 --hit-rate 0.0276
    python scripts/score_estimator.py --table
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALPHA, BETA = 0.2, 0.8

# G calibrated by scripts/calibrate_leaderboard.py from the r13 lattice submission.
G_POINT = 12405.768
G_INTERVAL = (12397.144, 12414.394)
# Credit delivered to hidden-truth cells per unit of dot-hit mass (B2 operating point:
# T = 5073.29 with M = 1038.49 -> 4.885).  Measured, not assumed.
CREDIT_PER_HIT = 5073.287555555577 / 1038.48891571688

# USER-REPORTED / UNVERIFIED leaderboard values of methodologically independent
# submissions (project prompt).  Values are 4-decimal leaderboard readouts.
INDEPENDENT = {
    "GEMSDOE82-h82-submodular-punoisyor": 0.1886,
    "GEMSDOE27-h29-hydrothermal-piedmont-celf": 0.2190,
    "GEMSDOE48-h59-cover-ds-belief-b2xh33d": 0.2296,
    "GEMSDOE63-cvarlw-thin-s3p17-54864": 0.2303,
    "GEMSDOE76-ptcf-tiltworm-submod39k": 0.2343,
    "GEMSDOE49-gate_ortho_w0.25-40k": 0.2376,
    "GEMSDOE70-p5-dual-submod300-oof38k": 0.2478,
}
# Nested "dotted family" members (same lineage; informative only as a lineage, not
# as independent draws).
DOTTED_FAMILY = {
    "GEMSDOE24-h25-1-dotted-h19-5-d1-5": 0.2477,
    "GEMSDOE25-dotted-h19-5-d2-8": 0.2600,
    "GEMSDOE30-d28-poisson300m-offcat": 0.2600,
    "GEMSDOE27-topo-gap-closure-t-v2-d1-5": 0.2449,
    "GEMSDOE28-h36-1-rung30-blind-r1": 0.2710,
    "GEMSDOE31-h27-4-solo-d28": 0.2708,
    "GEMSDOE32-h33-h33-2-b2": 0.2778,
    "GEMSDOE33-h33d-analog-tip-stepover": 0.2632,
    "GEMSDOE36-anderson-geothermal-pinn": 0.2750,
}


def forward_dti(n: float, T: float, M: float, G: float = G_POINT,
                alpha: float = ALPHA, beta: float = BETA) -> float:
    """Exact organizer metric for a binary dot field.

    ``T`` = truth credit (sum over truth cells of the best kernel weight),
    ``M`` = dot-hit mass (sum over dots of the best kernel weight),
    ``F`` = n - M, ``G`` = number of scored hidden-truth pixels.
    """
    T = min(float(T), float(G))          # T cannot exceed one credit per truth cell
    F = max(float(n) - float(M), 0.0)
    denom = alpha * T + alpha * F + beta * G
    return float(T / denom) if denom > 0 else 0.0


def model_state(n: float, hit_rate: float, credit_per_hit: float = CREDIT_PER_HIT,
                kernel_credit: float = 0.75, G: float = G_POINT) -> tuple[float, float]:
    """(T, M) for ``n`` dots with hit probability ``hit_rate``.

    A hit dot delivers ``credit_per_hit`` truth credit on average and carries
    ``kernel_credit`` self-credit; a miss carries none.  T is capped at G.
    """
    M = n * hit_rate * kernel_credit
    T = min(G, n * hit_rate * credit_per_hit)
    return T, M


def required_hit_rate(target: float, n: float, G: float = G_POINT) -> float | None:
    """Hit rate needed to reach ``target`` at budget ``n`` (None if unreachable)."""
    lo, hi = 1e-6, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        T, M = model_state(n, mid, G=G)
        if forward_dti(n, T, M, G) < target:
            lo = mid
        else:
            hi = mid
    T, M = model_state(n, hi, G=G)
    val = forward_dti(n, T, M, G)
    return hi if val >= target - 1e-9 else None


def optimal_budget(hit_rate: float, G: float = G_POINT, hi: float = 600_000) -> dict:
    """Budget maximising the exact metric under a fixed hit rate."""
    best = (0.0, 0.0)
    for n in range(1_000, int(hi) + 1, 1_000):
        T, M = model_state(n, hit_rate, G=G)
        v = forward_dti(n, T, M, G)
        if v > best[0]:
            best = (v, float(n))
    return {"hit_rate": hit_rate, "optimal_dots": best[1], "dti_at_optimum": round(best[0], 4)}


def registry_prior() -> dict:
    import statistics
    v = sorted(INDEPENDENT.values())
    mean = statistics.fmean(v)
    sd = statistics.stdev(v)
    return {"evidence_class": "EMPIRICAL REGISTRY PRIOR (USER-REPORTED leaderboard values)",
            "n": len(v), "values": v, "mean": round(mean, 4), "sd": round(sd, 4),
            "min": v[0], "max": v[-1],
            "p10": round(v[0], 4), "p90": round(v[-1], 4),
            "interpretation": ("A new submission built by a methodologically independent "
                               "pipeline and submitted at the 38k-dot budget class lands "
                               "here with high probability. It is a prior over submissions, "
                               "not a measurement of any specific file.")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dots", type=float, default=38000)
    ap.add_argument("--hit-rate", type=float, default=0.0276)
    ap.add_argument("--table", action="store_true")
    ap.add_argument("--json", type=Path, default=None)
    a = ap.parse_args(argv)

    if a.table:
        rows = []
        for hr in (0.010, 0.017, 0.0276, 0.040, 0.060, 0.080):
            opt = optimal_budget(hr)
            rows.append({"hit_rate": hr, "dti_at_38000": round(
                forward_dti(38000, *model_state(38000, hr)), 4),
                "optimal_dots": opt["optimal_dots"],
                "dti_at_optimum": opt["dti_at_optimum"]})
        need = {str(t): required_hit_rate(t, 38000) for t in (0.2778, 0.3195, 0.4413, 0.4544)}
        out = {"alpha": ALPHA, "beta": BETA, "G_point": G_POINT, "G_interval": G_INTERVAL,
               "credit_per_hit": round(CREDIT_PER_HIT, 4),
               "evidence_class": "LEADERBOARD-CALIBRATED ESTIMATE (exact metric algebra)",
               "hit_rate_table": rows,
               "hit_rate_required_at_38000_dots": {k: (round(v, 4) if v else None)
                                                   for k, v in need.items()},
               "registry_prior": registry_prior()}
        print(json.dumps(out, indent=1))
        if a.json:
            a.json.write_text(json.dumps(out, indent=1))
        return 0

    T, M = model_state(a.dots, a.hit_rate)
    print(json.dumps({
        "dots": a.dots, "hit_rate": a.hit_rate,
        "T": round(T, 1), "M": round(M, 1), "F": round(a.dots - M, 1),
        "estimated_dti": round(forward_dti(a.dots, T, M), 4),
        "evidence_class": "LEADERBOARD-CALIBRATED ESTIMATE (assumption: hit rate)",
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
