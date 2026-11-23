from __future__ import annotations

from food_carbon_cert.disclosure import ShareInterval
from food_carbon_cert.stage26 import (
    FactorAcquisition,
    FoodSide,
    ShareAcquisition,
    Stage26FoodState,
    Stage26PairState,
    apply_observation,
    observe_and_certify,
)
from food_carbon_cert.uncertainty import FactorInterval


def _state(*, budget: int = 2) -> Stage26PairState:
    return Stage26PairState(
        food_a=Stage26FoodState(
            "a",
            ("shared", "a-only"),
            1,
            ShareInterval("0.5", "0.8"),
        ),
        food_b=Stage26FoodState(
            "b",
            ("shared", "b-only"),
            1,
            ShareInterval("0.5", "0.8"),
        ),
        factor_intervals={
            "shared": FactorInterval(1.0, 2.0),
            "a-only": FactorInterval(2.0, 4.0),
            "b-only": FactorInterval(3.0, 5.0),
        },
        observed_factor_keys=frozenset(),
        budget=budget,
    )


def test_share_observation_costs_one_and_collapses_only_selected_share() -> None:
    state = _state()
    updated = apply_observation(state, ShareAcquisition(FoodSide.A), observed_value=0.6)

    assert updated.spent == 1
    assert updated.remaining_budget == 1
    assert updated.food_a.share_interval.is_point
    assert updated.food_a.share_observed
    assert not updated.food_b.share_observed
    assert updated.factor_intervals == state.factor_intervals


def test_factor_observation_costs_one_and_preserves_shared_identity() -> None:
    state = _state()
    updated = apply_observation(state, FactorAcquisition("shared"), observed_value=1.4)

    assert updated.spent == 1
    assert updated.factor_intervals["shared"] == FactorInterval(1.4, 1.4)
    assert updated.observed_factor_keys == {"shared"}
    assert updated.food_a.factor_keys[0] == updated.food_b.factor_keys[0] == "shared"


def test_observation_update_recomputes_robust_certificate() -> None:
    result = observe_and_certify(
        _state(), FactorAcquisition("a-only"), observed_value=3.0
    )

    assert result.state.spent == 1
    assert result.certificate.lower_bound <= result.certificate.upper_bound


def test_budget_accounting_rejects_third_unit_cost_action() -> None:
    state = _state()
    state = apply_observation(state, ShareAcquisition(FoodSide.A), 0.6)
    state = apply_observation(state, FactorAcquisition("shared"), 1.4)

    assert state.remaining_budget == 0
    try:
        apply_observation(state, ShareAcquisition(FoodSide.B), 0.6)
    except ValueError as error:
        assert "remaining budget" in str(error)
    else:
        raise AssertionError("an acquisition beyond budget was accepted")


def test_state_primitives_have_no_future_observation_input() -> None:
    state = _state()
    first = apply_observation(state, FactorAcquisition("shared"), 1.4)

    # Unobserved future values are deliberately external to the state API.
    unrelated_future_values = {"a-only": 2.1, "b-only": 4.9}
    unrelated_future_values["a-only"] = 3.9
    second = apply_observation(state, FactorAcquisition("shared"), 1.4)

    assert first == second
    assert not hasattr(state, "latent_factors")
    assert not hasattr(state, "future_observations")


def test_observations_must_be_contained_in_current_uncertainty() -> None:
    state = _state()

    for action, value in (
        (ShareAcquisition(FoodSide.A), 0.9),
        (FactorAcquisition("shared"), 2.1),
    ):
        try:
            apply_observation(state, action, value)
        except ValueError as error:
            assert "outside the current uncertainty set" in str(error)
        else:
            raise AssertionError("an out-of-set observation was accepted")
