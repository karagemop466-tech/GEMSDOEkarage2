# K2 release correction — three-pass review

## Pass 1: evidence and saved raster

Read the repository instructions, prior experiment and site audits. The prompt
refers to a single assigned method paragraph, but does not identify one. The
prior K2 session self-assigned a lane and reported three experiments. No new
experiments or submission slots were used in this review.

The saved K2 raster was independently read back: one float32 band, finite
values in [0,1] everywhere, EPSG:32611 and the shape/transform recorded for the
owner mirror. Its SHA-256 matches the prior card. This does not verify the
mirror against an organizer template or prove acceptance. The historical strict
validator's `outside_is_nan` check failed. Both checks and their provenance are
in the [current review card](../evidence/k2-review-2026-10-28.json).

Archived HOLDOUT-DTI: 0.1581, 95% CI [0.1424, 0.1742],
`gems57-pooled-hide-v2`, 58,258 withheld positives. It was not independently
replayed in this review. Its CI is conditional on the original holdout, not a
private leaderboard interval. A primitive control was beaten, but no frozen,
leakage-safe current-best incumbent was established on the same folds. The
historical transfer projection is not a calibrated leaderboard estimate.

## Pass 2: protocol and implementation

The K2 final routine calculated a positive-surface-support overlap of 1.0 against
a lattice reference before emitting dots, but did not enforce a stop. That is a
continuous-surface support diagnostic, not a dot set; under the repo's own
literal pre-placement interpretation it exceeds the limit. The final archived
audit also reports 1.0 overlap, three duplicate records, one invalid grid, and
an incomplete inventory. Restricting the check to submission paths cannot make
the literal registry pass. We retired the K2 final export routine rather than
create another raster, retained the prior data and marked its conditional
promotion as superseded. The lattice constrains many placements severely; the
counting bound does not prove that *every* possible smaller file must fail.

The readiness adapter had used only the maximum raw AUC over folds. An inverted
feature can hide leakage (e.g. AUC 0.05 has reversed AUC 0.95). The adapter now
uses max(AUC, 1−AUC) per fold, and the schema gate rejects either extreme. This
is a local evidence-schema fix, not a change or fork of the shared evaluator.

## Pass 3: user-facing reconciliation and limitations

The homepage, executive summary and submission guide now consistently identify
K2 as a research-only download, with the strict check and unknown portal status.
Historical cards are preserved with a prominent correction in the K2 review;
they are not proof of a valid release. The nine-site scorecard remains explicitly
user-reported, not file-bound organizer receipts. GEMSDOE32's prune-only mask
relationship is measured in the previous mirror audit; better balance of
marginal coverage versus false-positive mass is plausible, not a proven causal
explanation of the reported score. It is unknown whether another file can beat it.

The organizer reference repository's README was reachable on GitHub and says to
place challenge data in `data/`; it also provides a CPU option. Pinned reference:
[official reference README at aebe92f7](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md).
Current organizer pages, the official data page, the PDF, authenticated samples,
private results and weekly quota cannot be checked through this environment's
network allowlist. Links for review: [problem](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/),
[leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/),
[rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), and
[USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and).
Those pages were not independently re-fetched in this review.

Next: establish the actual lane and literal registry scope without exclusions;
restore an authenticated organizer sample, check exterior guidance, and establish
complete pinned registry coverage. Freeze and evaluate the current best on the
same fold-safe holdout before a new preregistered run. Keep slot selection separate.
The existing research ideas and data-access caveats remain in
[the preregistration](hypotheses-2026-10-28-preregistration.md); none is claimed
newly tested or validated here.
