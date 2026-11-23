"""Forward and exact inverse QUID-style share publication."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from .models import (
    ONE,
    ZERO,
    DisclosureSet,
    ShareInterval,
    ShareValue,
    as_share_decimal,
)

QUID_THRESHOLD = Decimal("0.05")
QUID_LOW_STEP = Decimal("0.005")
QUID_HIGH_STEP = Decimal("0.01")


def _round_to_step(value: Decimal, step: Decimal) -> Decimal:
    units = (value / step).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return units * step


def publish_quid_share(true_share: ShareValue) -> Decimal:
    """Publish a true share using the frozen positive half-up QUID rule."""

    share = as_share_decimal(true_share)
    step = QUID_LOW_STEP if share < QUID_THRESHOLD else QUID_HIGH_STEP
    return _round_to_step(share, step)


def _is_lattice_value(published: Decimal, step: Decimal) -> bool:
    return published % step == ZERO


def _low_branch_component(published: Decimal) -> ShareInterval | None:
    if not _is_lattice_value(published, QUID_LOW_STEP):
        return None
    half_step = QUID_LOW_STEP / 2
    lower = max(ZERO, published - half_step)
    upper = min(ONE, QUID_THRESHOLD, published + half_step)
    # The true low-branch set is [lower, upper), so equality is empty.
    if lower >= upper:
        return None
    return ShareInterval(lower, upper, upper_included=False)


def _high_branch_component(published: Decimal) -> ShareInterval | None:
    if not _is_lattice_value(published, QUID_HIGH_STEP):
        return None
    half_step = QUID_HIGH_STEP / 2
    lower = max(ZERO, QUID_THRESHOLD, published - half_step)
    upper = min(ONE, published + half_step)
    # The preimage is upper-half-open before share-domain intersection.
    if lower >= upper:
        return None
    upper_included = upper == ONE and upper < published + half_step
    return ShareInterval(lower, upper, upper_included=upper_included)


def inverse_quid_share(
    published_share: ShareValue,
    *,
    ingredient_count: int | None = None,
    rank: int | None = None,
) -> DisclosureSet:
    """Return the exact branch-aware inverse of a published QUID value.

    Each branch is first checked for lattice attainability. Valid preimages are
    then intersected with that branch's true-share domain. Endpoint inclusion
    is retained exactly. The robust adapter evaluates the closure of each
    nonempty component, as permitted for continuous objectives by the frozen
    protocol.

    ``ingredient_count`` and ``rank`` may be supplied together to additionally
    intersect the inverse with that ingredient rank's feasible range.
    """

    if (ingredient_count is None) != (rank is None):
        raise ValueError("ingredient_count and rank must be supplied together")

    published = as_share_decimal(published_share)
    components = [
        component
        for component in (
            _low_branch_component(published),
            _high_branch_component(published),
        )
        if component is not None
    ]
    result = DisclosureSet(components)
    if ingredient_count is not None and rank is not None:
        return result.clip_to_rank(ingredient_count, rank)
    return result


# Concise aliases for callers that already identify the values as shares.
publish_quid = publish_quid_share
inverse_quid = inverse_quid_share
