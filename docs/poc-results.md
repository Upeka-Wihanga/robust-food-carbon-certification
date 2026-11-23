# Proof-of-concept evidence and migration status

This document records what is historically reported and what is actually
available in the current repository. “Completed” refers to the historical
research record; it does not imply that executable source is present here.

## PoC 1 — Robust certification oracle

- Research objective: compute conservative lower and upper bounds over complete
  ordered-composition polytopes and shared uncertain factors.
- Historical status: reported corrected and independently checked after the
  four-corner shortcut was withdrawn.
- Evidence supplied: Stage-14 and Stage-17 reviews, Stage-18 protocol, Stage-24
  report, and the research handoff descriptions.
- Source code available: **NO**.
- Frozen numerical evidence available: **PARTIAL**; reviews contain defect and
  independent comparison summaries, but the original module and case files are
  missing.
- Migration status: not started; package scaffold only.
- Validation required: formalized reconstruction, independent small-instance
  oracle comparison, tolerance tests, and metric compatibility.

## PoC 2 — Permanent four-corner regression

- Research objective: prevent reintroduction of the invalid four-corner
  rounded-disclosure shortcut.
- Historical status: counterexample established and reported reproduced by the
  corrected oracle.
- Evidence supplied: full construction and reported bounds in the Stage-14
  review; reproduction summary in the Stage-17 review.
- Source code available: **NO**.
- Frozen numerical evidence available: **PARTIAL**; numeric evidence is in the
  reviews, while the original executable fixture is missing.
- Migration status: not started.
- Validation required: encode the supplied construction without changing it,
  verify the old upper bound and corrected abstention independently, and retain
  it permanently.

## PoC 3 — Corrected QUID inverse

- Research objective: invert the declared branch-and-lattice publication rule,
  including thresholds, ties, impossible components, and disconnected unions.
- Historical status: repaired in Stage 18 after a conservative 4.5% boundary
  defect was identified.
- Evidence supplied: exact Stage-18 frozen protocol and Stage-17 defect report.
- Source code available: **NO**.
- Frozen numerical evidence available: **PARTIAL**; rules and boundary cases are
  frozen, but the original full fixture set and rerun outputs are missing.
- Migration status: not started.
- Validation required: exhaustive threshold/lattice tests and sampled
  publication-property checks for every returned component.

## PoC 4 — External Guan validation

- Research objective: test disclosure sufficiency on an external recipe source
  while preserving dataset-selection and minor-ingredient limitations.
- Historical status: Guan61 primary analysis and nonzero minor-ingredient
  sensitivity are reported complete.
- Evidence supplied: raw Guan workbook, Stage-18 protocol, Stage-24 report, and
  independent reviews.
- Source code available: **NO**.
- Frozen numerical evidence available: **PARTIAL**; cohort/scenario definitions
  and selected metrics survive, but pair/action manifests and derived CSVs do
  not.
- Migration status: raw source manifested; pipeline not reconstructed.
- Validation required: reproduce cohort selection, mappings, factor scenarios,
  pair construction, and frozen metrics without silently repairing exclusions.

## PoC 5 — FCID and dataFIELD pipeline

- Research objective: construct food/commodity representations, factor mappings,
  uncertainty scenarios, pairs, and policy inputs.
- Historical status: reported complete for the research PoCs.
- Evidence supplied: raw FCID CSV, raw dataFIELD workbook, Stage-24 report, and
  reviews.
- Source code available: **NO**.
- Frozen numerical evidence available: **PARTIAL**; selected counts and Stage-24
  outcomes survive, while original mappings, panels, manifests, and action CSVs
  are missing.
- Migration status: raw sources manifested; pipeline not reconstructed.
- Validation required: recover or explicitly re-specify inclusion and mapping
  rules before executing results.

## PoC 6 — Selectable disclosure policies

- Research objective: choose ranks without hidden exact shares; keep hindsight
  only as a labelled upper-bound reference.
- Historical status: selectable policies are reported evaluated.
- Evidence supplied: Stage-24 report and independent review descriptions.
- Source code available: **NO**.
- Frozen numerical evidence available: **PARTIAL**; policy-level discussion and
  some coverage figures survive, but policy code and frozen rank files do not.
- Migration status: not started.
- Validation required: establish each policy's allowed inputs and add explicit
  leakage tests before reproducing comparisons.

## PoC 7 — Dependence-aware evaluation

- Research objective: account for repeated recipe/food endpoints and assess
  leave-one-cuisine/group-out stability.
- Historical status: endpoint-node bootstrap and leave-one-stratum analyses are
  reported complete.
- Evidence supplied: Stage-24 report, progress tracker, and reviews.
- Source code available: **NO**.
- Frozen numerical evidence available: **PARTIAL**; selected intervals and
  completion statements survive, but bootstrap implementation and replicate
  files are missing.
- Migration status: not started.
- Validation required: reconstruct the exact resampling unit, weighting,
  stratification, pairing, seed, and interval calculation.

## PoC 8 — Stage-20 matched uncertainty attribution

- Research objective: compare share and factor information under a matched
  design and preserve the result as bounded historical evidence.
- Historical status: reported complete in the research brief.
- Evidence supplied: research/review narrative only.
- Source code available: **NO**.
- Frozen numerical evidence available: **NO**; original scripts and frozen CSV
  outputs are listed as missing.
- Migration status: blocked on evidence recovery or an explicitly labelled
  reconstruction protocol.
- Validation required: recover the frozen design and metrics; do not infer them
  from later Stage-24 claims.

## PoC 9 — Stage-22 information frontier

- Research objective: measure a balanced share/factor precision surface and
  establish that information value depends on the current uncertainty state.
- Historical status: reported complete but materially corrected/superseded in
  affected FCID decisions by Stage 24.
- Evidence supplied: Stage-24 report and tracker describe the correction and
  changed-decision counts.
- Source code available: **NO**.
- Frozen numerical evidence available: **PARTIAL**; correction summaries survive,
  but Stage-22 scripts and full response-surface CSVs are missing.
- Migration status: not started.
- Validation required: reconstruct both the original frozen surface and the
  corrected interpretation without claiming universal dominance.

## PoC 10 — Stage-24 targeted information acquisition

- Research objective: compare leakage-free selected share refinement with
  targeted factor refinement across coarse and saturation regimes.
- Historical status: frozen report marks the repair and experiment complete.
- Evidence supplied: Stage-24 report and progress tracker, including headline
  metrics, cost ratios, targeting audit, and limitations.
- Source code available: **NO**.
- Frozen numerical evidence available: **PARTIAL**; report-level numbers survive,
  while scripts, full surfaces, bootstrap replicates, and subset-audit CSVs are
  missing.
- Migration status: not started.
- Validation required: implement actual-interval midpoint interpolation,
  reproduce all recoverable report metrics, and retain the bounded PoC-only
  interpretation.

Selected frozen Stage-24 evidence includes 27 shifted DF-SD1 intervals and 91
changed decisions, and 100 shifted DF-SD2 intervals and 267 changed decisions.
The report also records 540 primary targeted cost/budget states: 470
share-favouring point estimates, 36 factor-favouring estimates, 34 ties, 243
bootstrap-supported share advantages, no bootstrap-supported factor advantage,
and 297 unresolved states. These are frozen report claims, not results
regenerated by this repository.

