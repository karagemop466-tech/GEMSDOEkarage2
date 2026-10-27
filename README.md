# GEMSDOEkarage2

**Start every session here. No approved competition TIFF exists.**

Read [the project brief](knowledge/project-brief.md), [review and next steps](knowledge/review.md), and [run card](docs/data/run-card.json) before changing models. The site is in `docs/`; the executive dashboard links nine local per-site summaries and a submission guide.

## Operating contract from the user request
Generate scientifically distinct fault-prediction GeoTIFFs, never renamed copies. Prioritize GEMSDOE24/25/27/28/30/31/32/33/36. Show file, estimated performance evidence and uniqueness clearly. Use the assigned method lane and the common cached stack, `evaluate_holdout.py`, and `submission_writer.py`; never private forks. Whole fault segments must be hidden with buffers and catalogue features rebuilt from visible faults only. Use pooled DTI with alpha 0.2, beta 0.8 and a 300 m triangular kernel. Mask visible faults pixel-exactly. Run per-feature leakage canaries; AUC above 0.90 blocks trust. Stop if rank correlation exceeds 0.90 or more than 70% of dots lie within 3 pixels of a registry raster, at surface and final-dot stages. Budget: at most three experiments or two hours. Promotion and weekly-slot selection are separate. End every run with a JSON card and deliver negative results too.

Only label verified evaluator results HOLDOUT-DTI (version, positives, confidence interval); only submission-page receipts establish ORGANIZER-CONFIRMED results. Historical user claims are quarantined as USER-REPORTED. Never invent score estimates. Validate single band, no NaN inside footprint, [0,1] values and exact template CRS/shape/transform. No manual inspection bypass. Preserve auditable official sources; report inaccessible sources and incomplete work honestly.

Maximize P(Win): prefer reliable evidence over optimistic claims. Own the Outcome: automate checks, expose blockers, and preserve failed experiments.

## Current limitations
The starting repository had only its name. The prompt specifies no actual lane paragraph or template repository/commit. No experiments were run and no TIFF was fabricated. Read the research page for the three-pass audit and candidate hypotheses. The complete verbatim user message is not available as a workspace attachment; the brief preserves its actionable requirements rather than claiming a verbatim archive.

## Run checks and preview
```sh
python -m unittest discover -s tests -v
python -m http.server 8000 --bind 0.0.0.0 --directory docs
```

`readiness.assess` is a fail-closed evidence-schema gate, not a scientific evaluator or raster writer. Integrate shared tools only after their identity is established. GitHub Actions tests the gate and publishes `docs/` via Pages when enabled in repository settings.
