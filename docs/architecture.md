# Architecture

## Provenance layers

The repository separates four artifact classes:

- `original_source`: exact supplied bytes, including raw inputs when locally
  available;
- `frozen_research_evidence`: protocols, reports, reviews, and recorded results;
- `reconstructed_baseline`: behavior recreated from frozen evidence and still
  requiring equivalence validation;
- `new_implementation`: later FYP functionality not claimed to be historical.

`research_archive/` contains preserved evidence and must not import or depend
on active code. Active documentation may interpret it but cannot silently edit
it.

## Research library

The planned `food_carbon_cert` package is divided by responsibility:

- `geometry`: ordered simplex, rank slabs, interval polytopes, and vertices;
- `certification`: robust bounds, structured results, and decision oracle;
- `disclosure`: intervals, QUID inverse components, and precision models;
- `uncertainty`: factor boxes, shared factors, and interval interpolation;
- `acquisition`: leakage-free policies, targeted factors, and costs;
- `evaluation`: metrics, node-aware bootstrap, and stability analyses;
- `data`: Guan, FCID, dataFIELD, and mapping pipelines.

These packages are currently scaffolds, not implemented algorithms.

## Experiment boundary

`experiments/` owns configuration loading, provenance verification,
deterministic execution, and result serialization. Mathematical functions
belong in `src/`; notebooks must not be the sole route to a published result.

## Result handling

Current generated output is ignored under `results/current/`. A result becomes
historical evidence only through an explicit freeze that records its input
hashes, configuration, environment, limitations, and relationship to earlier
results.

