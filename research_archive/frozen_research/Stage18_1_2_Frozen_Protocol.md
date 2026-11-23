# Stage 18.1–18.2 Frozen Protocol

**Freeze date:** 23 November 2026  
**Frozen before Stage-18 empirical outcomes are inspected.**

## Entry condition

Stage 17 retained the corrected whole-interval oracle but identified:
1. a conservative QUID inverse edge defect near branch/lattice boundaries;
2. a major external-validity concern caused by structural zero production factors for under-5% Guan ingredients.

No novelty score is assigned in Stage 18.

# Stage 18.1 — Exact QUID publication-inverse repair

For a branch with grid step `s`, positive half-up rounding to published value `p` has preimage:

`[p-s/2, p+s/2)`

before intersection with the branch domain and rank-feasible range.

For robust extrema of continuous objectives, the solver may evaluate the **closure** of each nonempty valid preimage component because the supremum/infimum over the half-open component equals that over its closure.

A branch contributes only if `p` is an attainable lattice output for that branch.

Branches:

- branch L: true share `< 0.05`, grid `s=0.005`;
- branch H: true share `>= 0.05`, grid `s=0.01`.

Therefore:
- 4.5% is valid on the 0.5-pp lattice but not on the 1-pp lattice;
- 5.0% may receive contributions from both branches;
- impossible branch components must be absent, not represented as degenerate singletons.

### 18.1 gates

- explicit threshold/lattice tests for 4.5%, 5.0%, 5.5%, neighboring values and rank clipping;
- `publish(t)=p` property tests for sampled interior points of every returned component;
- no impossible branch component;
- Stage-17 4.5% defect reproduced by the old implementation and absent from the repaired implementation;
- rerun frozen FCID and Guan action sets and disclose all count changes.

# Stage 18.2 — Nonzero minor-ingredient Guan sensitivity

## Frozen cohort

Keep exactly the Stage-13/16 primary cohort:
- 61 eligible Guan recipes;
- 222 frozen within-cuisine pairs;
- 24,656 rank-pair actions.

No recipe may be added or removed because of Stage-18 outcomes.

## Major ingredients

Ingredients with source recipe share >=5% retain their existing Guan production factor.

Their uncertainty remains the primary shared ±25% box around the published factor.

## Minor ingredients with a direct Guan factor

For any <5% ingredient whose normalized name appears in the Guan factor table:
- use that published nonzero production factor;
- use shared ±25% uncertainty;
- share the same factor across recipes whenever the normalized ingredient is the same.

## Minor ingredients without a direct Guan factor

Fallback values are derived only from the positive production-factor distribution in the Guan factor table.

Frozen factor-distribution values:

- P25 = **1.145000 kgCO2e/kg**
- P50 = **1.810000 kgCO2e/kg**
- P75 = **4.763000 kgCO2e/kg**
- P95 = **8.721000 kgCO2e/kg**

The same normalized unmapped ingredient shares one fallback uncertain factor across recipes.

### Scenario M0 — historical source convention
Under-5% ingredients remain zero production impact.
This is the paired reference only.

### Scenario M1 — direct + median fallback
- directly mapped minor: published factor ±25%;
- unmapped minor: center = P50 = 1.810000, with ±25%.

Purpose: remove structural zero with a central positive fallback.

### Scenario M2 — direct + broad middle interval
- directly mapped minor: published factor ±25%;
- unmapped minor: factor interval `[P25, P75]`
  = `[1.145000, 4.763000]`.

Purpose: positive broad uncertainty without using extreme tail values.

### Scenario M3 — direct + conservative high interval
- directly mapped minor: published factor ±25%;
- unmapped minor: factor interval `[P50, P95]`
  = `[1.810000, 8.721000]`.

Purpose: deliberately high-impact sensitivity.

No scenario is selected after seeing its result.

## Primary outputs for every scenario

At the primary factor setting:
- exact-certifying actions / all actions;
- repaired-QUID certifying actions / all actions;
- conditional QUID retention among exact-certifying actions;
- exact-certifiable pairs / 222;
- repaired-QUID certifiable pairs / 222;
- conditional pair retention;
- direction/containment violations;
- decision changes relative to M0.

Also report:
- per-cuisine results;
- number/mass share of directly mapped vs fallback minor ingredients.

## Stage 18.2 interpretation gate

Positive external-validity survival requires the qualitative finding to persist under **all three nonzero scenarios**:
- rounded disclosure continues to retain a large majority of exact-certifying decisions;
- no containment/direction contradiction;
- absolute pair coverage remains nontrivial rather than collapsing.

No numerical pass percentage is invented after outcomes are seen. Results will be reported continuously and sent to an independent reviewer for significance judgment.

If the phenomenon collapses under one or more predeclared nonzero scenarios, that failure is retained as research-control evidence and the route is not promoted as the final FYP+Q1 contribution.
