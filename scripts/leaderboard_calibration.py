#!/usr/bin/env python3
"""Leaderboard-score calibration for the GEMS Prize Challenge.

What this is
------------
The competition's hidden expert truth is not public.  Two things *are* public:

1. the **owner-reported leaderboard scores** of past submissions (the score
   ledger of the participant repositories, evidence class ``USER-REPORT`` --
   user-reported, not independently authenticated, and not a submission-page
   receipt);
2. the **USGS state-geologic-map fault structures** (public domain), which give
   an independent fault truth for the same 100 m grid.

The official metric is algebraically simple for a binary dot field:

    DTI = TP_w / (TP_w + alpha*FP_w + beta*FN_w),  alpha = 0.2, beta = 0.8,
    FN_w = |G| - TP_w
        = TP_w / (0.2*TP_w + 0.2*FP_w + 0.8*|G|)

so a candidate is characterised by the truth-weighted coverage it achieves and
by the size of its dot budget.  Fitting the two free parameters of

    score ~= alpha_c * TP_sgmc / (0.2 * n_dots + 0.8 * G_hidden)

to the pairs (SGMC-cal measurement, owner-reported live score) gives an
empirical estimator of the hidden-set score from public measurements.

Every number produced here is a **PROJECTION** (a fitted estimator with a
prediction interval).  It is not an organiser score, not a receipt, and it is
never written as a score.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from sgmc_cal import SgmcInstrument  # noqa: E402

REGISTRY = ROOT / ".cache" / "registry"
EVID = ROOT / "evidence" / "hunmap"
ALPHA = 0.2
BETA = 0.8


def model(params: np.ndarray, tpw: np.ndarray, n: np.ndarray) -> np.ndarray:
    a, g = params
    return a * tpw / (ALPHA * n + BETA * g + 1e-12)


def fit(tpw: np.ndarray, n: np.ndarray, y: np.ndarray) -> dict:
    from scipy.optimize import least_squares

    def resid(p):
        return model(p, tpw, n) - y

    best = None
    for g0 in (5_000.0, 10_000.0, 15_000.0, 25_000.0, 40_000.0):
        p0 = np.array([y.mean() / max(tpw.mean(), 1.0), g0])
        try:
            sol = least_squares(resid, p0, bounds=([0.0, 500.0], [5.0, 500_000.0]))
        except Exception:  # pragma: no cover - defensive
            continue
        if best is None or sol.cost < best.cost:
            best = sol
    assert best is not None
    a, g = best.x
    pred = model(best.x, tpw, n)
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return dict(alpha_scale=float(a), G_hidden_cells=float(g),
                r_squared=1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan"),
                rmse=float(math.sqrt(ss_res / len(y))))


def loo_predictions(tpw: np.ndarray, n: np.ndarray, y: np.ndarray) -> np.ndarray:
    out = np.zeros(len(y))
    for i in range(len(y)):
        m = np.ones(len(y), bool)
        m[i] = False
        f = fit(tpw[m], n[m], y[m])
        out[i] = model(np.array([f["alpha_scale"], f["G_hidden_cells"]]),
                       tpw[i:i + 1], n[i:i + 1])[0]
    return out


def find_registry_file(needle: str) -> Path | None:
    hits = sorted(REGISTRY.rglob(f"*{needle}*"))
    hits = [h for h in hits if h.suffix.lower() in {".tif", ".tiff"}]
    if not hits:
        return None
    # prefer the file whose name contains the needle most literally
    hits.sort(key=lambda p: (0 if needle in p.name else 1, len(p.name)))
    return hits[0]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pairs", required=True,
                    help="JSON file: [{site, submission, score, file_needle}, ...]")
    ap.add_argument("--candidates", default=None,
                    help="JSON file: [{label, file}, ...] to project")
    ap.add_argument("--out", default=str(EVID / "leaderboard_calibration.json"))
    args = ap.parse_args(argv)

    pairs = json.loads(Path(args.pairs).read_text())
    inst = SgmcInstrument()
    rows = []
    for p in pairs:
        path = Path(p["file"]) if p.get("file") else find_registry_file(p["file_needle"])
        if path is None or not path.exists():
            rows.append(dict(**p, error="registry file not found"))
            continue
        r = inst.score_raster(path, inst) if hasattr(inst, "score_raster") else None
        from sgmc_cal import score_raster

        r = score_raster(path, inst)
        rows.append(dict(site=p["site"], submission=p["submission"],
                         live_score_user_reported=float(p["score"]),
                         file=str(path),
                         sgmc_tpw=r["tpw"], sgmc_fpw=r["fpw"],
                         n_dots=r["n_emitted"], sgmc_dti=r["dti"]))
    ok = [r for r in rows if "error" not in r]
    tpw = np.array([r["sgmc_tpw"] for r in ok])
    n = np.array([r["n_dots"] for r in ok], float)
    y = np.array([r["live_score_user_reported"] for r in ok])
    fitres = fit(tpw, n, y)
    for r, p in zip(ok, model(np.array([fitres["alpha_scale"], fitres["G_hidden_cells"]]), tpw, n)):
        r["projected_score"] = float(p)
        r["residual"] = float(r["live_score_user_reported"] - p)
    loo = loo_predictions(tpw, n, y)
    for r, p in zip(ok, loo):
        r["projected_loo"] = float(p)

    out = dict(
        evidence_class="PROJECTION - NOT A SCORE",
        model="score ~= alpha_scale * TP_sgmc / (0.2 * n_dots + 0.8 * G_hidden)",
        alpha=ALPHA, beta=BETA,
        fit=fitres,
        loo_rmse=float(np.sqrt(np.mean((loo - y) ** 2))),
        n_points=len(ok),
        rows=rows,
        caveats=[
            "live scores are owner-reported (USER-REPORT), not organiser receipts",
            "TP_sgmc is measured on the public USGS state-geologic-map fault set; the hidden truth is a different expert mapping",
            "the estimator is fitted on published submissions; predictions for new families are extrapolations",
            "a projection is never a score and never a promotion basis",
        ],
    )

    if args.candidates:
        cands = json.loads(Path(args.candidates).read_text())
        from sgmc_cal import score_raster

        a = fitres["alpha_scale"]
        g = fitres["G_hidden_cells"]
        rng = np.random.default_rng(520810)
        draws = []
        for _ in range(2000):
            idx = rng.integers(0, len(ok), len(ok))
            f = fit(tpw[idx], n[idx], y[idx])
            draws.append((f["alpha_scale"], f["G_hidden_cells"]))
        for c in cands:
            r = score_raster(Path(c["file"]), inst)
            vals = []
            for aa, gg in draws:
                vals.append(aa * r["tpw"] / (ALPHA * r["n_emitted"] + BETA * gg))
            vals = np.array(vals)
            out.setdefault("candidates", []).append(dict(
                label=c.get("label"), file=c["file"],
                sgmc_dti=r["dti"], sgmc_tpw=r["tpw"], n_dots=r["n_emitted"],
                projected_score=float(a * r["tpw"] / (ALPHA * r["n_emitted"] + BETA * g)),
                projected_95pi=[float(np.quantile(vals, 0.025)),
                                float(np.quantile(vals, 0.975))]))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2)[:3000])
    for r in ok:
        print(f"{r['site']:>10s} {r['submission'][:52]:<52s} live={r['live_score_user_reported']:.4f} "
              f"proj={r['projected_score']:.4f} resid={r['residual']:+.4f} "
              f"tpw={r['sgmc_tpw']:.0f} n={r['n_dots']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
