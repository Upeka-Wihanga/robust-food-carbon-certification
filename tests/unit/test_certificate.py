from __future__ import annotations

from food_carbon_cert.certification import Decision, classify_bounds


def test_conservative_tolerance_and_exact_zero_abstain() -> None:
    assert classify_bounds(-2.0, -2e-12, tolerance=1e-12) is Decision.A_LOWER
    assert classify_bounds(2e-12, 2.0, tolerance=1e-12) is Decision.B_LOWER
    assert classify_bounds(-1.0, 0.0, tolerance=1e-12) is Decision.ABSTAIN
    assert classify_bounds(0.0, 1.0, tolerance=1e-12) is Decision.ABSTAIN
    assert classify_bounds(-1.0, -5e-13, tolerance=1e-12) is Decision.ABSTAIN
    assert classify_bounds(5e-13, 1.0, tolerance=1e-12) is Decision.ABSTAIN
