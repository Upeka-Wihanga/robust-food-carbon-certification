# Data provenance

## Supplied raw sources

The handoff contains three raw files. They passed the supplied SHA-256 manifest
verification and were structurally inspected without modification.

### Guan external recipe workbook

- Filename: `Carbon footprint and nutrition estimation of Chinese cuisines.xlsx`
- Size: 157,817 bytes
- SHA-256: `22b55adad2b463fcff60f486560c66468923323609371ddaa5b3d42ddd34b80b`
- Workbook sheets: Recipe, Greenhouse gas emission factors, Data_Source
- Expected local path: `data/raw/Carbon footprint and nutrition estimation of Chinese cuisines.xlsx`

### FCID/WWEIA source

- Filename: `Recipes_WWEIA_FCID_0510.csv`
- Size: 5,863,715 bytes
- SHA-256: `3689803e5ef099fd4831d1136dabba183bff5454fc998fa7d7b7da61cf766c56`
- Observed structure: 129,863 data rows plus one header row
- Expected local path: `data/raw/Recipes_WWEIA_FCID_0510.csv`

### dataFIELD source

- Filename: `dataFIELDv1.0.xlsx`
- Size: 1,357,202 bytes
- SHA-256: `a2e0c8a609c88e96d679799666c37e678b75f60050cdc2eeb3e8b2498e9d4759`
- Workbook sheets: DESCRIPTION, FCID linkages, literature entries,
  Pivot Table_GHG, Pivot Table_CED, PROXY def'ns, MassConv
- Expected local path: `data/raw/dataFIELDv1.0.xlsx`

Machine-readable details are in `data/manifests/source_files.json`.

## Local ingestion checkpoint

The source files were recovered from the documented local handoff archive:

`/mnt/c/Users/MFIXPRO/Documents/ChatGPT/FYP/Codex_Research_Handoff_v1.zip`

Only its three named `raw_data/` entries were copied to the ignored
`data/raw/` directory. All three local copies match both the SHA-256 values and
byte lengths above. The raw loader API accepts explicit paths and can enforce
these manifest identities before parsing.

### FCID/WWEIA schema inspection

- Encoding: UTF-8.
- Shape: 129,863 data rows and 11 columns.
- Columns: `Food_Code`, `Mod_Code`, `Ingredient_Num`, `FCID_Code`,
  `Cooked_Status`, `Food_Form`, `Cooking_Method`, `Commodity_Weight`,
  `CSFII_9498_IND`, `WWEIA_9904_IND`, and `WWEIA_0510_IND`.
- The source has identifiers and composition fields but no food-description
  or ingredient-description column.
- The composite (`Food_Code`, `Mod_Code`, `Ingredient_Num`) has no duplicates.
  Repetition of `Food_Code`, `FCID_Code`, and `Ingredient_Num` alone is
  expected in this recipe-component layout.
- Null counts are zero for `Food_Code`, `Mod_Code`, and `Ingredient_Num`; 40
  each for `FCID_Code`, `Cooked_Status`, `Food_Form`, `Cooking_Method`, and
  `Commodity_Weight`; and 90 for each survey indicator.

### dataFIELD schema inspection

- Sheets and used dimensions: `DESCRIPTION` (18 x 19), `FCID linkages`
  (1002 x 32), `literature entries` (1646 x 62), `Pivot Table_GHG`
  (335 x 20), `Pivot Table_CED` (274 x 18), `PROXY def'ns` (161 x 9), and
  `MassConv` (999 x 15).
- `FCID linkages` identifies commodities with `FCID_Code` and `FCID_Desc`.
  Its utilized factors are `MJ / kg` and `CO2 eq / kg`; associated fields
  include datapoint counts, averages, standard deviations, proxy-group means,
  and scaled standard deviations.
- `literature entries` contains food type/subtype, functional-unit and
  life-cycle-stage metadata, farm/processor/total values, and a
  `reported variance` field. GHG units are kg CO2e/kg and CED units are MJ/kg.
- The pivot sheets expose count, average, minimum, maximum, and standard
  deviation fields. There are no explicit lower/upper uncertainty-bound
  columns.
- The 354 substantive cached-value rows observed in `FCID linkages` have
  unique, nonmissing `FCID_Code` values. In its relevant GHG variability
  fields, proxy-group mean has 77 missing values; raw and scaled SD each have
  one. These are inspection facts, not a factor mapping.

### Guan workbook schema inspection

- Sheets and dimensions: `Recipe` (322 x 25), `Greenhouse gas emission
  factors` (429 x 5), and `Data_Source` (20 x 4).
- `Recipe` contains 320 nonempty recipe rows, eight cuisine labels, English and
  Chinese names, a serialized `Ingredient (g)` field, cooking metadata,
  production/post-farmgate/cooking/source-total carbon fields, and nutrition
  fields. It has no explicit recipe-ID column.
- English names have three duplicate occurrences across three duplicate
  groups; Chinese names have one duplicate occurrence in one group.
- Ingredient cells are all present. Of 320 serialized ingredient fields, 308
  parse as dictionaries and 12 do not. The 3,449 entries in parseable
  dictionaries contain no missing or nonnumeric quantities.
- The factor sheet has 428 nonempty observations and columns for category,
  ingredient, production, postharvest/storage/processing, and
  distribution/retailing factors in kg CO2e/kg. No relevant values are
  missing; ingredient names have two duplicate occurrences across two groups.
- These structural facts are relevant to later Guan61/Guan86 reconstruction,
  but no cohort has been selected here.

## Redistribution

Redistribution status is `UNKNOWN_REQUIRES_LICENSE_CHECK` for all three sources.
They are ignored by Git and are not duplicated under `research_archive/`.
Local possession is not evidence that redistribution is permitted.

Before public release, the project must establish source attribution, license
terms, permitted derived-fixture use, and lawful acquisition instructions.

## Missing derived provenance

The handoff does not contain the historical FCID/Guan pair manifests, factor
mappings, selected rank files, action results, or full Stage-20/22/24 CSVs.
These must not be regenerated under historical filenames without an explicit
`reconstructed_baseline` label and new provenance record.

