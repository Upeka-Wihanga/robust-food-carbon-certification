"""Exact ingredient-share disclosure models.

Disclosure endpoints are stored as :class:`~decimal.Decimal` values so that
publication-grid decisions do not depend on binary floating-point rounding.
Endpoint inclusion is retained for exact QUID inversion. The robust adapter
uses the closure of each nonempty component because continuous objectives have
the same extrema on the half-open set and its closure.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import TypeAlias

from food_carbon_cert.geometry import rank_feasible_interval

ShareValue: TypeAlias = Decimal | int | float | str

ZERO = Decimal("0")
ONE = Decimal("1")


def as_share_decimal(value: ShareValue) -> Decimal:
    """Convert a public share value to an exact, validated decimal."""

    if isinstance(value, bool):
        raise TypeError("share values must be numeric, not boolean")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError("share values must be valid decimal numbers") from error
    if not result.is_finite():
        raise ValueError("share values must be finite")
    if not ZERO <= result <= ONE:
        raise ValueError("share values must lie between zero and one")
    return result


@dataclass(frozen=True, slots=True)
class ShareInterval:
    """An interval of possible true ingredient shares."""

    lower: Decimal
    upper: Decimal
    lower_included: bool
    upper_included: bool

    def __init__(
        self,
        lower: ShareValue,
        upper: ShareValue,
        *,
        lower_included: bool = True,
        upper_included: bool = True,
    ) -> None:
        validated_lower = as_share_decimal(lower)
        validated_upper = as_share_decimal(upper)
        if validated_lower > validated_upper:
            raise ValueError("share interval lower bound must not exceed upper bound")
        if validated_lower == validated_upper and not (
            lower_included and upper_included
        ):
            raise ValueError("a singleton interval must include its endpoint")
        object.__setattr__(self, "lower", validated_lower)
        object.__setattr__(self, "upper", validated_upper)
        object.__setattr__(self, "lower_included", lower_included)
        object.__setattr__(self, "upper_included", upper_included)

    @classmethod
    def point(cls, share: ShareValue) -> ShareInterval:
        """Construct a singleton share interval."""

        return cls(share, share)

    @property
    def is_point(self) -> bool:
        """Return whether this interval contains exactly one share."""

        return self.lower == self.upper

    def contains(self, share: ShareValue) -> bool:
        """Return whether a true share lies in this interval."""

        value = as_share_decimal(share)
        above_lower = value > self.lower or (
            self.lower_included and value == self.lower
        )
        below_upper = value < self.upper or (
            self.upper_included and value == self.upper
        )
        return above_lower and below_upper


@dataclass(frozen=True, slots=True)
class PointShareDisclosure:
    """An exact point disclosure."""

    share: Decimal

    def __init__(self, share: ShareValue) -> None:
        object.__setattr__(self, "share", as_share_decimal(share))

    def as_set(self) -> DisclosureSet:
        """Return this point as a one-component disclosure set."""

        return DisclosureSet((ShareInterval.point(self.share),))


@dataclass(frozen=True, slots=True)
class IntervalShareDisclosure:
    """A single closed interval disclosure."""

    interval: ShareInterval

    def __init__(self, lower: ShareValue, upper: ShareValue) -> None:
        object.__setattr__(self, "interval", ShareInterval(lower, upper))

    def as_set(self) -> DisclosureSet:
        """Return this interval as a one-component disclosure set."""

        return DisclosureSet((self.interval,))


@dataclass(frozen=True, slots=True)
class DisclosureSet:
    """A union of zero or more interval components.

    Components are sorted deterministically but deliberately not merged.
    Keeping them separate preserves disconnected inverse branches and their
    auditability.
    """

    components: tuple[ShareInterval, ...]

    def __init__(self, components: tuple[ShareInterval, ...] | list[ShareInterval]):
        if any(not isinstance(component, ShareInterval) for component in components):
            raise TypeError("disclosure components must be ShareInterval instances")
        ordered = tuple(
            sorted(
                components,
                key=lambda component: (
                    component.lower,
                    component.upper,
                    component.lower_included,
                    component.upper_included,
                ),
            )
        )
        object.__setattr__(self, "components", ordered)

    @classmethod
    def point(cls, share: ShareValue) -> DisclosureSet:
        """Construct a one-component point disclosure."""

        return cls((ShareInterval.point(share),))

    @classmethod
    def interval(cls, lower: ShareValue, upper: ShareValue) -> DisclosureSet:
        """Construct a one-component interval disclosure."""

        return cls((ShareInterval(lower, upper),))

    def contains(self, share: ShareValue) -> bool:
        """Return whether any component contains a true share."""

        return any(component.contains(share) for component in self.components)

    def clip_to_rank(self, ingredient_count: int, rank: int) -> DisclosureSet:
        """Intersect every component with the selected rank-feasible range."""

        feasible_lower, feasible_upper = rank_feasible_interval(ingredient_count, rank)
        lower = Decimal(str(feasible_lower))
        upper = Decimal(str(feasible_upper))
        clipped: list[ShareInterval] = []
        for component in self.components:
            component_lower = max(component.lower, lower)
            component_upper = min(component.upper, upper)
            lower_included = (
                component.lower_included if component_lower == component.lower else True
            )
            upper_included = (
                component.upper_included if component_upper == component.upper else True
            )
            if component_lower < component_upper or (
                component_lower == component_upper and lower_included and upper_included
            ):
                clipped.append(
                    ShareInterval(
                        component_lower,
                        component_upper,
                        lower_included=lower_included,
                        upper_included=upper_included,
                    )
                )
        return DisclosureSet(clipped)

    def __bool__(self) -> bool:
        return bool(self.components)


def point_disclosure(share: ShareValue) -> DisclosureSet:
    """Construct a point disclosure set."""

    return DisclosureSet.point(share)


def interval_disclosure(lower: ShareValue, upper: ShareValue) -> DisclosureSet:
    """Construct an interval disclosure set."""

    return DisclosureSet.interval(lower, upper)
