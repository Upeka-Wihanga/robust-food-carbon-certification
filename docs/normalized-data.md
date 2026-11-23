# Normalized FCID and dataFIELD intermediate layer

This layer is a `reconstructed_baseline`. It does not recreate the unavailable
historical FCID100 selection, factor mapping, pair manifest, or experiment
outputs.

## Architecture

`verified raw source -> normalized table -> explicit mapping-policy audit`

Research selection, pair/action construction, and experiment-specific
uncertainty scenarios are deliberately downstream and are not implemented
here.

## FCID normalization

Recipe identity is the exact `(Food_Code, Mod_Code)` pair. Every source row is
retained in source order with its filename, CSV row number, and complete raw
values. `Ingredient_Num` is preserved and independently checked against the
one-based source order.

The FCID CSV has no ingredient-description field. Normalized ingredient
descriptions therefore remain `None` with status
`NOT_PRESENT_IN_FCID_SOURCE`; dataFIELD descriptions are not silently copied
into FCID records.

For a recipe whose `Commodity_Weight` values are all finite, nonnegative, and
have a positive total, unit-mass shares are calculated in source order:

`share_i = Commodity_Weight_i / sum(Commodity_Weight)`

Decimal arithmetic is used. To make the stored representation sum exactly to
one under finite decimal division, the final share is the deterministic
residual `1 - sum(previous shares)`. The original weights and their uncorrected
total remain present. A missing or invalid weight prevents normalization of
the whole recipe but does not remove any ingredient row.

Current verified-source diagnostics:

- 7,154 distinct `Food_Code` values;
- 12,069 `(Food_Code, Mod_Code)` recipes;
- 129,863 retained ingredient rows;
- ingredient-count distribution min/Q1/median/Q3/P95/max:
  1/4/10/15/26/55;
- 12,029 normalized recipes and 40 recipes with missing composition values;
- 40 recipes, containing 40 rows, with missing FCID commodity linkage;
- zero invalid ingredient-order sequences;
- 10,704 complete recipes whose uncorrected source total is not exactly 100;
- zero normalized unit-mass share-sum failures.

No correction toward a source total of 100 is applied. Division by each
recipe's observed positive total is the only mass normalization.

## dataFIELD factor observations

The `FCID linkages` sheet is loaded twice from the same verified workbook:
once with formulas and once with Excel's stored cached values. The loader does
not execute or recalculate Excel formulas.

Each nonblank FCID-linkage row retains:

- canonical string factor ID and original workbook identifier;
- description, weight basis, linkage source, gate, and proxy/category field;
- stored `CO2 eq / kg` value;
- observation count, mean, standard deviation, and scaled standard deviation;
- source workbook, sheet, row, formula-row values, and cached-row values.

The linkage sheet does not contain per-FCID minimum or maximum fields. Those
values remain explicitly `None`; category-level pivot minima/maxima are not
silently assigned to commodities.

Current verified-source diagnostics:

- 354 factor observations with 354 unique factor IDs;
- zero missing or non-finite factor values;
- one missing scaled SD, for FCID code `8602000000`;
- 645 blank/formatted worksheet rows retained in the table-level audit.

No uncertainty interval is derived here. The surviving frozen evidence names
1-SD and 2-SD boxes and describes Stage-24 midpoint interpolation, but it does
not recover a sufficiently complete source-to-interval construction rule to
recreate those historical scenarios without inference.

## Mapping-policy audit

The mapping API requires one of two explicit policies:

- `EXACT_ONLY` compares canonical FCID code strings only;
- `EXACT_PLUS_CONFIRMED_BABYFOOD_PARENT` gives exact matches precedence and
  then consults a literal 118-pair crosswalk verified against the official
  WWEIA-FCID 2005-2010 descriptions and commodity vocabulary.

The enhanced policy does not rewrite arbitrary terminal digits. The two
parentless exceptions (`3600225001` and `3700222501`), unknown terminal-`1`
codes, and the 10 terminal-`0` gaps remain unmapped. The original FCID code is
retained separately from the mapped parent code. Mapping records identify the
selected policy, provenance status, reason, and weight-basis warning.

**The baby-food parent policy is an evidence-backed reconstructed policy
introduced by this implementation. It is not claimed to reproduce unavailable
historical mapping code.**

Verified-corpus coverage is:

- `EXACT_ONLY`: 354 mapped and 130 unmapped unique codes; 127,360 mapped and
  2,503 unresolved ingredient rows; 11,608 recipes with complete factor
  coverage and 461 incomplete recipes.
- `EXACT_PLUS_CONFIRMED_BABYFOOD_PARENT`: 472 mapped and 12 unmapped unique
  codes; 129,711 mapped and 152 unresolved ingredient rows; 11,921 recipes
  with complete factor coverage and 148 incomplete recipes.
- Improvement: 118 codes, 2,351 ingredient rows, and 313 completely covered
  recipes.

Unresolved ingredient-row counts include the 40 rows whose source FCID code is
missing. Five mapped baby-food/base-parent pairs carry a weight-basis warning;
no conversion is applied.

## Stage-26 Guan reconstruction

The Stage-26 Guan substrate is a `RECOVERED_PROJECT_CONVENTION`, not recovered
historical source code. Ingredient dictionaries are parsed from their literal
workbook text. Quantities and their recipe total remain `Decimal` values for
the source five-percent classification:

`ingredient_weight >= Decimal("0.05") * parsed_recipe_total`

This exact comparison is required at the threshold: source `15.0 / 300.0` is
exactly five percent. It avoids the former binary-float total
`300.00000000000006`, which incorrectly treated the 15 g pork in Sanhe Rice
Dumplings as a minor ingredient. Other numerical optimization remains
floating-point; this correction is limited to source threshold classification.

The independently verified reconstruction has 320 source rows, 308 parseable
recipes, 61 eligible recipes across eight cuisines, and 222 all-within-cuisine
pairs. Sanhe Rice Dumplings fails when its exactly-five-percent pork receives
its published factor. Sweet Barbecue Pork remains excluded because its 15 g
sugar is below five percent of its actual 300.2 g parsed total. A fixed 15 g
cutoff is not used.

Stage-18 M2 is reconstructed downstream without changing cohort eligibility:
directly mapped positive factors use shared ±25% intervals, while unmapped
minor ingredient keys use the frozen positive-factor interval
`[1.145000, 4.763000]`. Identical normalized ingredient keys share one factor
interval across recipes.
