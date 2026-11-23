# PoC Mapping Guide for Codex

This guide maps the ten PoCs from the research brief to evidence currently included in this handoff.

| PoC | Current evidence | Migration status |
|---|---|---|
| 1 Robust certification oracle | Research brief + Stage-17/18/24 descriptions | Original code missing; reconstruction required |
| 2 Four-corner regression | Stage-17 review / brief describes historical failure | Numeric fixture original missing |
| 3 QUID inverse | Stage-18 frozen protocol specifies branch/lattice repair | Reconstruct with threshold tests; label reconstructed |
| 4 Guan validation | Raw Guan workbook + Stage-18 protocol + Stage-24 report | Data present; derived cohort/pair manifests missing |
| 5 FCID + dataFIELD | Raw FCID CSV + raw dataFIELD workbook + Stage-24 report | Data present; original pipeline/mappings missing |
| 6 Selectable policies | Stage-24 report / brief | Policy code and frozen rank files missing |
| 7 Dependence-aware evaluation | Stage-24 report/tracker | Bootstrap implementation and frozen replicate files missing |
| 8 Stage 20 matched uncertainty | Research brief/reviews only | Historical outputs/scripts missing |
| 9 Stage 22 frontier | Stage-24 report describes corrections/supersession | Historical outputs/scripts missing |
| 10 Stage 24 targeted acquisition | Stage-24 report + tracker | Headline frozen metrics present; code/CSV originals missing |

## Important

Codex should first create an **evidence inventory** and repository skeleton. Do not start by recreating all ten PoCs in one pass.
