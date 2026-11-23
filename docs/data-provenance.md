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

