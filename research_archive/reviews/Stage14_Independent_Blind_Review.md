# Stage 14 — Independent Blind Reviewer Report

**Review date:** 23 November 2026  
**Review object:** *Robust Carbon Certification from Rounded Ingredient Percentages: A Disclosure-Precision Frontier for Ordered Food Compositions*  
**Material reviewed:** All files in `Stage14_QUID_Disclosure_Precision_Blind_Review_FROZEN.zip`, including frozen protocols, reports, CSV summaries/audit and the SHA-256 manifest; independent mathematical counterexamples; focused checks against published literature and official publisher/regulator documentation.

## Verdict

**REVISE — current version fails the supervisor PASS gate and is not ready for IEEE Access submission.** This is a potentially viable FYP research question, but there is a **dispositive counterexample to the principal four-corner certificate algorithm**, as well as a separate non-nesting problem for the tested precision family. Existing reported retention numbers cannot be treated as verified robust-certificate retention until recomputed with a sound interval solver.

| Criterion | Strict independent rating | Reason |
|---|---:|---|
| Novelty | **6.0 / 10** | A focused and potentially useful domain synthesis, but interval robust classification, precision selection and generic exact optimization are established. No new general theorem or demonstrated algorithmic advance survives as presented. |
| Mathematical soundness | **3.0 / 10** | The stated convexity of the point-disclosure upper bound is false in general, so the four-corner reduction can issue false certificates; the tested precision bins are not necessarily nested. |
| FYP suitability | **7.0 / 10** | A coherent, measurable, and repairable applied-optimization project. The present results should not be submitted as final scientific evidence. |
| IEEE Access/Q1-style publication potential | **3.5 / 10** | IEEE Access requires technically correct, distinct work and empirical evidence. Current central certificate is unsound; after repair, novelty and practical significance still need stronger evidence. |
| Reproducibility | **4.0 / 10** | All included Stage-14 packet files agree with their SHA-256 hashes, but the actual Stage-13 action/pair result CSVs, raw workbook, and runnable code are missing from this ZIP. Earlier A7.2 reported only a partial clean computation. |
| IEEE Access scope/suitability (additional) | **7.0 / 10** | Applied verification, optimization and sustainable computing are plausible cross-disciplinary fit; technical correctness and actual advance are separate questions. |
| Feasibility of a corrected FYP (additional) | **6.5 / 10** | Corrected polytope optimization and targeted reruns are plausible, but computational cost and clean reproduction need demonstration. |

**Gate:** novelty 6.0 < 7 and soundness 3.0 < 8; a mathematical counterexample exists. **FAIL.**  
**Direct prior equivalent found?** NO direct equivalent found in the focused searches; this is not proof that one does not exist.  
**Mathematical counterexample found?** YES, explicit and exactly checked below.

## 1. Hard-kill finding: the four-corner theorem is false

The packet defines ordered shares for A, with `x1 >= x2 >= x3 >= 0` and `x1+x2+x3=1`. Fix its second ingredient percentage at `t=x2`. Feasibility gives

```
x3 <= t                 (because x2 >= x3)
x3 <= 1 - 2t           (because x1 = 1-t-x3 >= t)
=> max x3 = min(t, 1-2t),   0 <= t <= 1/2.
```

This is a concave, piecewise-affine tent whose **maximum is at t=1/3**, not necessarily at a disclosure-interval endpoint. This disproves the packet's assertion that the point-disclosure worst-case upper bound must be convex in `(t,u)`.

### Positive-factor, ±25%-uncertainty example (realistic 1 pp QUID bin)

- A has three **distinct commodities**, with mean emission factors `cA=(0.01, 0.01, 1.00)` and each independent uncertainty interval `[0.75*c,1.25*c]`.
- B has two **distinct other commodities**, both with mean emission factor `0.564`, also each `[0.75*c,1.25*c]`.
- Ingredients are ordered; true A shares can be `x=(0.34, 0.33, 0.33)`, and true B shares `y=(0.75,0.25)`.
- Both disclosures are rounded to the nearest 1 percentage point, yielding `t in [0.325,0.335]` and `u in [0.745,0.755]` (ties do not affect the construction).
- Since commodities are distinct across foods, the uncertain factors can independently make A worst and B best. For **any** fixed B first share `u`, B's minimum intensity is `0.75*0.564=0.423`.

Therefore the **exact** point-disclosure worst-case upper difference is

```
U*(t,u) = 1.25 * [0.01 + 0.99 * min(t,1-2*t)] - 0.423.
```

It is independent of `u`.

| t | x3 maximizer | Exact U*(t,u) | Corner algorithm's classification |
|---|---:|---:|---|
| `0.325` | `0.325` | `-0.0083125` | A certified lower |
| `0.335` | `0.330` | `-0.0021250` | A certified lower |
| `1/3` | `1/3` | `+0.0020000` | A **NOT** robustly certified lower |

For all four rectangle corners (two A endpoints times two B endpoints), `U*<0`, so the proposed corner algorithm issues a certificate. But the admissible **interior** recipe `x=(1/3,1/3,1/3)` makes `U*>0` and invalidates it. Importantly, the actual true A share `t=0.33` gives `U*=-0.002125<0`, so **this is specifically a false *retention* of an exact-percentage certificate**, not merely a certificate for an action absent from the retention denominator.

The counterexample uses positive emission factors, the exact ±25% box model, a legal ordered mixture, and a genuine 1 percentage-point rounded disclosure rectangle. No floating-point ambiguity is involved.

**Implication:** The following packet statements are false as universal claims:
1. `U*(t,u)` is convex and `L*(t,u)` concave in the disclosed percentages.
2. Four outside rectangle corners always yield exact rounded-disclosure certification.
3. Reported QUID retention is established by evaluating only those four corners.

The third is conditional on the reported code actually using that method, as the Stage-13 runnable implementation was not included. If it did, retention may be **overestimated**, and its true magnitude is unknown from this archive. The reported figures should be treated as **provisional results of a potentially unsound evaluator**, not as independently established robust rates.

## 2. Second mathematical finding: the tested precision family need not be nested

The monotonicity statement is correct for *set-inclusion nested* intervals. It does **not** hold automatically for independently re-rounded grids `1pp, 2pp, 5pp, 10pp`.

For a true share of `60.9%`:

- nearest **1 pp** produces `61%`, meaning `[60.5%,61.5%]`;
- nearest **2 pp** produces `60%`, meaning `[59%,61%]`.

Neither set contains the other. Consider a valid affine robust upper bound increasing with `t`, with its strict-sign threshold at `61.2%`: a certificate can **fail at 1 pp** (because `61.5%` is allowed) yet **pass at 2 pp** (because `61%` is the maximum). Such increasing bounds arise from two-ingredient ordered mixtures with suitable positive carbon factors. Therefore a reported coarsest tested passing grid can still be listed descriptively, but **monotone frontier, binary search, and 'failure cannot be undone by coarsening' claims need genuine nested partitions or a redesigned information-order definition**.

## 3. Correct mathematical repair

For a disclosure interval `I`, define the complete feasible ordered-composition polytope:

```
P_A(I) = {x: x1>=...>=xn>=0, sum(x)=1, lo<=x_i<=hi}.
P_B(J) similarly.
```

Let `d = A*x - B*y` and shared uncertain factors satisfy `e_k in [m_k-rho_k,m_k+rho_k]`. The true rounded-disclosure extremes are

```
U_IJ = max_{x in P_A(I), y in P_B(J)} [m^T d + rho^T |d|]
L_IJ = min_{x in P_A(I), y in P_B(J)} [m^T d - rho^T |d|].
```

The upper expression is **convex in `(x,y)`**, so its maximum over the *full composition polytope* is attained at an extreme point; the lower expression is **concave**, so its minimum is also attained at an extreme point. Thus a defensible exact evaluator can enumerate **vertices of the interval-constrained ordered-composition polytopes**, not just four outer percentage corners, and evaluate the robust shared-factor endpoint at every required vertex pair. Equivalent exact LP/constraint-generation methods may be used if independently verified. A parametric solver may instead check boundary and **interior chamber-breakpoint intersections**, subject to a complete proof.

A corrective regression test must include the example above and every crossed reciprocal breakpoint `1/k`; compare against a generic exact/verified LP or exhaustive vertex oracle on small instances. Retain strict `U<0` and `L>0` sign checks, with inconclusive results for uncertified numerical signs.

Use truly **nested** disclosure intervals for monotone frontier theory, or explicitly report a potentially non-monotone set of pass/fail outcomes on separately rounded grids. Model QUID rounding as the inverse image of the *published value* under the legal rule, especially at the 5% branch boundary.

## 4. Audit of the reported external results

The Stage-13 report and accompanying CSV summaries are arithmetically consistent, and all files **present in the archive** match the stated Stage-14 SHA-256 hashes. The summary by cuisine totals exactly `61` eligible recipes, `222` pairs, `24,656` rank-pair actions, `2,210` exact-certifying actions, `2,109` reported QUID-retained actions, `108` exactly certifiable pairs, `107` reported QUID-retained pairs, and zero recorded conflicts.

**Reported metrics (not independently recomputed):**

| Metric | FCID development | Guan frozen external |
|---|---:|---:|
| All rank-pair actions | 7,594 | 24,656 |
| Exactly certifying actions | 604 | 2,210 |
| Reported QUID-retained actions | 567 | 2,109 |
| Reported action retention | 93.87% | 95.43% |
| Exactly certifiable pairs | 29 | 108 |
| Reported QUID-retained pairs | 28 | 107 |
| Reported pair retention | 96.55% | 99.07% |

**Interpretation:** The 95.43% is conditional on *already exactly certifying actions*, not on all query actions. The external reported retained action fraction of all actions is only `2,109/24,656 = 8.55%`. The reported retained pair fraction of all within-cuisine pairs is `107/222 = 48.20%`. These are different questions and should all be shown.

**Selection/generalization limitation:** The external publication has 320 dishes. Only 308 parsed and **61/308 (19.81%)** were eligible; 247 parsed recipes were excluded. The supplied eligibility audit reveals most exclusions have large carbon-reconstruction discrepancies; across 308 rows the median relative reconstruction error is approximately **27.15%**. The narrow retained set matched well, but that does not eliminate severe selection bias or demonstrate transfer to a representative sample of the original recipes. Eligibility ranges from 5 recipes for Min to 12 for Hui, and Chuan's reported action retention is only `75/101 = 74.26%`.

**Shared pair dependence:** The 222 within-cuisine pairs are not independent experiments; they share recipes, commodities, and factor assumptions. The 24,656 actions are more strongly correlated. Report uncertainty at recipe/cuisine clustering levels instead of treating actions as independent observations. Pair retention is more salient than action retention but can be high simply because many rank combinations are available per pair.

**Direction conflicts:** Zero conflicts is nearly a logical consequence of sound interval containment: if the true point is inside the rounded set, a sound rounded A-certificate cannot contradict a sound exact B-certificate. Therefore zero conflicts is a valuable internal consistency check but **not independent evidence that the corner method is sound**.

**Uncertainty and scope:** The shared ±25% box may be an informative engineering stress test but is not an empirically justified uncertainty distribution for every commodity. A reported 'carbon certification' covers **ingredient production only**, not processing, logistics, retail, cooking, packaging or a branded product's full LCA. The Guan article deliberately excludes under-5%-mass ingredients from carbon accounting; giving them fixed zero emissions is a **source convention**, not an assertion they have zero true emissions. The model must handle this counterfactual limitation carefully when interval uncertainty allows compositions to cross 5%.

**QUID practical boundary:** The FSAI guidance applies QUID to selected characterizing ingredients. It does not mandate percentages for every ingredient rank. A demonstration on actual labels or a realistic query-availability mask is essential for claims about practical deployment. The project's QUID branch is defined using the hidden true share; a consumer-facing verifier must invert the published rounded value and the applicable rounding convention without assuming knowledge of the hidden share.

## 5. Reproducibility audit

- **Verified:** Every included packet item in the Stage-14 manifest has the specified hash/byte length; Stage-13 cuisine totals and precision-curve percentages are internally coherent; 308 eligibility-audit rows are included.
- **Documented but not independently established:** The frozen protocol preceded access to the Guan workbook; the workbook hash matched; A7.2 computed 516 action smoke tests with zero mismatches; exact-arithmetic boundary tests passed. These are credible *reports*, not independently rerun results.
- **Absent from this ZIP:** The actual Guan workbook, Stage-13 parsing/execution source, per-action/per-pair results and outputs, input-to-claim reproduction runner, and complete A7.2 bundle. The Stage-13 manifest names some of these absent artifacts and their hashes, which cannot substitute for their bytes.
- **Full rerun:** A7.2 itself states the 7,594-action clean full rerun is still pending. That earlier run also does not establish the mathematical correctness of the Stage-14 rounded extension.

## 6. Literature and publication position

I did **not** find a published paper that directly implements the same full QUID+ordered-composition+shared-carbon+coarsest-disclosure synthesis in focused searches. However, the theory and core optimization components draw on established robust optimization, decision-dependent information discovery and parametric LP methods. A missing direct equivalence is **necessary but not sufficient** for novelty ≥7: the new research contribution must be more than a straightforward application of established ideas.

Relevant independently checked sources:

1. Food Safety Authority of Ireland, QUID guidance: https://www.fsai.ie/business-advice/labelling/labelling-general-labelling/quid
2. Vayanos, Georghiou & Yu, *Robust Optimization with Decision-Dependent Information Discovery*, *Management Science*, published online 2025, 2026 volume: https://pubsonline.informs.org/doi/10.1287/mnsc.2021.00160
3. Paradiso et al., *Exact and Approximate Schemes for Robust Optimization Problems with Decision-Dependent Information Discovery*, *INFORMS Journal on Computing*: https://pubsonline.informs.org/doi/10.1287/ijoc.2023.0290
4. Chen, Goerigk & Poss, *The robust selection problem with information discovery* (2026): https://www.sciencedirect.com/science/article/pii/S0166218X25007231
5. Guan et al. 2026, *Scientific Data*: https://pmc.ncbi.nlm.nih.gov/articles/PMC13737097/
6. IEEE Access, official reviewer guidelines: https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/

IEEE Access explicitly assesses contribution, technical correctness, sufficient evaluation and novelty relative to prior art, and it does **not** require unusually high novelty if distinct, technically sound applications provide value. Thus a sound revised applied study is plausible in principle, but the existing version cannot meet the technical-correctness threshold.

## 7. Strongest rejection argument

**The sole advertised exact rounded-disclosure shortcut is mathematically unsound and can create false A-lower-carbon certificates even in a standard 1 pp disclosure bin where the original exact-percentage action correctly certified A.** Consequently the numerical retention and precision-frontier claims cannot safely be used as evidence for the proposed novelty without an exact rerun. Independently, the quantization grids used for the frontier are not a nested family, invalidating the unconditional monotonicity narrative.

## 8. Strongest acceptance argument

The research identifies a concrete, practically motivated engineering question: what minimum public numerical ingredient precision suffices to support a guaranteed *production-stage* comparative carbon result under ordered recipes and shared factor uncertainty? Its development-to-external validation design, explicit negative generic-comparator disclosure, and source-convention audit are valuable foundations. With a sound evaluator, robust uncertainty sensitivity, transparent eligibility analysis, realistic disclosure availability and compelling baselines, the topic can still support a substantial FYP and perhaps an applied-methods manuscript.

## 9. Required changes before supervisor approval

1. **Withdraw the convexity/four-corner proof** as stated; include the explicit rational counterexample above as a permanent regression test.
2. **Implement and independently verify** a correct whole-interval robust endpoint oracle; test against generic exact LP/vertex enumeration on small exhaustive cases.
3. **Rerun both FCID and Guan** exact-versus-QUID action and pair retention using the corrected oracle, preserving old frozen case IDs and denominators; report changes and false-certificate counts.
4. **Fix the 'nested precision' claim:** nested disclosure refinements or honest nonmonotone grid-specific results.
5. **Provide actual source and action-level outputs** in one-command clean reproduction bundle with per-record hashes, solver versions and deterministic input serialization.
6. **Interpret Guan's 61/308 eligible fraction** and report differences between included/excluded dishes. Keep stage-13 original frozen criterion visible while adding clearly labeled sensitivity analyses.
7. Ask for a genuinely new reviewer novelty/methodology assessment only after (1)–(6), not simply a confirmation of the reported 95.43%.

## 10. Required changes before journal submission

All above, plus: (i) a disciplined paper-by-paper novelty matrix; (ii) a realistic QUID/actual-label feasibility study of which ranks are disclosed; (iii) sensitivity to factor uncertainty levels, factor dependence and excluded-under-5% mass; (iv) meaningful baselines (conservative whole-polytope LP, naïve interval bounds, exact-disclosure reference and, if applicable, generic robust methods); (v) cluster-aware uncertainty and per-cuisine limitations; (vi) reported computations/time/memory/scaling and numerical certification; (vii) real-world practical-significance analysis, not merely high conditional retention; and (viii) a reproducibility archive with independently verified full runs.

## 11. Answers to the 45 blind-review questions

### Part A — Mathematical soundness

**1. Is the rounded percentage correctly represented as an interval?** Broadly yes within a declared known grid and specified tie convention; the true inverse at the 5% piecewise branch may be a union/piecewise interval, so the packet's simple rule is not universally complete.  
**2. Is U* convex and L* concave in disclosed values?** **No.** The ordered three-ingredient construction gives a nonconvex tent-shaped U*.  
**3. Does that justify checking only rectangle corners?** **No.** Interior `t=1/3` defeats all-corners certification.  
**4. Are strict inequalities correct at zero?** Yes mathematically; exact-zero must abstain, and tolerance-based signs need verified bounds.  
**5. Is coarsest precision well defined for actual tested family?** A coarsest *passing member of a finite grid* may be defined, but the claimed monotone frontier is not assured because independently rounded bins are not nested.  
**6. Can coarser disclosure restore a certificate after finer failure?** Yes for the actual nonnested 1/2 pp re-rounded bins; no if feasible disclosure sets are rigorously nested by inclusion.  
**7. Is shared-factor uncertainty consistent for repeat commodities?** The algebra is consistent when each standardized commodity is represented by one shared factor; independent factors for repeated entries would be wrong.  
**8. Hidden assumptions in exact-to-interval move?** Yes: complete enumeration of interior feasible vertices, correct inverse rounding, public knowledge of precision, fixed ingredient identity/order, stability of factor/zero-factor assignments.  
**9. Is point-disclosure solver adequate though not novel?** It may be a useful validated subroutine for exact points, but it alone does not produce sound full-interval extrema through four calls.  
**10. Concrete counterexample?** **Yes:** section 1, with all four corner U values negative and an interior U value positive.

### Part B — External validation

**11. Is Guan external to development?** It is a distinct published dataset/source from FCID, but complete procedural independence cannot be externally verified from this archive.  
**12. Was the protocol frozen before inspection?** The included documents assert so and have matching hashes; an independent timestamp/remote preregistration or signed logs are needed to verify sequencing.  
**13. Were all eligible within-cuisine pairs included?** The cuisine counts match `n(n−1)/2` and sum to 222; missing runnable records prevent full independent verification.  
**14. Are reconstruction and factor rules defensible?** As a clearly restricted reanalysis of Guan's production boundary, yes; the 61/308 eligible fraction, large errors elsewhere and conditional zero-factor convention substantially limit generalization.  
**15. Does 61 vs 62 borderline materially change conclusion?** Reported sensitivity says no, but the primary threat is the unsound interval evaluator rather than this single case.  
**16. Are 95.43%/99.07% interpreted correctly?** Ratios are arithmetically correct conditional on reported classifications, but are **not** independently established sound retention; avoid implying rates across all actions or all pairs.  
**17. Is pair retention inflated by many rank-pair actions?** Potentially yes—one surviving action among many suffices, and the multiple opportunities are highly dependent.  
**18. Best evidence unit?** All three: action (algorithm behavior), pair (meaningful comparison decision), cuisine and recipe clusters (transfer/generalization).  
**19. Does weak Chuan retention matter?** Yes: 74.26% indicates important heterogeneity and undermines universal-performance language.  
**20. Are zero conflicts meaningful?** Necessary consistency check; mostly mechanically expected under sound interval containment, not compelling evidence of correct certification.

### Part C — Originality

**21. Is coarsest sufficient precision standard under another name?** Closely related to minimal sufficient information, robust verification radius, feature disclosure and quantization-robust classification; no exact food-specific equivalent identified.  
**22. Does minimum-query/DDID directly subsume it?** Not identical: those emphasize acquisition of unknown information; Stage 14 emphasizes how coarsely a known value can be published, but established information-design methods remain strong baselines.  
**23. Does interval robustness subsume it?** The mathematical core largely falls within generic robust-optimization/verification methods; the novel value must be domain framing or a demonstrable domain-specific advance.  
**24. Does cryptographic carbon verification solve this problem?** No direct equivalence found; it often proves claims without revealing underlying evidence rather than minimizing percentage granularity.  
**25. Does QUID make it obvious?** It supplies real relevance, but also makes the rounding operation itself nonnovel.  
**26. More than application?** Not yet convincingly established; the claimed exact trick is wrong, and the remaining synthesis looks incremental.  
**27. Meaningful methods contribution?** A plausible application-oriented contribution *after* corrected exact modeling and empirical distinction, not yet a strong new method.  
**28. Direct equivalent paper found?** No in this focused search, with explicit limits on completeness.  
**29. If none, still incremental?** Yes, possibly too incremental for a high bar; novelty 6/10. IEEE Access does not require groundbreaking novelty, but technical correctness is nonnegotiable.  
**30. Legitimate novel part?** Potentially the *operationally defined, empirically measured food-composition disclosure-precision requirement* with real QUID feasibility, not generic LP/convexity or quantization mathematics.

### Part D — Significance

**31. Is 93.9–95.4% meaningful?** Potentially, if sound and compared with simple baselines; current numbers are unverified for true interval robustness, and these are conditional rates.  
**32. Useful if QUID only applies to selected ranks?** Possibly, but simulated all-rank disclosure exaggerates feasible use; test legal availability and voluntary disclosure.  
**33. Does >80% retention at 5 pp strengthen practical story?** Yes as a provisional descriptive observation, but only after exact rerun and qualifying the fact that 5 pp is a sensitivity grid, not standard QUID.  
**34. Does it protect commercial information?** It plausibly reduces numeric precision disclosed; actual information leakage / value of confidentiality is not quantified, so don't claim proven privacy protection.  
**35. Is ingredient-production scope adequate?** Yes for a bounded methods study with truthful title/claims; no for whole-product climate superiority claims.  
**36. Is commercial label validation mandatory?** For strong practical deployment claims yes; for a carefully bounded theoretical/methods paper it may be a substantial advantage rather than logical necessity.  
**37. Are two sources enough for FYP?** Usually sufficient for a well-executed scoped FYP after mathematical repair and transparent limitations.  
**38. Enough for Q1/IEEE Access?** Not by themselves; external representativeness, empirical baselines, method advance, exactness and realistic labels need work.  
**39. Experiment most increasing significance?** Correct exact solver + a preregistered real commercial-label case study with actual disclosed QUID ranks, different factor uncertainty regimes and meaningful baseline comparisons.  
**40. Missing experiment most likely to cause rejection?** Fully sound re-evaluation of every interval certificate; without it, the central result is potentially false.

### Part E — Reproducibility

**41. Do hashes/protocols establish no retuning?** They establish internal package integrity only; external chronological attestation and full artifact provenance would make the sequence auditable.  
**42. Is A7.2 adequate?** It is a substantial reported improvement, but its own full clean rerun is pending; the standalone bundle is absent from this ZIP and does not validate the Stage-14 extension.  
**43. Is negative generic comparator sufficiently disclosed?** Yes, as a frank qualitative limitation; final manuscript should include direct comparator setup, measurements and code.  
**44. Are exclusions transparent?** Eligible-by-recipe audit is included, but raw parsing failures, detailed mapping-failure causes and bias analyses are missing.  
**45. What artifact is required?** A complete public/accessible hashed bundle with original workbook, FCID inputs where permitted, deterministic parsing and interval solvers, per-action proof/output records, independent generic reference oracle, environment lock and one-command full rerun.

## Final scientific recommendation

**Do not proceed to a 'novelty PASS' or journal drafting based on the current Stage-13 retention numbers.** First repair the exact rounded-interval certification and precision-grid definition, then run a blinded, reproducible reassessment on the same frozen development and external cases. The existing research question remains worth investigating; the present *claimed certificate theorem and evidence derived from it* must be treated as unproven and, in part, disproved.
