# Methodology

## Evidence-first reconstruction

This repository begins from frozen documents rather than an available original
implementation. The workflow is therefore:

1. preserve and hash supplied evidence;
2. record missing historical artifacts explicitly;
3. reconstruct one bounded component from frozen specifications;
4. compare it with every recoverable numerical result and defect case;
5. label it `reconstructed_baseline` until that comparison passes;
6. refactor only after behavior is locked by tests.

No reconstructed module may be described as unchanged historical source.

## Robust certification

The research record requires optimization over complete interval-constrained
ordered-composition polytopes. The Stage-14 review contains a counterexample in
which checking only disclosure-rectangle corners produces a false certificate.
The reconstructed oracle must retain this case permanently and must be checked
against an independent exact formulation on small instances.

## Disclosure inverse

The Stage-18 frozen protocol defines positive half-up inverse components for a
0.5-percentage-point branch below 5% and a 1-percentage-point branch at or above
5%. Only attainable lattice outputs contribute. Impossible components must be
absent rather than represented by degenerate points. Disconnected components
must not be silently replaced by an invalid interpretation.

## External data

Guan61 remains the primary source-reconstruction-selected external cohort in
the frozen protocol. Broader cohorts are sensitivity analyses. Nonzero
minor-ingredient scenarios M1–M3 must remain available alongside historical
M0; structural-zero treatment must not become the only supported model.

FCID/WWEIA and dataFIELD reconstruction must preserve the historical inclusion,
mapping, aggregation, uncertainty-scenario, pair, and policy rules when they
can be recovered. Missing rules must be recorded rather than inferred from
headline metrics.

## Evaluation

Repeated recipe and food pairs share endpoints and are not independent.
Dependence-aware recipe/endpoint-node resampling and leave-one-stratum analyses
must be reconstructed from evidence. Naive pair-level binomial intervals are
not an acceptable replacement.

## Reproducibility

Each future experiment should verify source hashes, load a frozen configuration,
use deterministic seeds, record dependency and environment metadata, write to
a dedicated results directory, and print a concise summary. Historical outputs
must never be overwritten silently.

