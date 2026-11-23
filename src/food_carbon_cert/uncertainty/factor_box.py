"""Explicit uncertain impact-factor intervals."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class FactorInterval:
    """Closed interval for one shared commodity impact factor."""

    lower: float
    upper: float

    def __post_init__(self) -> None:
        if not isfinite(self.lower) or not isfinite(self.upper):
            raise ValueError("factor interval endpoints must be finite")
        if self.lower > self.upper:
            raise ValueError("factor interval lower bound must not exceed upper bound")

    @classmethod
    def around(cls, center: float, relative_radius: float) -> FactorInterval:
        """Construct a symmetric relative interval around a center value."""

        if not isfinite(center) or not isfinite(relative_radius):
            raise ValueError("center and relative_radius must be finite")
        if relative_radius < 0.0:
            raise ValueError("relative_radius must be nonnegative")
        return cls(center * (1.0 - relative_radius), center * (1.0 + relative_radius))
