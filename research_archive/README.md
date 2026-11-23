# Historical research evidence archive

This directory preserves supplied historical research evidence separately from
the reconstructed software baseline and future FYP implementation.

Files copied from the handoff are retained byte-for-byte and must not be
silently edited, normalized, renamed, or replaced. Corrections and later
interpretations belong in the active documentation, with an explicit reference
to the preserved source artifact.

Artifact labels used by this repository are:

- `original_source`: exact supplied historical bytes;
- `frozen_research_evidence`: frozen protocols, reports, results, and reviews;
- `reconstructed_baseline`: code recreated from frozen specifications but not
  yet validated as equivalent to the unavailable historical implementation;
- `new_implementation`: newly developed FYP code.

The raw datasets are not duplicated here. They remain outside Git pending
license and redistribution review and are identified by hashes in
`data/manifests/source_files.json`.

The repository's MIT license applies to repository software. It does not grant
redistribution rights for third-party datasets or archived third-party review
material where those rights have not been established.

