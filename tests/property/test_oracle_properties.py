from __future__ import annotations

import numpy as np

from food_carbon_cert.certification import Decision, FoodUncertainty, certify_pair
from food_carbon_cert.uncertainty import FactorInterval


def _random_case(
    rng: np.random.Generator,
) -> tuple[FoodUncertainty, FoodUncertainty, dict[str, FactorInterval]]:
    count_a = int(rng.integers(2, 6))
    count_b = int(rng.integers(2, 6))
    rank_a = int(rng.integers(1, count_a + 1))
    rank_b = int(rng.integers(1, count_b + 1))

    def interval(count: int, rank: int) -> tuple[float, float]:
        feasible_lower = 1.0 / count if rank == 1 else 0.0
        feasible_upper = 1.0 / rank
        center = float(rng.uniform(feasible_lower, feasible_upper))
        radius = 0.2 * (feasible_upper - feasible_lower)
        return max(feasible_lower, center - radius), min(
            feasible_upper, center + radius
        )

    lower_a, upper_a = interval(count_a, rank_a)
    lower_b, upper_b = interval(count_b, rank_b)
    codes_a = tuple(f"a{index}" for index in range(count_a))
    codes_b = tuple(
        codes_a[index] if index < min(count_a, count_b, 2) else f"b{index}"
        for index in range(count_b)
    )
    factors = {
        code: FactorInterval(float(rng.uniform(0.1, 3.0)), float(rng.uniform(3.1, 7.0)))
        for code in set(codes_a) | set(codes_b)
    }
    return (
        FoodUncertainty(codes_a, rank_a, lower_a, upper_a),
        FoodUncertainty(codes_b, rank_b, lower_b, upper_b),
        factors,
    )


def _narrow(food: FoodUncertainty) -> FoodUncertainty:
    center = (food.lower_share + food.upper_share) / 2.0
    half_width = (food.upper_share - food.lower_share) / 4.0
    return FoodUncertainty(
        food.commodity_codes,
        food.rank,
        center - half_width,
        center + half_width,
    )


def test_nested_disclosure_and_swap_properties() -> None:
    rng = np.random.default_rng(20261123)
    for _ in range(60):
        food_a, food_b, factors = _random_case(rng)
        narrow_a = _narrow(food_a)
        narrow_b = _narrow(food_b)
        broad = certify_pair(food_a, food_b, factors)
        narrow = certify_pair(narrow_a, narrow_b, factors)

        assert broad.lower_bound <= narrow.lower_bound + 1e-11
        assert broad.upper_bound >= narrow.upper_bound - 1e-11
        if broad.decision is Decision.A_LOWER:
            assert narrow.decision is Decision.A_LOWER
        if broad.decision is Decision.B_LOWER:
            assert narrow.decision is Decision.B_LOWER
        if narrow.decision is Decision.A_LOWER:
            assert broad.decision is not Decision.B_LOWER
        if narrow.decision is Decision.B_LOWER:
            assert broad.decision is not Decision.A_LOWER

        exact_a_share = (narrow_a.lower_share + narrow_a.upper_share) / 2.0
        exact_b_share = (narrow_b.lower_share + narrow_b.upper_share) / 2.0
        exact = certify_pair(
            FoodUncertainty(
                food_a.commodity_codes, food_a.rank, exact_a_share, exact_a_share
            ),
            FoodUncertainty(
                food_b.commodity_codes, food_b.rank, exact_b_share, exact_b_share
            ),
            factors,
        )
        assert narrow.lower_bound <= exact.lower_bound + 1e-11
        assert narrow.upper_bound >= exact.upper_bound - 1e-11

        swapped = certify_pair(food_b, food_a, factors)
        assert np.isclose(swapped.lower_bound, -broad.upper_bound, atol=1e-11)
        assert np.isclose(swapped.upper_bound, -broad.lower_bound, atol=1e-11)
        expected_swap = {
            Decision.A_LOWER: Decision.B_LOWER,
            Decision.B_LOWER: Decision.A_LOWER,
            Decision.ABSTAIN: Decision.ABSTAIN,
        }[broad.decision]
        assert swapped.decision is expected_swap


def test_expanding_factor_uncertainty_cannot_create_contradictory_certificate() -> None:
    rng = np.random.default_rng(8102026)
    for _ in range(40):
        food_a, food_b, _ = _random_case(rng)
        codes = set(food_a.commodity_codes) | set(food_b.commodity_codes)
        centers = {code: float(rng.uniform(0.2, 5.0)) for code in codes}
        narrow_factors = {
            code: FactorInterval(center * 0.95, center * 1.05)
            for code, center in centers.items()
        }
        broad_factors = {
            code: FactorInterval(center * 0.7, center * 1.3)
            for code, center in centers.items()
        }
        narrow = certify_pair(food_a, food_b, narrow_factors)
        broad = certify_pair(food_a, food_b, broad_factors)
        assert broad.lower_bound <= narrow.lower_bound + 1e-11
        assert broad.upper_bound >= narrow.upper_bound - 1e-11
        if narrow.decision is Decision.A_LOWER:
            assert broad.decision is not Decision.B_LOWER
        if narrow.decision is Decision.B_LOWER:
            assert broad.decision is not Decision.A_LOWER


def test_shared_factor_cancels_for_identical_foods() -> None:
    food = FoodUncertainty(("shared", "shared"), 1, 0.5, 1.0)
    result = certify_pair(food, food, {"shared": FactorInterval(0.1, 10.0)})
    assert result.lower_bound == 0.0
    assert result.upper_bound == 0.0
    assert result.decision is Decision.ABSTAIN
