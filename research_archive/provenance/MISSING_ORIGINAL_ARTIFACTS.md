# Missing Original Artifacts

The following historical implementation artifacts are referenced by the research record but are **not present in this handoff** because their exact original bytes are not available in the current runtime.

- validated whole-interval oracle Python module;
- Stage-17/18 randomized LP comparison script;
- permanent four-corner false-certificate fixture with original numeric bounds;
- full corrected QUID inverse test fixture set;
- FCID/Guan pair manifests and derived action-result CSVs;
- Stage-20 matched 2x2 experiment scripts and frozen CSV outputs;
- Stage-22 information-frontier scripts and full response-surface CSVs;
- Stage-24 targeted-acquisition Python scripts and full bootstrap/subset-audit CSVs;
- the original portable reproduction ZIP produced in the earlier runtime;
- original dependency environment snapshot.

## Critical instruction

Do **not** infer that these artifacts never existed. The frozen research documents record that they were executed and reviewed. But because the exact files are unavailable now, any recreated implementation must be marked as a **reconstruction from frozen specifications/results**, not as an unchanged migration.

## Reconstruction acceptance rule

A reconstructed module can be promoted into the repository baseline only after:

1. its behavior is compared against every recoverable frozen numeric result;
2. permanent regression tests cover known historical defects;
3. input hashes and deterministic configurations are recorded;
4. any result that cannot be recovered exactly is listed as unresolved rather than guessed.
