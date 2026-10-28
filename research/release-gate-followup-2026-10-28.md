# Release-gate follow-up — 2026-10-28

**No approved submission. Do not upload any current research TIFF.** This
session ran no geological experiments and did not consume a competition slot.
The assigned single method paragraph is absent, and the earlier K2 experiment
already crossed the required pre-placement stop. Reinterpreting the registry
or selecting a lane ourselves would not resolve that failure. See
[K2 protocol review](k2-protocol-review-2026-10-28.md).

## Three passes

1. **Review and implement.** Inspected the previous review, hypotheses, evidence,
   release gate and public executive summary. Strengthened the evidence-schema
   gate to require explicit attestations that (a) the baseline uses the same
   holdout protocol, (b) the surface passed the registry check *before* dot
   placement, and (c) the organizer template was authenticated. Missing or
   non-boolean attestations fail closed. These are claims in a card, not proof:
   this function does not authenticate evidence, compare registry inventory to
   the snapshot, validate TIFF bytes, reconstruct the baseline, or enforce
   chronology during generation. A passing schema is not authorization.
2. **Review edge cases.** Tested missing, false, numeric and string flags; kept
   the known prior H1 adapter negative because it cannot supply these facts.
   Existing serialized selector results are historical snapshots, not results
   under the revised schema. Historical K2 and other files remain quarantined.
3. **Re-check.** Full Python suite: 147 passed, 7 skipped (inputs unavailable),
   47 subtests passed; 38 rasterio/affine pending-deprecation warnings. No new
   holdout, uniqueness result, official score, portal receipt or current quota
   is inferred. The pre-existing nine-site table remains unverified owner reports,
   not organizer receipts or private-score estimates.

## Remaining work

- Obtain the actual lane assignment and a coordinated, complete registry policy
  and snapshot; resolve the lattice stop rule without silently exempting it.
- Authenticate organizer inputs and submission template, obtain the shared cached
  feature stack, and establish the exterior-value convention from the organizer.
  Mirror hashes demonstrate integrity of mirrors, not organizer provenance.
- Freeze a same-fold incumbent and use the shared evaluator/writer; test feature
  canaries, buffered whole-segment holdout and surface novelty *before* placing
  any dots. Capture evidence in a machine-verifiable, artifact-bound ledger;
  booleans alone are not a sufficient release system.
- Independently check final dots, saved TIFF bytes, registry completeness, current
  quota and selector decision. Compare the scored receipt to the exact artifact;
  a holdout score cannot be presented as a private leaderboard prediction.

The runtime's outbound allowlist permits GitHub but not DrivenData, Dropbox or
USGS; the enrolled competition account, current data, live leaderboard and
portal are not accessible here. The request's stated leaderboard figures
conflict and are not current verified observations. Manual review links:
[competition](https://www.drivendata.org/competitions/306/competition-doe-gems/),
[problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/),
[data](https://www.drivendata.org/competitions/306/competition-doe-gems/data/),
[official reference code](https://github.com/drivendataorg/gems-prize-reference-solution),
[GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and).
Links are not a claim of direct access to restricted hosts.
