# Normalized FCID and dataFIELD intermediate layer

This layer is a `reconstructed_baseline`. It does not recreate the unavailable
historical FCID100 selection, factor mapping, pair manifest, or experiment
outputs.

## Architecture

`verified raw source -> normalized table -> exact-code mapping audit`

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

## Exact-code mapping audit

Mapping compares canonical FCID code strings only. It does not pad, truncate,
or replace code digits, and duplicate candidate rows remain ambiguous.

Current verified-source audit:

- 484 unique nonmissing FCID ingredient codes;
- 354 directly mapped;
- 130 unmapped;
- zero codes with multiple candidates;
- zero ambiguous mappings;
- zero mapped codes with missing/non-finite factor values;
- 40 FCID ingredient rows with no source commodity code.

Of the 130 exact-code unmapped identifiers, 120 end in `1`; many have a
dataFIELD identifier differing only in the final digit. No such relationship
is applied because the historical code-normalization rule is unavailable.
