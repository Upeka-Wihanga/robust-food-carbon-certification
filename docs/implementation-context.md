# Implementation context

This repository contains a `reconstructed_baseline`, not the unavailable
original historical implementation. Future mathematical implementation work
must preserve these non-negotiable rules:

- Ingredient shares satisfy the ordered-simplex constraints
  `x1 >= ... >= xn >= 0` and `sum(xi) = 1`.
- Certification uses the complete interval-constrained composition polytopes.
- The historical four-corner rounded-percentage shortcut is permanently
  rejected.
- Identical commodity codes share one factor variable whenever the
  shared-factor model is active.
- Certification uses strict robust sign conditions.
- Borderline numerical values abstain under an explicit tolerance.
- QUID publication and inversion follow the permanently corrected rules below.
- Dataset reconstruction is outside the current reconstructed core.
- Recreation of the Stage-20, Stage-22, and Stage-24 experiments is outside
  the current reconstructed core.
- Reconstructed code must never be described as the unavailable original
  implementation.

## Permanent corrected QUID rules

- A true share below 5% uses a 0.5 percentage-point publication step.
- A true share at or above 5% uses a 1 percentage-point publication step.
- Publication uses positive half-up rounding.
- Lattice attainability is checked before constructing an inverse component
  for a branch.
- Impossible branches are absent; they are never represented by singleton
  placeholders.
- Exact inverse components may be half-open.
- The closure of a nonempty component is used only for continuous robust
  optimization, after branch and component validity have been established.
- Disconnected components remain separate and must not be silently replaced
  by one enclosing interval.

The current engineering default tolerance is `1e-12`. It is newly defined for
this baseline and is not claimed to be a recovered historical tolerance.

