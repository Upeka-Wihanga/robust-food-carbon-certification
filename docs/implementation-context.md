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
- QUID inversion is outside the current reconstructed core.
- Dataset reconstruction is outside the current reconstructed core.
- Recreation of the Stage-20, Stage-22, and Stage-24 experiments is outside
  the current reconstructed core.
- Reconstructed code must never be described as the unavailable original
  implementation.

The current engineering default tolerance is `1e-12`. It is newly defined for
this baseline and is not claimed to be a recovered historical tolerance.

