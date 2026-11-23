from __future__ import annotations

from decimal import Decimal

import pytest

from food_carbon_cert.certification import Decision, FoodUncertainty, certify_pair
from food_carbon_cert.disclosure import (
    DisclosureSet,
    FoodDisclosure,
    InfeasibleDisclosureError,
    IntervalShareDisclosure,
    PointShareDisclosure,
    ShareInterval,
    certify_disclosure_pair,
    inverse_quid_share,
    publish_quid_share,
)
from food_carbon_cert.uncertainty import FactorInterval


def _bounds(disclosure: DisclosureSet) -> list[tuple[Decimal, Decimal]]:
    return [(component.lower, component.upper) for component in disclosure.components]


def test_point_interval_and_disconnected_disclosure_models() -> None:
    point = PointShareDisclosure("0.125").as_set()
    interval = IntervalShareDisclosure("0.1", "0.2").as_set()
    disconnected = DisclosureSet(
        [ShareInterval("0.3", "0.4"), ShareInterval("0.1", "0.2")]
    )

    assert point.components == (ShareInterval.point("0.125"),)
    assert interval.contains("0.15")
    assert _bounds(disconnected) == [
        (Decimal("0.1"), Decimal("0.2")),
        (Decimal("0.3"), Decimal("0.4")),
    ]


def test_neighboring_quid_values_and_positive_half_up_publication() -> None:
    assert _bounds(inverse_quid_share("0.04")) == [
        (Decimal("0.0375"), Decimal("0.0425"))
    ]
    assert _bounds(inverse_quid_share("0.06")) == [(Decimal("0.055"), Decimal("0.065"))]

    assert publish_quid_share("0.0425") == Decimal("0.045")
    assert publish_quid_share("0.0475") == Decimal("0.050")
    assert publish_quid_share("0.049999") == Decimal("0.050")
    assert publish_quid_share("0.050") == Decimal("0.05")
    assert publish_quid_share("0.054999") == Decimal("0.05")
    assert publish_quid_share("0.055") == Decimal("0.06")


def test_every_inverse_component_has_attainable_interior() -> None:
    for published in ("0.04", "0.045", "0.05", "0.055", "0.06"):
        disclosure = inverse_quid_share(published)
        for component in disclosure.components:
            midpoint = (component.lower + component.upper) / 2
            assert publish_quid_share(midpoint) == Decimal(published)


def test_rank_clipping_can_remove_one_or_all_quid_branches() -> None:
    clipped_one = inverse_quid_share("0.05", ingredient_count=20, rank=1)
    assert _bounds(clipped_one) == [(Decimal("0.050"), Decimal("0.055"))]

    clipped_all = inverse_quid_share("0.06", ingredient_count=20, rank=20)
    assert clipped_all.components == ()


def test_rank_clipping_preserves_feasible_intersection() -> None:
    clipped = DisclosureSet.interval("0.2", "0.6").clip_to_rank(4, 2)
    assert _bounds(clipped) == [(Decimal("0.2"), Decimal("0.5"))]


def test_dense_grid_forward_inverse_consistency() -> None:
    failures = 0
    impossible_components = 0
    published_values: set[Decimal] = set()

    for units in range(4000, 6001):
        true_share = Decimal(units) / Decimal("100000")
        published = publish_quid_share(true_share)
        published_values.add(published)
        if not inverse_quid_share(published).contains(true_share):
            failures += 1

    for published in published_values:
        for component in inverse_quid_share(published).components:
            midpoint = (component.lower + component.upper) / 2
            if publish_quid_share(midpoint) != published:
                impossible_components += 1

    assert 6001 - 4000 == 2001
    assert failures == 0
    assert impossible_components == 0


def test_disconnected_components_are_aggregated_without_enclosure() -> None:
    factors = {
        "a0": FactorInterval(0.0, 0.0),
        "a1": FactorInterval(10.0, 10.0),
        "b": FactorInterval(2.0, 2.0),
    }
    food_a = FoodDisclosure(
        ("a0", "a1"),
        2,
        DisclosureSet([ShareInterval.point("0.1"), ShareInterval.point("0.4")]),
    )
    food_b = FoodDisclosure(("b",), 1, DisclosureSet.point("1"))

    first = certify_pair(
        FoodUncertainty(("a0", "a1"), 2, 0.1, 0.1),
        FoodUncertainty(("b",), 1, 1.0, 1.0),
        factors,
    )
    second = certify_pair(
        FoodUncertainty(("a0", "a1"), 2, 0.4, 0.4),
        FoodUncertainty(("b",), 1, 1.0, 1.0),
        factors,
    )
    combined = certify_disclosure_pair(food_a, food_b, factors)

    assert first.decision is Decision.A_LOWER
    assert second.decision is Decision.B_LOWER
    assert combined.lower_bound == min(first.lower_bound, second.lower_bound)
    assert combined.upper_bound == max(first.upper_bound, second.upper_bound)
    assert combined.decision is Decision.ABSTAIN
    assert combined.metadata["disclosure"]["component_pair_count"] == 2


def test_oracle_adapter_rejects_disclosure_with_no_feasible_component() -> None:
    food_a = FoodDisclosure(
        ("a0", "a1"),
        2,
        DisclosureSet.interval("0.6", "0.7"),
    )
    food_b = FoodDisclosure(("b",), 1, DisclosureSet.point("1"))
    factors = {
        "a0": FactorInterval(1.0, 1.0),
        "a1": FactorInterval(1.0, 1.0),
        "b": FactorInterval(1.0, 1.0),
    }

    with pytest.raises(InfeasibleDisclosureError):
        certify_disclosure_pair(food_a, food_b, factors)
