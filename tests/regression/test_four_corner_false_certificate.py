from __future__ import annotations

import numpy as np

from food_carbon_cert.certification import Decision, FoodUncertainty, certify_pair
from food_carbon_cert.geometry import is_ordered_simplex_point
from food_carbon_cert.uncertainty import FactorInterval, fixed_composition_bounds


def _stage14_factors() -> dict[str, FactorInterval]:
    means = {
        "a1": 0.01,
        "a2": 0.01,
        "a3": 1.00,
        "b1": 0.564,
        "b2": 0.564,
    }
    return {code: FactorInterval.around(mean, 0.25) for code, mean in means.items()}


def test_complete_polytope_prevents_stage14_false_certificate() -> None:
    factors = _stage14_factors()
    food_a = FoodUncertainty(("a1", "a2", "a3"), 2, 0.325, 0.335)
    food_b = FoodUncertainty(("b1", "b2"), 1, 0.745, 0.755)
    interior_a = np.asarray([1.0 / 3.0] * 3)
    interior_b = np.asarray([0.75, 0.25])

    assert is_ordered_simplex_point(interior_a)
    assert 0.325 <= interior_a[1] <= 0.335
    _, interior_upper = fixed_composition_bounds(
        interior_a,
        food_a.commodity_codes,
        interior_b,
        food_b.commodity_codes,
        factors,
    )
    assert np.isclose(interior_upper, 0.002, rtol=0.0, atol=1e-12)

    result = certify_pair(food_a, food_b, factors)
    assert result.upper_bound > 0.0
    assert np.isclose(result.upper_bound, 0.002, rtol=0.0, atol=1e-12)
    assert result.decision is Decision.ABSTAIN


def test_historical_outer_percentage_cases_are_all_negative() -> None:
    factors = _stage14_factors()
    upper_bounds = []
    for share_a in (0.325, 0.335):
        for share_b in (0.745, 0.755):
            result = certify_pair(
                FoodUncertainty(("a1", "a2", "a3"), 2, share_a, share_a),
                FoodUncertainty(("b1", "b2"), 1, share_b, share_b),
                factors,
            )
            upper_bounds.append(result.upper_bound)
            assert result.decision is Decision.A_LOWER

    assert max(upper_bounds) < 0.0
    assert np.isclose(max(upper_bounds), -0.002125, rtol=0.0, atol=1e-12)
