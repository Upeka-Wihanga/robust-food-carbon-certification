from __future__ import annotations

from decimal import Decimal

from food_carbon_cert.disclosure import inverse_quid_share


def _bounds(published: str) -> list[tuple[Decimal, Decimal]]:
    return [
        (component.lower, component.upper)
        for component in inverse_quid_share(published).components
    ]


def test_45_percent_is_attainable_on_low_branch_only() -> None:
    inverse = inverse_quid_share("0.045")

    assert _bounds("0.045") == [(Decimal("0.0425"), Decimal("0.0475"))]
    assert len(inverse.components) == 1
    assert not inverse.components[0].upper_included


def test_45_percent_has_no_spurious_high_branch_singleton_at_50_percent() -> None:
    inverse = inverse_quid_share("0.045")

    assert all(
        not (component.lower == Decimal("0.05") and component.upper == Decimal("0.05"))
        for component in inverse.components
    )
    assert not inverse.contains("0.05")


def test_50_percent_has_valid_low_and_high_branch_components() -> None:
    inverse = inverse_quid_share("0.050")

    assert _bounds("0.050") == [
        (Decimal("0.0475"), Decimal("0.050")),
        (Decimal("0.050"), Decimal("0.055")),
    ]
    assert len(inverse.components) == 2
    assert not inverse.components[0].upper_included
    assert inverse.components[1].lower_included
    assert not inverse.components[1].upper_included


def test_55_percent_is_unattainable() -> None:
    assert inverse_quid_share("0.055").components == ()
