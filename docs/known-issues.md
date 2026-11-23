# Known issues

## Missing historical implementation

The original validated research Python implementation is not currently
available. In particular, the whole-interval oracle, randomized LP comparator,
QUID inverse, data pipelines, policies, bootstrap, and Stage-20/22/24 scripts
are absent. Recreated code must be labelled `reconstructed_baseline`, not
`original_source`.

## Missing derived artifacts

Some historical derived CSVs, pair/action manifests, frozen selected-rank files,
bootstrap replicates, subset audits, full response surfaces, and the original
portable reproduction ZIP are missing. Headline reports cannot substitute for
their exact bytes.

## Python runtime unresolved

`python.exe` and `python3.exe` currently resolve only to inaccessible Windows
Store aliases. The Python launcher, uv, and conda were not found. No runtime was
installed and no PATH or system setting was changed during bootstrap.

## Data rights unresolved

The licensing and redistribution status of all three raw sources requires
review. They are intentionally not committed.

## Handoff description mismatch

`handoff/00_READ_ME_FIRST.md` describes
`frozen_research/Pasted text.txt` as the original/current research brief. The
file's actual contents begin with “Stage 19 — Independent Research Review” and
are review material rather than the repository brief supplied separately in
the project conversation. The historical file is preserved unchanged and is
not silently renamed.

## Evidence versus implementation statements

The Stage-24 report says a portable package contained raw inputs, frozen policy
and pair inputs, and relative-path scripts, and that metric comparison passed.
Those scripts and frozen inputs are not present in the current handoff. This is
a provenance gap, not evidence that the reported work did not occur.

The progress tracker calls reproducibility “substantially complete,” whereas
the current bundle lacks the historical executable package. Repository
documentation therefore describes current reproducibility as evidence-level,
not source-to-output reproduction.

## Incomplete research and application

The final observation-aware sequential acquisition experiment has not been
completed. Realistic observation models, held-out sequential evaluation,
strong baselines, cost justification, and broader commercial validation remain
open. No production UI exists.

