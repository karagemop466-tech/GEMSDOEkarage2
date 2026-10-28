# Starting point for future work

Read `README.md`, `research/review.md`, `research/hypotheses.md`,
`knowledge/hypotheses.md`, `evidence/h1/run_card.json` (H1),
`evidence/run_card.json` (H1 restored root), `evidence/run_card_h2.json` (H2),
and the audit-session
`docs/data/run-card.json`, `docs/data/audit-run-card.json` and
`research/independent-review.md` before changing scientific or submission workflows.
The standing protocol in the README is binding. H1's verdict is negative;
its format-checked research surface is not an approved submission. The follow-on
independent audit ran zero additional experiments. Preserve negative evidence
and source-access limits. Do not invent an assigned method lane, exempt registry
entries, hide unavailable evidence, privately modify shared evaluators/writers,
or spend a competition slot. Do not place dots or tune H1 after its registry
stop. Read the three-pass reviews; remain on the Arena-assigned branch.

Read `research/findings-2026-10-27.md`, `research/hypotheses-2026-10-27.md`,
and the independent follow-on `evidence/run-card.json` for the additional
lattice, shared-stack, prior-art and upstream-tool review. Its static companion
is `docs/field-notes/`; it does not replace or approve the parallel H1 surface.
Automated source refresh must contact GitHub only, never DrivenData. The dated
leaderboard snapshot is not a live score or a file-bound organizer receipt.

## 2026-10-28 K2 protocol correction

Read `research/k2-protocol-review-2026-10-28.md` and its JSON run card. K2 is
negative: the literal pre-placement registry stop was crossed, so its file is
research-only and must not be submitted. Preserve historical measurements; do
not regenerate K2 or infer a lane assignment, registry exemption, portal
acceptance, or current leaderboard score. The prompt supplies no identifiable
method paragraph, and the previous session exhausted its three-experiment budget.

## 2026-10-28 HK3 strict disposition — current state (read this first)

Read `README.md` ("Current status"), `research/strict-protocol-review-2026-10-28.md`,
`evidence/hk3/strict_disposition.json`, and `evidence/hk3/strict_selector_result.json` before
changing anything. **No TIFF is approved for submission.** The old
`evidence/hk3/run_card.json` (`PROMOTE`) and `evidence/hk3/selector_result.json` remain
unchanged historical evidence only; the strict negative disposition controls current release.
The HK3 file is research-only and no slot was spent.

* The four desk pages (`docs/index.html`, `executive-summary.html`, `how-to-submit.html`,
  `submit.html`) and `docs/assets/hk3.css` are **generated** by
  `scripts/build_hk3_pages.py`; CI runs `build_hk3_pages.py --check`. Change the evidence or
  generator, never generated HTML.
* The prior HK3 run used three experiments and records about 2 h 15 min. Do not run another
  experiment in that lane. No coordinator-assigned next lane is documented; research slates are
  proposals, not authorization.
* Apply the literal rule to **every** registry raster. A rank correlation >0.90 or >70% of
  final dots within 3 px of any single raster is a stop. Do not exempt unsubmitted, dense, or
  “degenerate” witnesses. HK3 has 99.8626% overlap with the r13 lattice; the scan is also
  incomplete (452/453), and no pre-placement surface audit was saved.
* The saved HK3 TIFF writes zeros outside the bounds; the official problem page specifies
  null/NaN there and the strict local receipt fails `outside_is_nan`. Do not claim that the
  whole-array [0,1] check proves portal acceptance or resolves the prior range error.
* Keep the historical positive card intact. New current release decisions must use
  `strict_disposition.json` and `strict_selector_result.json`; `scripts/audit_public_downloads.py`
  must remain fail-closed with zero upload candidates.
* Preserve negative evidence. Do not privately modify shared evaluators/writers, regenerate the
  blocked HK3 candidate, select lattice holes to evade the rule, or spend a competition slot.
* Legacy files (K2, H1, H-KARAGE-1) remain research-only; `scripts/k2.py` and
  `scripts/generate_submission.py` stay disabled.

## Notes from concurrent 2026-10-28 branches (merged)

## 2026-10-28 K3 result

Read `research/review-2026-10-28-k3.md`, `research/hypotheses-2026-10-28-k3-preregistration.md`
and `evidence/k3/run_card.json`. K3 is holdout-best but NEGATIVE: HOLDOUT-DTI
0.19157 (+0.03402 vs the replicated K2 incumbent, paired CI > 0), yet final
dots exceed 70% within-3-px overlap vs 10 registry records including fleet
submissions, and the surface gate failed vs the quarantined K2 predecessor
(placement ran only under a disclosed research override). The K3 TIFF is a
quarantined research artifact; do not submit it, do not regenerate it (writer
refuses overwrite; surface gate fails closed without the override flag), and do
not treat the labelled projection as a score. Experiment budget for that
session is exhausted. The next lane must differentiate dot geography from the
fleet supervised consensus (preregistration slate C4/C5), with the same shared
evaluator/writer and preregistered gates.

## 2026-10-28 saved-byte/data preflight follow-up

Read `research/2026-10-28-next-lane-slate.md`,
`evidence/owner_mirror_preflight_2026-10-28.json` and
`evidence/public_downloads_audit.json` and
`evidence/session-31569490-run-card.json`. Every published TIFF is research-only;
`PASS_RESEARCH_ONLY` means file/hash/ZIP integrity, not scientific or organizer
approval. To repeat the GitHub-owner-mirror preflight without a human:
`bash scripts/download_competition_data.sh --research-mirror` (ignored cache,
NOT official inputs). Run `python scripts/audit_public_downloads.py --check`
before publishing: any extra or changed public TIF/ZIP stops CI. Do not label a
new method as assigned or clear the lattice witness by gaming footprint edges.

Read `research/release-gate-followup-2026-10-28.md`: the evidence schema now
requires three additional attestations; schema passage is not evidence verification.
H2 and B4 artifacts merged from main are also negative research files and are
included in the public research inventory (five files at that review; six after K3). Read
`evidence/current-session-review-2026-10-28.md` for the concurrent B4
integration: its artifact is research-only, its registry scan fails the literal
lattice stop, and its CLI/final generation are retired. Do not regenerate it or
claim uniqueness or organizer approval.
