# Stage 24 — Targeted Information-Acquisition Repair

**Status:** COMPLETE

## Executive result

The Stage-22 review's targeted-factor objection was tested directly. The factor policy now greedily refines the factor producing the largest reduction in the current robust comparison interval width per acquisition cost, while the share comparator refines the two already-selected share disclosures without hidden-share selection.

The result is a clear **two-regime information-acquisition pattern**:

1. **Coarse/order-only selected shares:** share refinement is usually the better first acquisition, even when factors are targeted and assumed much cheaper.
2. **After selected shares are already known to about +/-1 pp:** further share precision is nearly saturated and targeted factor refinement becomes the more valuable next acquisition across a wide range of cost assumptions.

## 1. Factor interpolation correction

The frozen protocol is now implemented literally: every partially refined factor interval shrinks toward the arithmetic midpoint of the actual frozen interval `[l,u]`.

- DF-SD1: **27** factor intervals had shifted centers; **91** Stage-22 surface decisions changed.
- DF-SD2: **100** shifted intervals; **267** decisions changed.

The discrepancy was therefore material and the affected FCID surfaces were recomputed. All Stage-24 analyses use the corrected interpolation.

## 2. Primary coarse-share targeted comparison

### Guan61 M2 / rank-weighted
At budget 2 with factors assumed **4x cheaper** than shares (factor/share cost ratio 0.25):
- share coverage: **37.4%**
- targeted-factor coverage: **14.9%**
- factor minus share: **-22.5 pp**
- 95% paired bootstrap interval: **[-32.6, -13.3] pp**.

At equal scalar cost and budget 2:
- share: **37.4%**
- targeted factor: **3.2%**
- difference: **-34.2 pp**
- 95% interval: **[-45.3, -23.2] pp**.

### FCID100 corrected SD1 / historical impact-variance
At factor/share cost ratio 0.25 and budget 2:
- share: **9.0%**
- targeted factor: **3.0%**
- difference: **-6.0 pp**
- 95% interval: **[-16.0, 1.6] pp**.

FCID is smaller/noisier, so this specific contrast remains statistically unresolved, but the point estimate still favors share refinement.

## 3. Targeting-quality audit

The greedy factor ranking was checked against exact minimum-width subsets on the primary datasets.

- best 1-factor subset: greedy matches **100%** of Guan and **100%** of FCID pairs;
- best 2-factor subset: greedy matches **98.2%** of Guan and **99.0%** of FCID pairs;
- exact best 1- or 2-factor subsets produce **zero additional certifiable pairs** over greedy.

Thus the coarse-regime result is not explained by an obviously poor factor-targeting heuristic.

## 4. Across all primary targeted cost/budget states

Across **540** dataset/scenario/policy/cost/budget states:
- share-favoring point estimates: **470**
- factor-favoring point estimates: **36**
- ties: **34**
- bootstrap-supported share advantage: **243**
- bootstrap-supported factor advantage: **0**
- unresolved: **297**.

There is **no bootstrap-supported factor advantage** when starting from order-only/maximally coarse selected-share uncertainty within the tested cost range.

## 5. Secondary confirmatory saturation-regime test

This analysis was frozen after the primary result and is explicitly secondary. It starts with both selected shares already constrained to +/-1 pp.

### Guan61 M2
Equal cost, budget 1:
- further share refinement: **36.9%**
- targeted factor refinement: **50.9%**
- factor advantage: **14.0 pp**
- 95% interval: **[7.0, 22.4] pp**.

Factors twice as expensive, budget 2:
- factor advantage: **13.5 pp**
- 95% interval: **[6.6, 21.9] pp**.

Factors four times as expensive, budget 2:
- factor advantage: **5.9 pp**
- 95% interval: **[1.6, 11.1] pp**.

### FCID100 corrected SD1
Equal cost, budget 1:
- further share: **9.0%**
- targeted factor: **17.0%**
- factor advantage: **8.0 pp**
- 95% interval: **[1.4, 15.9] pp**.

Factors twice as expensive, budget 2:
- factor advantage: **8.0 pp**
- 95% interval: **[1.4, 15.9] pp**.

At four-times factor cost and budget 2 the point advantage is **4.0 pp**, but FCID remains statistically unresolved.

## 6. Corrected staged acquisition rule

The evidence now supports the following bounded rule:

> **When the selected ingredient shares are very coarse, improve share precision first. Once those shares reach the observed saturation regime around +/-1 percentage point, stop spending effort on making them exact and redirect additional information-acquisition effort toward the most influential impact factors.**

This is not claimed as a universal LCA rule or a measured real-world cost optimum. It is an empirical result under the tested robust-certification model and cost sensitivities.

## 7. Stability and reproducibility

- leave-one-cuisine/group-out results required by the prior frozen protocol are now produced;
- significant secondary factor-advantage states remain directionally stable under leave-one-stratum removal;
- the portable package contains raw FCID, dataFIELD and Guan sources plus frozen policy/pair inputs and relative-path scripts;
- the primary relative-path components were executed individually from the bundle;
- frozen expected metrics returned **METRIC COMPARISON PASS**;
- the secondary relative-path scripts were also executed successfully.

The hosted environment interrupts a parent process that launches all nested multiprocessing stages in one uninterrupted wrapper, so the verified component commands are documented rather than hiding that orchestration limitation.

## 8. Prior-work boundary

Gregory et al. (2016) already establishes comparative-LCA resolvability, influential-parameter identification and iterative uncertainty refinement. Marchese et al. (2018) explicitly applies value-of-information analysis to prioritize LCA data acquisition under differing costs. Bohn et al. (2022) establishes optimization-based reconstruction of ingredient compositions from mandatory labels.

Therefore the candidate novelty is **not** targeted uncertainty reduction itself. The narrower candidate contribution is the measured, deterministic worst-case food-certification result that the preferred information source switches with disclosure precision: **share-first when composition is coarse, factor-first after share precision saturates**.

## 9. Next step

No further internal novelty experiment is recommended. The corrected Stage-24 contribution should now receive one genuinely blind independent review with the complete evidence/reproduction package and explicit Gregory/Marchese/Bohn positioning.
