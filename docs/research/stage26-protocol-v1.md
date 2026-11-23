# Stage 26 — Frozen Protocol v1

## Observation-Aware Sequential Acquisition for Robust Food-Carbon Certification

**Frozen:** 2026-11-23  
**Primary purpose:** Run the final research experiment needed before independent publication-gate review.

## 1. Research question

Under ordered but incompletely disclosed food compositions and shared uncertain ingredient-production emission factors, can an observation-aware sequential acquisition policy improve robust pairwise certification efficiency by choosing whether to acquire ingredient-share information or impact-factor information under a matched limited budget?

A secondary mechanism question asks whether the preferred information source changes as starting share information becomes more precise.

## 2. Locked prior work

This experiment does not reopen or retune the corrected complete interval oracle, repaired QUID inverse, shared-factor model, upstream ingredient-production scope, Stage-18/20/22/24 preliminary results, or the nonzero-minor Guan sensitivity framework.

Stage 24 is motivation, not a target that Stage 26 is required to reproduce.

## 3. Primary data/scenario

- Dataset: **Guan61**
- Primary uncertainty scenario: **M2**
- Pairing: all frozen within-cuisine pairs
- Outer evaluation: **8-fold leave-one-cuisine-out**
- Secondary cohort: Guan86 M2 if reconstructed without changing the primary protocol

The Stage-26 held-out cuisines are held out from Stage-26 policy selection/tuning. They are not claimed to be historically unseen because earlier aggregate work used Guan61.

## 4. Starting share-information regimes

Run all four:
- ORDER_ONLY
- ±5 pp
- ±2 pp
- ±1 pp

Quantitative starting intervals must be generated via a declared rounded disclosure whose published value determines interval location. Hidden exact shares must not simply be used as interval centers.


### 4.1 Frozen share-rank preselection

Exactly one share rank per food is eligible for Stage-26 acquisition.

Before quantitative disclosure, select:

`r* = argmax_r [ factor_midpoint(r) * feasible_share_width(r) ]`

using only the frozen factor interval midpoint and order-only rank geometry.

Tie-break: lowest rank number.

The selected rank is fixed across all policies, worlds, budgets and starting regimes. Exact recipe shares are prohibited from rank selection.

For `±δ` starting precision, round the latent selected share half-up to a grid of width `2δ`; invert the published value to its feasible interval and intersect with the selected-rank geometry.

A share acquisition reveals only this preselected share. No post-observation rank substitution is allowed.

## 5. Latent truths and observations

### Shares
Recipe shares from the source are latent truth.

### Factors
For each of 100 fixed worlds, independently draw one latent value for every shared factor key:

`e_k ~ Uniform(l_k, u_k)`

where `[l_k,u_k]` is the frozen initial M2 interval.

A factor key uses the same latent value wherever it appears.

Seeds: `26000..26099`.

### Acquisition
One unit-cost acquisition fully reveals one currently uncertain share or factor variable in the primary controlled experiment.

The policy sees an acquired value only after choosing that action.

After each observation, update the uncertainty set and recompute the robust certificate.

## 6. Budget

Primary:
- share cost = 1
- factor cost = 1
- total budget B = 2

Secondary descriptive budgets:
- B=1
- B=3

Do not move the primary endpoint to another budget after viewing results.

## 7. Baselines

- B0 share-only
- B1 factor-only
- B2 fixed Stage-24-inspired staged rule
- B3 expected interval-width-reduction mixed policy
- B4 one-step certification-VOI policy
- P OASA two-step budget-aware rollout
- H hindsight ceiling (upper bound only)

All implementable methods use identical information, actions, costs, and observation models.

## 8. Fold-level strongest baseline

Within each LOCO fold:
1. use only seven training cuisines to rank B0-B4;
2. freeze the best baseline identity;
3. compare OASA with that selected baseline on the held-out cuisine.

The held-out cuisine cannot select its own comparator.

## 9. OASA

At B=2, for each available first action, estimate expected terminal certification at the end of the two-step budget over possible observation outcomes.

Choose the action with maximum expected terminal value.

After the real observation:
- update state;
- recompute robust certificate;
- choose the final action from the updated state.

The expectation model may use training-fold share distributions and the declared factor prior only.

No held-out truth or hindsight action value may enter action scoring.

## 10. Primary metric

Macro-average terminal robust certification coverage across:
- ORDER_ONLY
- ±5 pp
- ±2 pp
- ±1 pp

at B=2, Guan61 M2, equal costs.

Primary effect:

`coverage(OASA) - coverage(fold-selected strongest implementable baseline)`

## 11. Inference

Use 5,000 paired dependence-aware bootstrap replicates.

Resampling must respect recipe-node dependence and cuisine structure and must not treat the 222 pair edges as independent.

Factor-world uncertainty remains paired across policy comparisons.

## 12. Safety gate G26-0

Required before performance interpretation:
- 100% observation-set containment of latent truth;
- 0 false-direction robust certifications;
- no held-out leakage;
- exact cost/budget accounting;
- deterministic reproduction under frozen seeds.

Failure blocks the performance result.

## 13. Policy-value gate G26-1

Strong PASS requires:
- primary improvement >= +5.0 percentage points;
- paired dependence-aware 95% CI lower bound > 0.

Positive CI but <5 pp: statistical PASS / practical WARNING.  
Positive estimate with CI crossing zero: UNRESOLVED.

## 14. Switching gate G26-2

PASS requires:
- share-first majority in pooled ORDER_ONLY + ±5 pp;
- factor-first majority at ±1 pp;
- factor-first rate at ±1 pp at least 20 pp higher than pooled coarse rate;
- same coarse-to-tight direction in at least 6/8 held-out cuisines.

Failing this gate prohibits a validated prospective switching claim.

## 15. Result classes

**STRONG PASS:** G26-0 + strong G26-1 + G26-2 all pass.

**PARTIAL PASS:** G26-0 passes and only part of the policy/mechanism evidence succeeds.

**FAIL:** G26-0 fails, or neither policy value nor mechanism is supported.

A Stage-26 failure does not invalidate the robust-certification FYP or Stage-24 preliminary evidence.

## 16. No post-hoc recovery

After the first valid held-out run, do not change primary budget, starting precision set, effect threshold, factor latent distribution, baselines, primary metric, or held-out folds.

Only verified implementation/data defects permit rerunning the frozen protocol.

## 17. Publication authorization

After Stage 26 is frozen:

- Gate 1: independent publishability estimate >=70%.
- Gate 2: IEEE Access suitability >=7/10 and novelty >=7/10.

Begin the IEEE Access/Q1 draft only after both pass.
