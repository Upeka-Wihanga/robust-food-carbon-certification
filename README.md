# Robust Food-Carbon Certification under Incomplete Ingredient Disclosure

**Information Sufficiency and Observation-Aware Sequential Acquisition**

> This repository is currently being initialized from the validated research PoCs and frozen experimental evidence. The original exploratory research artifacts are preserved separately from the reconstructed software baseline. Observation-aware sequential acquisition and the final application are under active development.

## Research problem

Food ingredient lists disclose order but often omit exact shares. This research
asks when the available information is nevertheless sufficient to guarantee
the direction of a pairwise modeled greenhouse-gas comparison, and what
additional share or factor information is most valuable when it is not.

The method has three possible outcomes: certify food A as lower, certify food B
as lower, or abstain. Abstention is required whenever the modeled difference
can change sign over the complete declared uncertainty set.

## Environmental scope

The current model covers normalized ingredient mass and upstream
ingredient-production greenhouse-gas factors. It is not a whole-product life
cycle assessment and does not currently model processing, packaging,
distribution, retail, cooking, supplier-specific sourcing, or every legal form
of commercial QUID disclosure.

## Current status

This milestone establishes an auditable repository and preserves the supplied
evidence. It does **not** reconstruct or implement the mathematical oracle.

Ten research PoCs are historically reported: robust certification, the
four-corner regression, the corrected disclosure inverse, Guan validation,
FCID/dataFIELD processing, selectable disclosure policies, dependence-aware
evaluation, matched uncertainty attribution, the information frontier, and
targeted information acquisition. Their current evidence and migration status
are recorded in [docs/poc-results.md](docs/poc-results.md).

The original historical Python implementation and several derived CSVs are
not available. Any later recreation from the frozen protocols will be labelled
`reconstructed_baseline` until validated against recoverable metrics and
regression cases.

## Repository architecture

- `research_archive/`: immutable historical evidence and provenance records;
- `src/food_carbon_cert/`: future research library, separated by geometry,
  certification, disclosure, uncertainty, acquisition, evaluation, and data;
- `experiments/`: deterministic command-line experiment orchestration;
- `tests/`: unit, permanent regression, and property/metamorphic tests;
- `configs/`: versioned dataset, uncertainty, policy, and experiment settings;
- `data/`: manifests and local placement for uncommitted raw sources;
- `results/`: deliberately frozen historical results and ignored current runs;
- `docs/`: supervisor-facing scope, methods, provenance, status, and roadmap.

See [docs/architecture.md](docs/architecture.md) for the provenance boundary
between historical evidence and future code.

## Archived evidence

The repository preserves supplied Stage-18 and Stage-24 documents, progress
tracking, four independent review files, handoff metadata, and the original
provenance manifest. All 14 handoff files passed SHA-256 and byte-length
verification. Raw datasets are not duplicated into the archive or committed.

## Datasets

Three raw sources were supplied:

- `Carbon footprint and nutrition estimation of Chinese cuisines.xlsx`;
- `Recipes_WWEIA_FCID_0510.csv`;
- `dataFIELDv1.0.xlsx`.

Their exact hashes and sizes are in
[`data/manifests/source_files.json`](data/manifests/source_files.json). Until
redistribution rights are confirmed, another researcher must lawfully obtain
the files and place them under `data/raw/` with the exact listed filenames.
These paths are ignored by Git.

## Planned test strategy

The reconstructed baseline will require independently checked unit tests for
ordered-simplex geometry, complete interval constraints, shared-factor bounds,
sign classification, disclosure inversion, aggregation, and factor
interpolation. Permanent regressions will cover the four-corner false
certificate, the 4.5%/5% inverse boundary, the truncated-interval midpoint, and
near-zero abstention. Property tests will check uncertainty-set containment and
shared-factor invariants.

No such mathematical tests are claimed to be implemented in this bootstrap.

## Reproducibility approach

Future experiment entry points will load versioned configurations, verify
input hashes, use deterministic seeds, write to dedicated output directories,
record environment metadata, and compare recoverable frozen metrics. A
reconstructed result will not be promoted merely because it appears plausible.

The intended command shape is:

```text
python -m experiments.<experiment_name>.run
```

No experiment runner exists yet, and the local Python interpreter is currently
unresolved.

## Roadmap

The next phase is a narrow reconstruction of the validated robust oracle with
the historical false-certificate case locked first. Subsequent work will
reconstruct disclosure handling, uncertainty models, datasets, policies,
dependence-aware evaluation, and Stage-20/22/24 experiments in separate,
reviewable commits.

Observation-aware sequential acquisition, genuinely held-out evaluation,
realistic observation and acquisition-cost models, broader commercial
validation, and a production application remain active research tasks. See
[docs/roadmap.md](docs/roadmap.md).

## License and data rights

Repository software is licensed under the MIT License. Third-party datasets
and archived evidence may have separate rights; no redistribution permission
is inferred from local availability.


