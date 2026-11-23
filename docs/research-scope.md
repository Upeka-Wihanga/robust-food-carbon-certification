# Research scope

## Question

The project studies whether an ordered but incompletely quantified ingredient
composition contains enough information to guarantee the direction of a
pairwise modeled upstream production-carbon comparison. It also studies which
additional observation should be acquired when the current information is
insufficient.

## Declared mathematical boundary

For a food with ingredient shares `x1, ..., xn`, the declared model requires:

```text
x1 >= x2 >= ... >= xn >= 0
sum(xi) = 1
```

Disclosures may restrict selected shares to points, intervals, or multiple
valid inverse components. Certification must consider the complete feasible
ordered-composition set. It must not use the withdrawn four-corner rounded
percentage shortcut.

For foods A and B, the modeled difference is `D = C_A - C_B`. Robust lower and
upper bounds range over all allowed compositions and factor realizations.
Shared commodity factors remain shared across both foods when the declared
scenario specifies a common factor.

The decision rule is:

- certify A lower only when the upper bound is conservatively below zero;
- certify B lower only when the lower bound is conservatively above zero;
- otherwise abstain.

The validated historical tolerance and numerical handling must be recovered or
re-established explicitly during reconstruction rather than guessed.

## Environmental boundary

The present scope is normalized ingredient mass and upstream
ingredient-production greenhouse-gas factors. It excludes unsupported claims
about full product life-cycle impact, regulatory certification, supplier-level
sourcing, and universal commercial-label applicability.

## Disclosure settings

Regulatory-style QUID inversion and theoretical voluntary disclosures are
distinct experiments. The frozen evidence specifies a project-specific
two-branch half-up rounding model, but legal applicability to a particular
product remains outside the current evidence.

## Claim boundary

The Stage-24 share-first/factor-first pattern is historical PoC evidence under
tested scenarios. It is not a universal LCA law or a demonstrated globally
optimal acquisition policy.

