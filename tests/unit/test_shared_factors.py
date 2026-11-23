from __future__ import annotations

from itertools import product

import numpy as np

from food_carbon_cert.uncertainty import (
    FactorInterval,
    aggregate_factor_difference,
    factor_box_extrema,
    fixed_composition_bounds,
)


def test_direct_endpoint_selection_matches_factor_corner_enumeration() -> None:
    coefficients = {"positive": 0.7, "negative": -0.2, "zero": 0.0}
    factors = {
        "positive": FactorInterval(1.0, 3.0),
        "negative": FactorInterval(2.0, 5.0),
        "zero": FactorInterval(10.0, 20.0),
    }
    direct = factor_box_extrema(coefficients, factors)
    corners = [
        sum(
            coefficients[code] * value
            for code, value in zip(factors, corner, strict=True)
        )
        for corner in product(*[(item.lower, item.upper) for item in factors.values()])
    ]
    np.testing.assert_allclose(direct, (min(corners), max(corners)))


def test_identical_codes_are_aggregated_as_one_shared_factor() -> None:
    coefficients = aggregate_factor_difference(
        [0.6, 0.4], ["shared", "a"], [0.6, 0.4], ["shared", "b"]
    )
    assert coefficients["shared"] == 0.0

    bounds = fixed_composition_bounds(
        [1.0], ["shared"], [1.0], ["shared"], {"shared": FactorInterval(1.0, 9.0)}
    )
    assert bounds == (0.0, 0.0)
