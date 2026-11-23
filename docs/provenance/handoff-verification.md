# Handoff verification

- Verification time: 2026-11-23 13:21:23 +05:30 (Asia/Colombo)
- Manifest: `handoff/provenance/PROVENANCE_MANIFEST.json`
- Git commit at verification: `a55947a5b228d8f6086a66be0d0f8b71458ebd3a`
- Files checked: 14
- SHA-256 and byte-length result: **PASS**
- Mismatches or missing files: none

Every file listed in the supplied provenance manifest was recomputed from the
extracted handoff. All 14 files matched both the recorded SHA-256 digest and
the recorded byte length. The raw datasets were read only for verification and
structural inspection.

The supplied ZIP contained one wrapper directory. It was extracted and that
wrapper was flattened into the requested `handoff/` import layout without
changing file contents. The original ZIP remains ignored and unmodified.

