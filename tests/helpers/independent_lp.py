"""Independent LP/factor-corner comparator for small test instances."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np
from scipy.optimize import linprog

from food_carbon_cert.certification import Decision, FoodUncertainty
from food_carbon_cert.uncertainty import FactorInterval


@dataclass(frozen=True, slots=True)
class IndependentBounds:
    """Bounds returned by the independent test-only LP comparator."""

    lower: float
    upper: float


def _constraint_matrices(
    food_a: FoodUncertainty, food_b: FoodUncertainty
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    count_a = food_a.ingredient_count
    count_b = food_b.ingredient_count
    variable_count = count_a + count_b
    inequalities: list[np.ndarray] = []
    limits: list[float] = []

    for offset, food in ((0, food_a), (count_a, food_b)):
        for index in range(food.ingredient_count - 1):
            row = np.zeros(variable_count)
            row[offset + index + 1] = 1.0
            row[offset + index] = -1.0
            inequalities.append(row)
            limits.append(0.0)

        upper_row = np.zeros(variable_count)
        upper_row[offset + food.rank - 1] = 1.0
        inequalities.append(upper_row)
        limits.append(food.upper_share)

        lower_row = np.zeros(variable_count)
        lower_row[offset + food.rank - 1] = -1.0
        inequalities.append(lower_row)
        limits.append(-food.lower_share)

    equalities = np.zeros((2, variable_count))
    equalities[0, :count_a] = 1.0
    equalities[1, count_a:] = 1.0
    return (
        np.vstack(inequalities),
        np.asarray(limits),
        equalities,
        np.ones(2),
    )


def independent_lp_bounds(
    food_a: FoodUncertainty,
    food_b: FoodUncertainty,
    factor_intervals: dict[str, FactorInterval],
) -> IndependentBounds:
    """Enumerate factor corners and optimize compositions using SciPy LPs."""

    codes = sorted(set(food_a.commodity_codes) | set(food_b.commodity_codes))
    endpoints = [
        tuple(
            dict.fromkeys((factor_intervals[code].lower, factor_intervals[code].upper))
        )
        for code in codes
    ]
    a_ub, b_ub, a_eq, b_eq = _constraint_matrices(food_a, food_b)
    variable_count = food_a.ingredient_count + food_b.ingredient_count
    global_lower = np.inf
    global_upper = -np.inf

    for values in product(*endpoints):
        factor_values = dict(zip(codes, values, strict=True))
        objective = np.asarray(
            [factor_values[code] for code in food_a.commodity_codes]
            + [-factor_values[code] for code in food_b.commodity_codes]
        )
        minimum = linprog(
            objective,
            A_ub=a_ub,
            b_ub=b_ub,
            A_eq=a_eq,
            b_eq=b_eq,
            bounds=[(0.0, None)] * variable_count,
            method="highs",
        )
        maximum = linprog(
            -objective,
            A_ub=a_ub,
            b_ub=b_ub,
            A_eq=a_eq,
            b_eq=b_eq,
            bounds=[(0.0, None)] * variable_count,
            method="highs",
        )
        if not minimum.success or not maximum.success:
            raise AssertionError(
                f"independent LP failed: min={minimum.message}, max={maximum.message}"
            )
        global_lower = min(global_lower, float(minimum.fun))
        global_upper = max(global_upper, float(-maximum.fun))

    return IndependentBounds(float(global_lower), float(global_upper))


def independent_classification(
    bounds: IndependentBounds, *, tolerance: float
) -> Decision:
    """Classify comparator bounds without calling production classification."""

    if bounds.upper < -tolerance:
        return Decision.A_LOWER
    if bounds.lower > tolerance:
        return Decision.B_LOWER
    return Decision.ABSTAIN
