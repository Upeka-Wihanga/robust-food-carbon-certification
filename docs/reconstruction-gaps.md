# FCID/dataFIELD reconstruction gaps

## Scope and decision

This is an evidence audit of the historical FCID-to-dataFIELD mapping and
dataFIELD SD1/SD2 factor intervals. It does not change production mapping or
uncertainty behavior. The raw sources and frozen research evidence remain
unchanged.

The audit uses the verified FCID and dataFIELD sources described in
`docs/data-provenance.md`. Detailed row-level outputs are local, ignored
workbench artifacts:

- `workbench/experiments/reconstruction_audit/fcid_unmapped_code_audit.csv`
- `workbench/experiments/reconstruction_audit/candidate_mapping_rules.csv`
- `workbench/experiments/reconstruction_audit/candidate_sd_intervals.csv`
- `workbench/experiments/reconstruction_audit/terminal_1_official_audit.csv`
- `workbench/experiments/reconstruction_audit/terminal_0_official_audit.csv`
- `workbench/experiments/reconstruction_audit/datafield_variability_formula_patterns.csv`

This document contains aggregates only.

## Current evidence classification

### Recovered from project evidence

- Exact matching maps 354 of 484 unique nonmissing FCID codes and leaves 130
  unmapped: 120 ending in `1` and 10 ending in `0`.
- Frozen review evidence explicitly describes the historical factor-specific
  scenarios as dataFIELD **scaled-SD** one-SD and two-SD stress boxes, not
  confidence intervals. It also confirms SD2 nesting and shared factors for
  repeated commodity codes.
- Stage 24 says refinement must use the arithmetic midpoint of the actual
  frozen interval and reports 27 shifted FCID100 SD1 intervals and 100 shifted
  FCID100 SD2 intervals.
- The original FCID100 identities, factor mapping, interval table, and
  source-to-interval implementation remain unavailable.

### Recovered from external authoritative documentation

The U.S. EPA/JIFSAN WWEIA-FCID 2005-2010 download index and its three reference
tables were retrieved on 2026-11-23. The local copies remain ignored pending a
licensing and redistribution review.

- Source index:
  `https://fcid.foodrisk.org/dbc/`
- FCID Commodity Code Descriptions:
  `https://fcid.foodrisk.org/dbc/csv2014Q4/FCID_Code_Description.csv`
- FCID Commodity Vocabulary:
  `https://fcid.foodrisk.org/dbc/csv2014Q4/Commodity_Vocabulary.csv`
- Updated FCID Code Lookup:
  `https://fcid.foodrisk.org/dbc/csv2014Q4/FCID_Code_Update_0510.csv`

The official descriptions establish the following:

- All 120 terminal-`1` source codes exist in the official current vocabulary.
- For 118 codes, the corresponding terminal-`0` code also exists. In every
  case the terminal-`1` description explicitly identifies a baby-food or
  baby-food/infant-formula variant of the terminal-`0` base description.
- All 118 official parents have a dataFIELD factor. They are unique, so this
  crosswalk creates no mapping collisions.
- Official weight-basis text is identical for 113 pairs. Five pairs differ in
  punctuation, wording, singular/plural form, inclusion of juice, or truncated
  source text. These require explicit review before assuming identical
  per-mass semantics.
- `3600225001`, “Milk, sugar (lactose)-baby food/infant formula”, has no
  official terminal-`0` parent.
- `3700222501`, “Milk, human”, is not described as a baby-food variant and has
  no official terminal-`0` parent.
- The Updated FCID Code Lookup contains all 120 source codes and the 118
  parents as separate current codes. It corroborates code identity but does
  not itself instruct users to inherit a parent's environmental factor.

The 10 terminal-`0` unmapped codes are:

- `101084000` — Celeriac
- `401104000` — Chrysanthemum, garland
- `1100310000` — Quince
- `1302136000` — Currant
- `2302358000` — Starfruit
- `2401351000` — Spanish lime
- `2403361000` — Sugar apple
- `3100048000` — Beef, kidney
- `3400294000` — Pork, kidney
- `3500342000` — Sheep, kidney

All 10 exist in the official FCID references. None appears by exact code or
exact official description in the dataFIELD workbook, and none has an
explicit code-level proxy/category assignment there. Assigning any dataFIELD
group would therefore require a new semantic mapping decision.

### Recovered from workbook formulas

The hash-verified `dataFIELDv1.0.xlsx` was inspected with formulas preserved
and by reading `xl/worksheets/sheet2.xml`. The XML stores many formulas as
shared formulas; their master formulas agree with the formulas expanded by
openpyxl.

For GHG variability, the relevant columns are:

- `P`: whether the source is a direct database value or a proxy.
- `Q`: source observation count.
- `R`: commodity/source GHG mean.
- `S`: commodity/source GHG standard deviation.
- `AB`: final variability basis (`DIRECT`, a manually or formula-selected
  proxy group, or `no var`).
- `AC`: direct count `Q`, or `DCOUNT` over the selected proxy group.
- `AD`: blank for `DIRECT`, otherwise the selected proxy-group mean.
- `AE`: `S` for `DIRECT`, otherwise the selected proxy-group sample SD.
- `AF`: scaled SD.

The symbolic scaled-SD formula is exactly:

`scaled_sd = S` when `AB == "DIRECT"`

`scaled_sd = (AE / AD) * R` otherwise

Thus a grouped/proxy scaled SD preserves the proxy group's coefficient of
variation and applies it to the commodity mean. It is a source variability
statistic, not an interval and not a confidence bound.

The basis-selection formula uses a five-observation threshold:

`basis = K` for a proxy source with at least five observations;

`basis = DIRECT` for a direct source with at least five observations;

`basis = "need group"` otherwise.

The workbook then contains manually selected group literals where this generic
formula is insufficient. All 163 rows with fewer than five GHG observations
have a literal final basis: a selected group or `no var`. Across all 354
factor rows, 66 use `DIRECT`, 277 use a group, and 11 use `no var`.

The utilized final GHG factor is:

`G = R * H + U`

where `H` is the weight/mass-conversion factor and `U` is an additional
processing input. Neither `H` nor `U` appears in the `AF` formula. The same
`AF` formula is used for direct, proxy, processing-gate, processing-adjusted,
and mass-converted rows; gate selection changes the source statistics, not the
final scaling expression. There are 343 formula-based `AF` cells, 10 manually
fixed zeros, and one blank.

For `8602000000` (“Water, indirect, all sources”), the workbook records zero
source observations, zero source mean and SD, weight-conversion factor zero,
final GHG factor zero, and a manually assigned `no var` basis. The `AF` cell
is intentionally blank in both the worksheet XML and openpyxl view. The
missing value is therefore not a failed proxy calculation: it is a
no-source-variance, zero-factor row for which the author omitted the scaled-SD
formula/value. The historical downstream treatment remains undocumented.

### Strong inference

- A semantic `babyfood -> terminal-0 parent commodity` crosswalk is implemented
  for the 118 confirmed pairs as an optional reconstructed mapping policy. The
  official metadata proves the parent relationship, and every parent has one
  dataFIELD factor. This does not prove that the unavailable historical
  pipeline applied that factor, and the five weight-basis wording differences
  remain explicit warnings.
- `center = G` is **STRONGLY_INFERRED** because `G` is the workbook's utilized
  factor and the historical scenario perturbed dataFIELD factors, but no
  surviving interval-construction equation states the center.
- `width = k * scaled_sd` for `k in {1,2}` is
  **STRONGLY_INFERRED** from the explicit use of scaled SDs and the names
  one-SD/two-SD boxes. No surviving code or factor-level numeric example
  states the endpoint equation.
- `upper = G + k * scaled_sd` is **STRONGLY_INFERRED** from the same box
  terminology, but not explicitly recovered.

### Still unresolved

- `lower = max(0, G - k * scaled_sd)` is **UNRESOLVED**. Stage 24 proves that
  some frozen intervals had midpoints shifted away from a prior assumed
  center, and zero truncation is compatible with that fact, but neither the
  archive nor workbook states `max(0, ...)`.
- Treatment of the missing `scaled_sd` for `8602000000` is **UNRESOLVED**.
  Fixed `[0,0]` is source-compatible, but it is not documented as the
  historical downstream rule.
- The workbook's `scaled_sd` does not include `H` or `U`, while the final
  factor `G` does. The evidence does not say whether historical interval code
  used `AF` directly, transformed it again, or handled converted/processed
  factors specially.
- No historical FCID100 factor subset can be identified without reconstructing
  selection by guesswork.
- Consequently, the complete SD1/SD2 endpoint construction is not yet
  recoverable without assumptions.

### Prohibited assumption

- Do not represent the authoritative baby-food parent relationship as proof of
  the unavailable historical factor-mapping implementation.
- Do not force the two parentless terminal-`1` codes or the 10 terminal-`0`
  codes into a nearest semantic/category match.
- Do not assume identical weight bases where the official text differs.
- Do not infer zero truncation solely from the Stage-24 shifted-midpoint
  counts.
- Do not silently replace the missing scaled SD with zero, raw SD, an imputed
  value, or row omission.
- Do not tune an interval formula or an invented FCID100 subset to reproduce
  27/100 shifted intervals.

## Evidence trail

The relevant surviving textual evidence is:

- `docs/methodology.md:40-43` requires historical mapping and
  uncertainty-scenario rules to be preserved when recoverable and missing
  rules to be recorded rather than inferred from headline metrics.
- `docs/data-provenance.md:68-81` identifies the dataFIELD linkage and
  variability fields, records unique linkage codes and one missing raw/scaled
  SD, and states that the workbook has no explicit lower/upper interval
  columns.
- `docs/normalized-data.md:84-101` defines the current exact-code-only audit
  and records the unresolved terminal-digit pattern.
- `docs/poc-results.md:75-88` records that the original mappings, panels,
  manifests, and action files are unavailable and that mapping rules must be
  recovered or explicitly re-specified before results are run.
- `docs/implementation-context.md:12-13` and
  `docs/research-scope.md:25-28` require one shared factor for identical
  commodity codes in scenarios using the shared-factor model.
- `research_archive/reviews/Stage17_Independent_Blind_Review.md:293-303`
  identifies missing factor-mapping provenance and asks for a deterministic
  source-to-output recipe, mapping checksums, and reconstruction filters.
- `research_archive/reviews/Stage14_Independent_Blind_Review.md:185-186`
  says repeated standardized commodities must share one factor and identifies
  correct mappings as an assumption of the interval analysis.
- `research_archive/frozen_research/Pasted text.txt:123-129` confirms shared
  commodity factors and reports SD1-to-SD2 nesting in the examined outputs.
- `research_archive/frozen_research/Pasted text.txt:175-180` explicitly calls
  the dataFIELD values **scaled SDs**, describes SD1/SD2 as factor-specific
  variability stress sets, and warns that the resulting one- and two-SD boxes
  are not confidence intervals.
- `research_archive/frozen_research/Stage24_Targeted_Information_Acquisition_Report.md:14-21`
  requires refinement toward the arithmetic midpoint of each actual frozen
  `[l,u]` interval and reports 27 shifted SD1 intervals and 100 shifted SD2
  intervals.
- `research_archive/frozen_research/Progress_Tracker_After_Stage24.md:1-6`
  confirms that the midpoint correction changed 91 SD1 and 267 SD2 decisions.

No frozen document or review states a terminal-digit mapping transformation.
No archived text gives a complete source-to-SD1/SD2 lower/upper formula,
zero-truncation rule, or missing-scaled-SD rule.

The workbook adds the following source-level facts:

- `DESCRIPTION`, rows 3, 13, 17, and 18, says that dataFIELD links production
  factors to 2005-2010 FCID commodity codes, that `FCID linkages` contains the
  utilized factors and proxy assignments, and that `MassConv` handles mass
  conversion.
- In `FCID linkages`, the utilized GHG factor formula is `R * H + U`.
- The scaled-SD formula uses the raw SD for a direct record and
  `proxy-group SD / proxy-group mean * food GHG mean` for a proxy/group
  record.
- There are no factor lower/upper columns, relevant comments, or workbook
  metadata defining SD1/SD2 boxes.
- Code `8602000000` has utilized factor zero, raw SD zero, missing scaled SD,
  and a `no var` marker. A fixed zero interval is a reasonable interpretation,
  but no surviving evidence proves that this was the historical handling.

The remaining frozen Stage-18 protocol and the two `High Model` review files
contain general requirements about QUID repair, mapping quality, and factor
uncertainty calibration, but no additional mapping transformation or SD-bound
construction. This negative search result includes the terms `FCID code`,
`linkage`, `commodity`, `mapping`, `normalization`, `final digit`, `terminal
digit`, `suffix`, `dataFIELD`, `WWEIA`, `SD1`, `SD2`, `standard deviation`,
`scaled SD`, `variance`, `lower`, `upper`, `midpoint`, `truncation`,
`nonnegative`, and one-/two-sigma variants.

## FCID mapping audit

### Recovered facts

- The normalized FCID data contains 484 unique nonmissing commodity codes.
- Exact canonical-code matching maps 354 and leaves 130 unmapped.
- The 130 unmapped codes account for 2,463 ingredient rows/recipe
  occurrences. Per-code frequency ranges from 1 to 198.
- Final digits are highly concentrated: 120 codes end in `1`; 10 end in `0`.
- Of the 120 terminal-`1` codes, 118 have an available dataFIELD factor with
  the same prefix and terminal `0`. The other two do not.
- Those 118 candidates produce no one-to-many cases, no many-to-one
  collisions, and no conflict with an existing exact mapping.
- The terminal-`1` source rows use multiple `Cooked_Status` values (`1`, `2`,
  and `9`), so that field does not independently establish a terminal-digit
  rule.
- The 130 codes have nearest same-length dataFIELD codes at Hamming distance
  one for 125 codes, distance two for four, and distance three for one.
- The unmapped codes do not occur in the inspected `MassConv` FCID-code or
  FCID-code-basis fields.

### Candidate rules

1. **Exact first, then terminal `1 -> 0`: SEMANTICALLY SUPPORTED,
   HISTORICAL USE UNVERIFIED.**
   It resolves 118 of 130 codes, leaves 12, has zero one-to-many and
   many-to-one collisions, and raises complete-factor recipe coverage from
   11,608 to 11,921 (+313). Official descriptions confirm all 118 as
   baby-food/infant-formula variants of the corresponding base commodities.
   No surviving project source proves that the historical factor pipeline
   inherited the parent factor.

2. **Exact first, then replace any terminal digit with `0`: UNSAFE.**
   It resolves the same 118 codes and no additional cases. It has no observed
   collision in this dataset, but it generalizes beyond the observed pattern
   without semantic evidence.

3. **Drop the terminal digit: CONTRADICTED.**
   It resolves none of the 130 codes.

4. **Use any same-length Hamming-distance-one factor: UNSAFE.**
   It resolves 125 codes and leaves five, but creates four one-to-many cases
   and one many-to-one target shared by two source codes. Complete-factor
   recipe coverage would increase by 316.

5. **Use the nearest numeric factor code: UNSAFE.**
   It resolves all 130 by construction, with three one-to-many cases and two
   many-to-one targets involving four source codes. Complete-factor recipe
   coverage would increase by 419, but numeric proximity supplies no commodity
   semantics.

### Mapping decision

The terminal `1 -> 0` relationship is now authoritative for 118 baby-food
variant/base-commodity pairs. It is defensible as a new, explicitly documented
reconstructed mapping policy, subject to preserving the five weight-basis text
differences. It is not recovered evidence of the unavailable historical
factor-mapping implementation. The implementation exposes it only through the
explicit `EXACT_PLUS_CONFIRMED_BABYFOOD_PARENT` policy; `EXACT_ONLY` remains
available and is the default.

**The baby-food parent policy is an evidence-backed reconstructed policy
introduced by this implementation. It is not claimed to reproduce unavailable
historical mapping code.**

## SD1/SD2 uncertainty audit

### Evidence levels

**EXPLICITLY DOCUMENTED**

- The historical scenarios use dataFIELD scaled SDs as factor-specific
  variability stress scales.
- The scenarios are called one-SD and two-SD boxes, are not confidence
  intervals, and SD2 is wider/nested relative to SD1.
- A commodity factor is shared across foods where the same mapped commodity is
  present.
- Stage-24 partial refinement shrinks the actual frozen interval toward its
  arithmetic midpoint.

**CONSISTENT BUT NOT PROVEN**

- Using the utilized GHG factor `G` as center and scaled SD `s` as radius,
  `[G - k*s, G + k*s]` for `k` equal to one or two, is consistent with the
  names “SD1” and “SD2”, but the archive never states this formula.
- Using `[max(0, G - k*s), G + k*s]` is consistent with nonnegative production
  factors and could create the shifted arithmetic midpoints reported at
  Stage 24. No numeric interval example or text proves zero truncation or
  proves that the upper endpoint remained symmetric after lower truncation.
- Treating the zero-factor, zero-raw-SD, `no var` record with missing scaled SD
  as fixed `[0,0]` is source-compatible but not proven to be historical.

**SPECULATIVE**

- Substituting raw SD for scaled SD conflicts with the surviving description
  of the historical stress sets.
- Centering on an intermediate/direct mean rather than the utilized GHG factor
  has no archived support.
- Imputing the missing scaled SD, silently dropping its factor, or applying a
  generic fallback width has no archived support.

No formula is classified as **IMPLIED BY NUMERIC EXAMPLE**, because no
surviving factor-level historical interval example is available.

### Consistency probes

As a nonproduction probe, the candidate
`[max(0, center - k*SD), center + k*SD]` was evaluated over all 354 normalized
factor observations. The number of intervals whose midpoint shifts because
the candidate lower endpoint is truncated is:

- utilized factor with scaled SD: 68 for SD1 and 228 for SD2;
- utilized factor with raw SD: 32 and 132, over the 296 usable raw-SD rows;
- utilized factor with the proxy/group SD field: 89 and 204;
- direct/intermediate mean with scaled SD: 95 and 300;
- direct/intermediate mean with raw SD: 45 and 193;
- direct/intermediate mean with proxy/group SD: 112 and 261.

None equals the historical Stage-24 counts of 27 and 100 on the full
354-factor universe. This does not refute the scaled-SD/truncation candidate:
the historical counts concern the unavailable FCID100 frozen factor subset,
whose membership and interval file are missing. The direction of the counts
(more shifts for SD2 than SD1) is compatible, but the historical headline
counts cannot validate or select a formula.

### SD decision

The complete SD1/SD2 construction is not recoverable from the surviving
evidence. Missing elements are the exact center, endpoint formula, lower-bound
treatment, missing-scaled-SD treatment, and the frozen FCID100 factor subset.
No candidate formula should enter production code until those are recovered or
a new scenario is explicitly specified as a reconstructed, nonhistorical
baseline.

## Research controls

Recovered facts may be used directly. Evidence-backed inferences may guide
targeted provenance searches or preregistered sensitivity designs, but must be
labelled as inferences. Unresolved gaps must remain visible in downstream
provenance. It is prohibited to:

- infer a code mapping solely from terminal-digit or nearest-code proximity;
- choose a mapping or SD formula by tuning it to historical headline counts;
- represent a guessed rule as the historical FCID100/dataFIELD pipeline;
- silently impute the missing scaled SD or silently discard affected records;
- describe SD stress boxes as confidence or probability intervals.
