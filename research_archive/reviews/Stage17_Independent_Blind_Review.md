# Stage 17 Blind Reviewer Response

**Subject:** *Disclosure Sufficiency for Robust Food-Carbon Certification: Exact Interval Verification and Cross-Dataset Evidence*  
**Review date:** 23 November 2026  
**Basis:** Frozen reviewer package, review instructions in `00_START_HERE.md`, fresh source/code/result audit, and independent targeted prior-work search.  
**Review stance:** Adversarial but technically fair; no previous internal scores adopted.

## Verdict

**REVISE**. The corrected oracle and the measured retention phenomenon support a strong bounded Final Year Project, but the present evidence does **not** yet meet a demanding IEEE Access/Q1 applied-methods novelty-and-significance gate. REVISE does not mean that the verified calculations failed; it means that model-to-reality validity, generalizability, actionable value, and differentiation from routine robustness sensitivity have not yet been sufficiently demonstrated.

## Independent scores

| Dimension | Score | Rationale |
|---|---:|---|
| **Novelty** | **6.0 / 10** | Specific empirical question and cross-source measurements are distinguishable, but the exact geometry, robust sign testing and nested input-radius sensitivity are established mathematical techniques; no clear generic algorithmic innovation. |
| **Mathematical soundness** | **8.0 / 10** | The corrected simplex-slab vertex theorem and robust bounds are valid under the declared model; fresh independent tests agree. Some rounding-boundary and numerical-hardening details remain. |
| **Methodological soundness** | **5.5 / 10** | Heavy Guan reconstruction selection, structural zero emissions for minor ingredients, repeated observations, heuristic uncertainty boxes, and an existence-based query metric limit inference and practical interpretation. |
| **FYP suitability** | **8.0 / 10** | A precise, substantial, reproducible-at-output-level technical investigation with a defensible bounded conclusion and feasible next steps. |
| **IEEE Access / Q1-style publication potential** | **5.0 / 10** | Plausible applied-paper direction, not yet a submission-ready or Q1-level distinct contribution, particularly absent realistic independent validation and baselines. |
| **Reproducibility** | **6.0 / 10** | Complete outputs, hashes, source code, tests and Guan workbook are available; the raw FCID/dataFIELD files and frozen upstream manifests are absent, with nonportable absolute paths in rerun scripts. |

## Hard findings

- **Direct prior equivalent found? NO.** I found no direct equivalent in the *targeted searches performed*, not proof of exhaustive priority. Clark et al. (2022), Mohamed & Alosman (2026), and decision-dependent information-discovery work are substantial near prior art.
- **Valid mathematical counterexample found? NO — not against the corrected whole-interval oracle.** The supplied earlier four-corner counterexample correctly changes from false certification to abstention. I found a narrower **implementation defect in the QUID inverse:** for a valid published share of `0.045`, the routine includes a degenerate component at `0.05`, which cannot yield a 4.5% publication under the declared >=5%/1-pp branch. This over-approximates the inverse and is *conservative*, not a discovered false-positive certificate. It must nevertheless be fixed and rerun before calling the inverse exact.
- **Archive integrity:** all 28 packet files match their frozen SHA-256 manifest entries.
- **Headline arithmetic:** independently counted all 7,594 FCID and 24,656 Guan action rows and matched the report's exact/QUID/action/pair counts at 10%, 25%, 50% uncertainty; no recorded action-level containment or direction violation. The nested radius output includes 604 FCID and 2,210 Guan exactly certifying actions at ±25%; all six radii are monotone in recorded rows.
- **Independent fresh mathematical check:** 55 newly generated cases, using a separately written SciPy linear-programming and factor-corner comparator with some boundary/point slabs, yielded 0 direction/bound mismatches (maximum endpoint error `3.55e-15`). This supplements rather than substitutes for full proof and numerical boundary tests.
- **Critical Guan audit:** source workbook has **320 recipe rows; 308 parse; 61 pass the frozen reconstruction filter**. All 61 eligible recipes have individually under-5%-share ingredients treated as zero production impact. Their total excluded mass averages **11.345%** of recipe mass (median **10.063%**, maximum **32%**); **49/61** eligible recipes exclude more than 5% of total recipe mass. The source paper itself acknowledges excluding spices/condiments below 5%; reproducing the convention does not establish robustness of the result to this assumption.
- **Dependent evidence:** the 222 Guan observations are all within-cuisine pairs from 61 recipes across eight cuisines; rank actions and pairs share recipes, and are not 24,656 or 222 independent samples.

### Primary result, correctly framed

| ±25% factor boxes | FCID | Guan |
|---|---:|---:|
| Exactly certifying actions | 604 / 7,594 | 2,210 / 24,656 |
| QUID-style certifying actions | 568 / 7,594 (7.48% all) | 2,109 / 24,656 (8.55% all) |
| Conditional action retention | 94.04% | 95.43% |
| QUID-style certifiable pairs | 28 / 100 (28.00%) | 107 / 222 (48.20%) |
| Conditional pair retention | 96.55% | 99.07% |
| Nested ±1 pp action survival among exact actions | 77.81% | 88.37% |
| Nested ±10 pp action survival among exact actions | 46.85% | 58.51% |

The strong retention result is **conditional on an exact one-rank-per-food action already certifying**. It is not a claim that most food pairs are certifiable, or that a consumer knows which action to choose. These are modeled ingredient-production signs under specified uncertainty sets, not full commercial LCA guarantees.

## Strongest rejection argument

The study risks presenting an unsurprising instance of the established principle that sufficiently strong robust decisions survive modest widening of input uncertainty as a novel science result. Conditional retention is calculated on the *selected subset that already certifies exactly*, whereas all-action QUID coverage is only 7–9%. The purported external replication depends on just 61/308 parseable Guan recipes and models an average 11.3% of their ingredient mass as zero-emission; it does not show the phenomenon persists with realistic minor-ingredient factors, broader recipes, actual available product disclosures, or an implementable disclosure-selection policy. This is a **significance and validity problem**, not a disproval of the mathematical solver.

## Strongest acceptance argument

The research clearly separates probabilistic environmental estimation from **worst-case sign certification over all ordered ingredient compositions and shared commodity-factor boxes**. Following withdrawal of an unsound shortcut, the entire published-interval uncertainty set is handled by valid vertex extrema; the study quantifies certificate survival across two independent recipe sources and multiple nested precision radii. The retained negative generic-method comparator and cautious QUID-style wording improve the credibility of a bounded applied empirical contribution.

## Most important experiment still missing

**A preregistered external robustness reanalysis that removes the structural-zero ingredient artifact and broadens the validation set.** First repeat Guan with realistic nonzero or interval factors for under-5%-share ingredients (including missing-factor sensitivity) while preserving the original 61-recipe set for direct paired comparison; then assess a much broader, predeclared source cohort and report pair/recipe/cuisine-clustered uncertainty. Include at least one actually selectable fixed/query-budget action policy compared with simple baselines. A genuine label-availability case study is the strongest subsequent real-world validation.

## Most important theoretical issue still missing

A formally specified and tested **end-to-end precision-disclosure certificate** covering the true inverse image of the rounding mechanism at every threshold/tie, any disconnected components, numerical sign margins, and the monotone certificate feasibility frontier. The simplex-slab robust verifier itself is sound under the stated assumptions, but the current implementation's 4.5%-publication edge case shows that the claimed *exact* rounded inverse deserves an explicit proof, reference implementation and adversarial tests. Completing a continuous `r*` is useful for a precision-frontier claim, but is not a prerequisite for publishing the explicitly discrete radius results.

## Required changes before supervisor approval

1. Reframe as a **measured applied disclosure-sufficiency phenomenon**, explicitly distinguishing empirical from algorithmic novelty and accepting the negative A7 comparator.
2. Fix the QUID inverse branch-lattice/empty-interval defect; rerun the published-value results, counterexample and threshold tests, and disclose any changes.
3. Add a sensitivity experiment for Guan's under-5% zero-factor convention and quantify the 61/320 retention and correlated pair/action observations.
4. Report absolute pair coverage alongside conditional retention in every headline and clarify *existence of some rank action* versus a feasible policy selecting that action.
5. Document all factor-box assumptions, dataset restrictions, rounding scope and loss of real-world/QUID guarantees. Present an explicit stage-specific experiment plan, not a claim that the journal novelty gate has passed.

## Required changes before journal submission

1. Complete an independent dataset/source-to-output rerun with releaseable scripts, frozen pair/action manifests, documented hashes, environment and licensed download instructions.
2. Demonstrate robustness to realistic/nonzero minor-ingredient factors, commodity mapping alternatives, source-reconstruction thresholds and uncertainty-box calibrations.
3. Supply predeclared recipe- or cuisine-clustered intervals and heterogeneity analyses; avoid pseudoreplication and action-weighted overgeneralization.
4. Benchmark against relevant, well-chosen **simple robustness and disclosure policies**, not only a straw-man factor-sign enumerator: order-only screening, rank-selection heuristics, coarse fixed-grid approaches, and, when appropriate, calibrated-estimate comparisons, with clear distinction in guarantee type.
5. Add empirical disclosure feasibility: verify QUID applicability and actually obtainable share ranges for a representative commercial-label sample, or label the setting transparently as hypothetical voluntary disclosures.
6. Formalize and test rounding-inverse edge cases and strict numerical boundary handling; optionally compute per-action/pair tolerance frontiers `r*` to move beyond six sample points.
7. Narrow the introduction and novelty claim to the empirically supported result; publish uncertainty-aware limitations, zero-factor sensitivity and the negative A7 comparator as essential context.

## Answers to Questions 1–70

### A. Mathematical validity

**1. Is the interval-constrained ordered-composition polytope correctly defined?**  
Yes. The intersection of the ordered simplex with a rank-share slab is the correct feasible set given ordered shares summing to one. This correctness is conditional on the actual label order, complete ingredient model and normalization being valid.

**2. Is the vertex construction complete for a simplex intersected by a rank slab?**  
Yes. The ordered simplex is the convex hull of prefix-uniform vectors; any new vertex of a hyperplane cut arises on an original edge, and the slab intersection also retains original vertices. The implementation enumerates all simplex vertex pairs rather than only adjacent entries.

**3. Is the shared-factor robust upper/lower formulation internally correct?**  
Yes, for independently boxed commodity factors that are **shared** across both foods where commodity codes coincide. Maximizing/minimizing the linear factor dot product gives `m·d ± rho·|d|`.

**4. Do convex-maximum/concave-minimum arguments justify vertex pairs?**  
Yes. The upper function is convex in composition and attains a maximum at some extreme point of the product polytope; the lower is concave and attains its minimum at an extreme point. A proof should explicitly identify these extrema and the Cartesian-product vertex set.

**5. Does it avoid the old four-corner counterexample?**  
Yes. Reproduced: old upper `-0.002125` (false A), corrected upper `+0.002000` (ABSTAIN).

**6. Can I construct a new counterexample to the corrected interval oracle?**  
No valid counterexample found. The model is supported by the vertex argument and fresh 55-case independent LP/sign enumeration. This is not exhaustive verification.

**7. Is the QUID inverse correct near 5%?**  
Mostly conservative but **not an exact inverse in all cases**. For `published=0.045`, code adds an impossible zero-width 5%-share component because it does not check if 4.5% is an allowed 1-pp branch output; it also accepts intervals with `lo > hi` within a tolerance. Fix this before submission.

**8. Are union components handled conservatively?**  
Yes for certificate soundness: all component vertices are pooled, so the result is checked against their union (and possibly a larger convex-hull uncertainty, which remains conservative for convex maxima/concave minima). In the current 4.5% case the extra singleton only increases abstention risk.

**9. Are strict sign certificates at zero handled appropriately?**  
The specification uses strict `U<0`/`L>0`, and implementation adds a `1e-10` tolerance that conservatively abstains near zero. An explicitly scaled/magnitude-aware tolerance or interval arithmetic is preferable for a rigorous journal implementation.

**10. Is the nested radius family genuinely nested?**  
Yes. `I_r(t)=[t-r,t+r]` intersected with a fixed feasible rank range is nested in `r`.

**11. Does pair-level survival behave monotonically?**  
Yes. Each certifying action can only become less certain with larger nested sets; the logical OR over actions is consequently nonincreasing. All stored action and pair counts satisfy monotonicity.

**12. Is continuous `r*` essential?**  
No for discrete radius comparisons. It is important if the claimed headline is the *exact minimum required precision* or a continuous distribution of tolerances; those claims cannot be made from the six tested radii alone.

**13. Any hidden mapping/zero-factor issue invalidating robust bounds?**  
No demonstrated algebraic invalidation **under the declared mappings**; but Guan assigns zero-production-factor synthetic codes to all individual under-5% ingredients, even though allowed counterfactual share compositions may place substantial weight on them. This weakens environmental meaning and external replication, and requires sensitivity testing.

**14. Is the point solver suitable as support despite weak novelty?**  
Yes. The negative A7 generic multiparametric-basis comparator shows no meaningful overall computational edge, but the point solver remains a valid supporting technique.

**15. What additional mathematical verification?**  
Formal theorem proof with degeneracies; property-based tests at all prefix breakpoints, slab endpoints, disconnected inverse unions and threshold ties; exact/interval-arithmetic boundary checks; and metamorphic invariants for commodity aggregation and rank monotonicity.

### B. Correctness evidence

**16. Are 220 randomized LP/sign cases enough?**  
Encouraging, not sufficient alone for production-grade correctness. They use small `n` and at most five commodities, so targeted large/degenerate and adversarial cases are needed. My additional 55 differently generated cases agree.

**17. Were critical breakpoints and boundaries covered?**  
The 220 random cases do not systematically enumerate every reciprocal boundary. The 356 point-geometry comparison cases explicitly include breakpoints and cell midpoints, but full interval and threshold tests are still needed.

**18. Does point compatibility strengthen trust?**  
Yes, it checks the corrected method reduces appropriately to the known point formulation, although the old implementation is also part of the same project and is not a fully independent external source.

**19. Is the old counterexample a regression?**  
Yes. The exact counterexample is implemented and the recorded corrected result agrees with its stated endpoints.

**20. Are floating-point tolerances adequately controlled?**  
Sufficient for exploratory positive-margin cases, not a complete numerical proof. Fixed absolute tolerance can be scale dependent, and degenerate near-empty inverse intervals can pass tolerance checks.

**21. Does earlier exact-rational work materially help?**  
Conceptually yes for sign certification, but it was not bundled as a standalone end-to-end Stage-17 exact-rational rerun; it should not be cited as proving every current rounded-interval result.

**22. Most likely remaining implementation failure?**  
Threshold/tie inverse bugs and ill-conditioned near-zero classifications, followed by inconsistent commodity-factor mapping/reconstruction across datasets; I observed the concrete 4.5% inverse edge case.

### C. Empirical evidence

**23. Are FCID denominators and actions appropriate?**  
Yes for the *frozen panel*: one action queries one rank in each food; `7,594` is an action denominator, `100` a pair denominator. Panel sampling and source-reconstruction details are not independently reconstructable from this ZIP.

**24. Is Guan genuinely external?**  
It is an independently originated recipe/factor workbook, so yes in that constrained sense. It is not independent ground-truth retail carbon certification or a commercially verified QUID-label dataset.

**25. Does frozen 61-recipe selection prevent post-hoc selection?**  
It reduces result-aware tuning if the freeze predates the corrected rerun, as documented. It does **not** remove selection bias from the eligibility rule itself or prove absence of earlier tuning.

**26. Is 61/308 a serious selection risk?**  
**Yes.** Source has 320 rows, 308 parseable, only 61 included (`19.8%` of parseable, `19.1%` of all). Exclusions correlated with factor mapping/reconstruction compatibility may change the observed coverage and radius distribution.

**27. How should 222 Guan pairs be interpreted?**  
As descriptive within-cuisine comparisons from only 61 recipes. Overlapping recipes induce a network/dependence structure; 222 is not an independent-sample size.

**28. Are action-level observations too correlated for primary evidence?**  
Yes as a statistical unit. Actions from the same pair and recipe reuse factors/composition and are strongly dependent; action retention is a useful engineering descriptor, not 24,656 independent replications.

**29. Is pair-level coverage more meaningful?**  
Yes, while still dependent through shared recipes. The headline must report both `28/100` and `107/222` and identify the existential all-rank search behind the latter.

**30. Should recipe/cuisine/group clustering be used?**  
Yes. Use cluster/bootstrap procedures that resample **recipes or cuisines** and recompute the induced pair summaries, ideally with transparent design-based caveats; a naive binomial interval over 222 pairs is not adequate.

**31. Is FCID's 28/100 coverage practically meaningful?**  
A potentially useful proof-of-possibility, but modest for a universal consumer tool, especially because the certifying action may not be known beforehand or legally obtainable.

**32. Is Guan's 107/222 coverage meaningful?**  
More promising as *within-cuisine* potential, but heavily affected by sample selection and zero-impact minor ingredients; do not extrapolate to all foods or labels.

**33. Is 94–95% conditional retention meaningful with 7–9% all-action coverage?**  
Yes as a statement about the robustness of *already-certifying* actions. It cannot be presented as a 94–95% chance of certifying a random action or random pair.

**34. Does the nested curve add beyond QUID retention?**  
Yes. It identifies how survival degrades as a common radius widens and separates a specific rounded disclosure rule from a general numerical precision test. It remains a routine sensitivity construction unless tied to a substantive real-world insight or benchmark.

**35. Is cross-source radius difference informative?**  
Descriptively yes: Guan survives wider radii better than FCID in this sample. Without comparable source construction, factor mapping, recipe clusters and baseline margin distributions, the reason is not identified.

**36. Is uncertainty sensitivity convincing?**  
It is internally coherent: the exact and QUID counts fall as factor boxes widen. It establishes robustness **to these three assumed widths**, not empirical coverage of true commodity uncertainty.

**37. Are ±10/25/50% adequate?**  
Useful descriptive perturbations, insufficient as calibrated uncertainty. Explore factor-specific evidence-based ranges, correlated factors, geographic sourcing and interval asymmetry.

**38. Does Guan's under-5% convention limit external validity?**  
**Substantially.** All 61 eligible recipes contain excluded under-5% ingredients, which together average `11.345%` of their mass; 49/61 exclude over 5% combined. Synthetic zero-factor rank codes remain zero even if a feasible alternative composition gives them more share.

**39. What further statistical analysis is essential?**  
Report recipe-level and cuisine-level denominator tables, selection-flow counts, clustered intervals, effect sizes, threshold-margin distributions and strata by source/ingredient count. Include alternative-mapping/zero-factor sensitivity and fixed-policy success.

**40. Does corrected rerun repair the prior empirical evidence?**  
It repairs the stated *mathematical-certification shortcut* and reproduces the aggregate patterns under the declared model. It does not repair dataset representativeness, factor validity or the minor inverse implementation artifact.

### D. Originality

**41. Does Clark et al. supply the same contribution?**  
No direct robust pairwise sign/precision-frontier result identified, but Clark already establishes ingredient-order composition inference and food environmental impact estimation at scale. A broad 'ingredient-list carbon estimation' novelty claim is untenable.

**42. Does the 2026 calibrated screening LCA paper narrow novelty?**  
**Yes.** It uses ingredient declarations for large-scale environmental screening with calibrated uncertainty and held-out validation. Stage 17's distinct claim must be a different kind of **worst-case feasible-set guarantee** and its information-granularity effect, not 'uncertainty-aware food impact.'

**43. Do DDID methods directly subsume Stage 17?**  
They subsume broad language about optimally acquiring information for robust decisions, but not automatically the particular empirical food-disclosure-radius measurements. Do not claim a new general information-discovery algorithm.

**44. Is nested radius standard robust sensitivity?**  
Yes in mathematical structure. Its value lies in what it reveals for an externally meaningful dataset and disclosure mechanism, not in inventing sensitivity to uncertainty-set expansion.

**45. Is 'coarsest sufficient information' already general?**  
Yes as a general concept across robust optimization and information design. Only a narrowly contextualized empirical characterization may be novel.

**46. Is exact interval verification a meaningful method?**  
It is a valid and useful implementation/derivation for this constrained setting, but vertex enumeration over cut simplices is generic polyhedral optimization rather than persuasive standalone algorithmic novelty.

**47. Is external replicated retention substantive?**  
Potentially, but its novelty is **empirical** and its significance currently depends too much on a selective, zero-factor external set without inferential uncertainty or practical action selection.

**48. Is the integrated combination distinct?**  
Specific and recognizably different as a complete experimental question, yes. A distinctive combination is not by itself proof of a scientifically *important* advance.

**49. Direct equivalent paper or algorithm?**  
No direct paper found in the targeted 2026 search combining all elements; the core optimization algorithm is nonetheless an instance of established techniques. Absence in a focused search is not proof of novelty priority.

**50. Is it still too incremental for IEEE Access/Q1?**  
**Currently yes**, on the evidence provided. A routine robust computation plus correlated retention measurements under simplified emissions and hypothetical label availability falls below a demanding novelty/significance bar.

**51. One novelty claim I would allow:**  
"We quantify, on two independently sourced recipe datasets, the survival of worst-case pairwise ingredient-production-carbon sign certificates as one ingredient share per food is disclosed at progressively coarser, explicitly bounded precision under ordered-composition and shared box-factor uncertainty." This is a scoped empirical claim, not a priority assertion.

**52. One novelty claim I would reject:**  
"We introduce the first exact, privacy-preserving, QUID-compliant method to guarantee which commercial food product has the lower full carbon footprint using minimal disclosure." Exactness/priority/privacy/QUID availability and full-LCA reach are not all supported.

### E. Practical significance

**53. Is 'QUID-style' sufficiently honest?**  
Yes, provided the word *simulation* accompanies the result and no specific disclosure is called legally compulsory without product-level assessment.

**54. Is real QUID availability essential before publication?**  
Not for a clearly bounded methodological feasibility study, but it is important for strong applied impact and essential for claims about deployment from existing retail labels.

**55. Would a commercial-label case study help materially?**  
Yes. It would quantify how many rank shares actually appear and whether the chosen rank-pair information can be obtained, making the existential certificate useful.

**56. Is ingredient-production GHG worthwhile as a bounded target?**  
Yes for transparent upstream comparisons. It cannot justify full brand/product superiority, since processing, cooking, packaging and distribution can reverse rankings.

**57. Is a guaranteed sign certificate useful versus calibrated intervals?**  
Yes when a cautious decision genuinely needs a worst-case guarantee under *credible uncertainty sets*. Calibrated prediction intervals answer a different statistical question, often with broader coverage; compare objectives fairly.

**58. Is abstention a feature or low coverage?**  
Both. Abstention avoids unsupported certainty and is the mathematically appropriate outcome, but high abstention constrains usefulness. Report its operational cost/coverage tradeoff.

**59. Is existence of some action useful without a policy?**  
Limited. It is an oracle-style attainable upper bound on coverage, not the success rate of an actual label-reading or query workflow.

**60. Would deployment require voluntary disclosure?**  
Often yes, unless the needed rank is genuinely published or obtained from another valid source; the recipe studies cannot establish retail availability.

**61. Strongest use case under present evidence?**  
A **voluntary manufacturer–auditor screening protocol** that requests an agreed rounded rank percentage, then issues a conservative upstream-production comparison only when the declared factor and composition assumptions warrant it.

**62. Which practical claim is overstated?**  
Treating 94–95% conditional action retention as typical real-world certification performance or calling hypothetical recipe-rank outputs QUID-available commercial product comparisons.

### F. Reproducibility

**63. Are files sufficient to audit Stage 16?**  
Sufficient for output-level recount, math-code review and fresh small synthetic tests; **not sufficient for a clean full FCID source-to-output rerun** because upstream input artifacts are absent.

**64. Can headline numbers be recomputed from CSVs?**  
**Yes.** I independently recounted action classifications, unique pairs, retention and all six radius survivals from the supplied CSVs, and every reported primary number matched.

**65. Is incomplete continuous `r*` a reproducibility issue?**  
Not for the explicitly reported discrete radius curve. It is an uncompleted analysis, not a hidden missing dependency, as long as no exact per-action `r*` claim is made.

**66. Is negative A7 comparator preserved transparently?**  
Yes. It reports matching geometry/endpoints and essentially identical end-to-end runtime for a generic multiparametric basis comparator, directly weakening the earlier method-originality argument.

**67. What inputs are missing for a full rerun?**  
Original FCID CSV and dataFIELD workbook, the upstream A4 frozen action/pair manifest and corresponding importable script layout, plus a fully specified environment and provenance for all factor mappings. Hashes are supplied for two raw files but not their contents.

**68. Is Guan workbook inclusion useful?**  
**Yes.** I independently re-parsed its 320 recipe rows, reproduced 308 parseable/61 eligible, and quantified its zero-factor-share exclusion. This materially strengthened the review.

**69. Is omission of licensed FCID/dataFIELD data acceptable?**  
Potentially for a blind-review package if redistribution restrictions are real and clear lawful acquisition steps are supplied. Licensing restrictions do not excuse absence of a deterministic public source-to-output recipe and manifest.

**70. What single artifact most improves reproducibility?**  
A self-contained, versioned **one-command reproduction bundle** with exact source acquisition/licensing guidance, pinned dependencies, the frozen A4 pair/action manifest, source and factor-mapping checksums, all reconstruction filters and the corrected inverse-model tests.

## Final 2–3 sentence summary

The corrected whole-interval robust certificate is mathematically defensible within its model, and the action/pair retention results are internally consistent and independently countable; they make this a strong, bounded Final Year Project. However, the new headline is primarily an empirical sensitivity characterization rather than a novel optimization method, and the small selected Guan subset, structural zero factors, correlated observations and absence of a realistic disclosure-selection workflow prevent a convincing IEEE Access/Q1 significance claim today. **Verdict: REVISE; proceed with the FYP under narrowed claims and complete a genuinely external, nonzero-factor, policy-aware validation before asserting journal-level readiness.**

## External sources independently consulted

1. Clark et al., *Estimating the environmental impacts of 57,000 food products*, PNAS (2022): https://pmc.ncbi.nlm.nih.gov/articles/PMC9388151/
2. Mohamed and Alosman, *Calibrated screening-level life cycle assessment of food products from ingredient data*, *Sustainable Production and Consumption* (2026): https://www.sciencedirect.com/science/article/pii/S2352550926001776
3. Vayanos, Georghiou and Yu, *Robust Optimization with Decision-Dependent Information Discovery*, *Management Science*: https://pubsonline.informs.org/doi/10.1287/mnsc.2021.00160
4. Paradiso et al., *Exact and Approximate Schemes for Robust Optimization Problems with Decision-Dependent Information Discovery*, *INFORMS Journal on Computing*: https://pubsonline.informs.org/doi/10.1287/ijoc.2023.0290
5. Chen, Goerigk and Poss, *The robust selection problem with information discovery* (2026): https://www.sciencedirect.com/science/article/pii/S0166218X25007231
6. Food Safety Authority of Ireland, *Quantitative Ingredient Declaration (QUID)*: https://www.fsai.ie/business-advice/labelling/labelling-general-labelling/quid
7. European Commission, QUID Notice: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52017XC1121(01)
8. Guan et al., *Carbon footprint and nutrition estimation of Chinese eight cuisines*: https://www.oaepublish.com/articles/cf.2025.118

**Audit note:** The archive evidence concerns source-derived model behavior, while literature findings are an independently consulted external comparison. None of the percentages should be interpreted as empirically calibrated uncertainty coverage for actual commercial products.
