# Codex Research Handoff — READ THIS FIRST

This archive is an evidence-preserving handoff for the FYP repository migration.

## Purpose

The Codex workspace was empty. This archive supplies the raw source datasets and the research documents that are still recoverable in the current ChatGPT project context.

**Do not treat this archive as a complete copy of the historical implementation.** Several temporary Python scripts/results that were executed during earlier research stages are no longer mounted in the current runtime. They must not be silently reconstructed and then labelled as original historical code.

## What is genuine historical material here

- the three raw source datasets in `raw_data/`;
- the Stage-18 frozen protocol;
- the Stage-24 result report and tracker;
- independent review documents;
- the original/current research brief (`Pasted text.txt`);
- the SHA-256 provenance manifest generated for this handoff.

## Migration rule

1. Archive every supplied file unchanged first.
2. Verify every SHA-256 before migration.
3. Classify artifacts as `raw source`, `frozen research document`, `review evidence`, or `current reconstruction`.
4. If implementation code is reconstructed from a protocol/report, label it **reconstruction**, not **original migrated code**.
5. Do not change mathematical behavior in the same commit that establishes the reconstructed baseline.
6. Reconstructed behavior must be locked with regression fixtures derived from the frozen documents before refactoring.

Read `MISSING_ORIGINAL_ARTIFACTS.md` before writing code.
