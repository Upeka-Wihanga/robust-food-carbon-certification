"""Whole-polytope robust endpoint calculation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import inf

import numpy as np
from numpy.typing import ArrayLike

from food_carbon_cert.uncertainty.factor_box import FactorInterval
from food_carbon_cert.uncertainty.shared_factors import fixed_composition_bounds


@dataclass(frozen=True, slots=True)
class RobustBounds:
    """Extrema and audit counts for a complete pairwise uncertainty set."""

    lower: float
    upper: float
    evaluated_vertex_pairs: int


def calculate_robust_bounds(
    vertices_a: ArrayLike,
    commodity_codes_a: Sequence[str],
    vertices_b: ArrayLike,
    commodity_codes_b: Sequence[str],
    factor_intervals: Mapping[str, FactorInterval],
) -> RobustBounds:
    """Evaluate robust bounds over every required composition-vertex pair."""

    array_a = np.asarray(vertices_a, dtype=np.float64)
    array_b = np.asarray(vertices_b, dtype=np.float64)
    if array_a.ndim != 2 or array_b.ndim != 2:
        raise ValueError("composition vertices must be two-dimensional arrays")
    if array_a.shape[0] == 0 or array_b.shape[0] == 0:
        raise ValueError("each food must have at least one feasible vertex")
    if array_a.shape[1] != len(commodity_codes_a):
        raise ValueError("food A vertex width does not match its commodity codes")
    if array_b.shape[1] != len(commodity_codes_b):
        raise ValueError("food B vertex width does not match its commodity codes")

    global_lower = inf
    global_upper = -inf
    evaluated_pairs = 0
    for vertex_a in array_a:
        for vertex_b in array_b:
            pair_lower, pair_upper = fixed_composition_bounds(
                vertex_a,
                commodity_codes_a,
                vertex_b,
                commodity_codes_b,
                factor_intervals,
            )
            global_lower = min(global_lower, pair_lower)
            global_upper = max(global_upper, pair_upper)
            evaluated_pairs += 1

    return RobustBounds(global_lower, global_upper, evaluated_pairs)
