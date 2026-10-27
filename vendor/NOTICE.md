# Shared-tool provenance

`gems57/*.py` are unchanged copies of the shared tools published in
buffedlizard55-lab/GEMSDOE32 at commit
73485f27cf230af770167397c2b72cb9ce3b3f25, retrieved 2026-10-27.
Per-file SHA256 and immutable source links: `evidence/sources.json`.
No license grant beyond any applicable upstream terms is asserted here.

This is a new checkout without its own template. Reusing a pinned shared
implementation is not a private evaluator fork. Neither the scorer nor writer
was modified in this session. New geological features live only in the runner.

The inherited `scripts/fetch_focus_registry.py` did trust same-size cached files.
Its one local template copy now verifies Git blob hashes against the tree and
rejects truncated trees; `tests/test_registry_fetch.py` exercises equal-size
corruption. This flaw did not affect the initial fetch (the cache was empty).
Upstream repositories are read-only, so the fix has not been applied there.
The inventory retains the upstream path/size filters and does not certify all
submissions. Never weaken the shared uniqueness thresholds to approve a file.
