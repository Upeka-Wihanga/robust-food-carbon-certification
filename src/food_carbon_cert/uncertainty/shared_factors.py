"""Shared-factor aggregation and exact box extrema for fixed compositions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import numpy as np
from numpy.typing import ArrayLike

from .factor_box import FactorInterval


def aggregate_factor_difference(
    shares_a: ArrayLike,
    commodity_codes_a: Sequence[str],
    shares_b: ArrayLike,
    commodity_codes_b: Sequence[str],
) -> dict[str, float]:
    """Aggregate ``A - B`` composition coefficients by shared commodity code."""

    values_a = np.asarray(shares_a, dtype=np.float64)
    values_b = np.asarray(shares_b, dtype=np.float64)
    if values_a.ndim != 1 or values_b.ndim != 1:
        raise ValueError("composition shares must be one-dimensional")
    if values_a.size != len(commodity_codes_a):
        raise ValueError("food A shares and commodity codes have different lengths")
    if values_b.size != len(commodity_codes_b):
        raise ValueError("food B shares and commodity codes have different lengths")

    coefficients: dict[str, float] = {}
    for share, code in zip(values_a, commodity_codes_a, strict=True):
        coefficients[code] = coefficients.get(code, 0.0) + float(share)
    for share, code in zip(values_b, commodity_codes_b, strict=True):
        coefficients[code] = coefficients.get(code, 0.0) - float(share)
    return coefficients


def factor_box_extrema(
    coefficients: Mapping[str, float],
    factor_intervals: Mapping[str, FactorInterval],
) -> tuple[float, float]:
    """Return exact minimum and maximum for a linear shared-factor box."""

    lower_value = 0.0
    upper_value = 0.0
    for code, coefficient in coefficients.items():
        try:
            interval = factor_intervals[code]
        except KeyError as error:
            raise KeyError(
                f"missing factor interval for commodity code {code!r}"
            ) from error
        if coefficient >= 0.0:
            lower_value += coefficient * interval.lower
            upper_value += coefficient * interval.upper
        else:
            lower_value += coefficient * interval.upper
            upper_value += coefficient * interval.lower
    return lower_value, upper_value


def fixed_composition_bounds(
    shares_a: ArrayLike,
    commodity_codes_a: Sequence[str],
    shares_b: ArrayLike,
    commodity_codes_b: Sequence[str],
    factor_intervals: Mapping[str, FactorInterval],
) -> tuple[float, float]:
    """Return robust ``A - B`` bounds for one fixed composition pair."""

    coefficients = aggregate_factor_difference(
        shares_a, commodity_codes_a, shares_b, commodity_codes_b
    )
    return factor_box_extrema(coefficients, factor_intervals)
