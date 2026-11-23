from __future__ import annotations

from inspect import signature

import pytest

from food_carbon_cert.disclosure import ShareInterval
from food_carbon_cert.stage26 import (
    BASELINE_ORDER,
    EXPECTATION_NODE_COUNT,
    ActionKind,
    B0ShareOnly,
    B1FactorOnly,
    B2FixedStaged,
    B3WidthMixed,
    B4OneStepVoi,
    FactorAcquisition,
    FoodSide,
    LatentObservations,
    OasaTwoStep,
    PolicyId,
    ShareAcquisition,
    Stage26FoodState,
    Stage26PairState,
    StartingShareRegime,
    apply_observation,
    available_actions,
    expectation_nodes,
    run_hindsight_ceiling,
    run_implementable_policy,
    score_immediate_action,
    select_baseline_champion,
    select_macro_average_baseline_champion,
    state_value,
)
from food_carbon_cert.uncertainty import FactorInterval

REGIME = StartingShareRegime.ORDER_ONLY


def _state(
    share_a: tuple[str, str],
    share_b: tuple[str, str],
    factor_bounds: tuple[tuple[float, float], ...],
) -> Stage26PairState:
    keys = ("a1", "a2", "b1", "b2")
    return Stage26PairState(
        Stage26FoodState("a", keys[:2], 1, ShareInterval(*share_a)),
        Stage26FoodState("b", keys[2:], 1, ShareInterval(*share_b)),
        {
            key: FactorInterval(*bounds)
            for key, bounds in zip(keys, factor_bounds, strict=True)
        },
        frozenset(),
        2,
    )


def _symmetric_state() -> Stage26PairState:
    return _state(
        ("0.5", "1"),
        ("0.5", "1"),
        ((1.0, 3.0), (1.0, 3.0), (1.0, 3.0), (1.0, 3.0)),
    )


def _share_first_case() -> Stage26PairState:
    # Synthetic Case A: one-step certification probability favors share A.
    return _state(
        ("0.5", "1"),
        ("0.5", "1"),
        (
            (5.521, 9.202),
            (0.375, 2.625),
            (3.520, 4.302),
            (4.958, 6.060),
        ),
    )


def _factor_first_case() -> Stage26PairState:
    # Synthetic Case B: observing a1 certifies six of nine quadrature branches.
    return _state(
        ("0.5", "1"),
        ("0.55", "0.75"),
        (
            (1.887, 13.211),
            (6.539, 7.992),
            (3.496, 4.273),
            (7.055, 8.622),
        ),
    )


def _non_myopic_case() -> Stage26PairState:
    # Synthetic Case C: B4 chooses factor b1; two-step OASA chooses share B.
    return _state(
        ("0.6", "0.9"),
        ("0.55", "0.75"),
        (
            (3.291, 4.023),
            (2.797, 4.662),
            (3.443, 4.208),
            (0.950, 1.584),
        ),
    )


def _observations() -> LatentObservations:
    return LatentObservations(
        share_a=0.72,
        share_b=0.65,
        factors={"a1": 3.6, "a2": 3.5, "b1": 3.8, "b2": 1.2},
    )


def _symmetric_observations() -> LatentObservations:
    return LatentObservations(
        share_a=0.7,
        share_b=0.7,
        factors={"a1": 2.0, "a2": 2.0, "b1": 2.0, "b2": 2.0},
    )


def test_available_actions_are_pair_local_unresolved_and_canonical() -> None:
    state = _symmetric_state()
    state = Stage26PairState(
        state.food_a,
        state.food_b,
        {**state.factor_intervals, "global-irrelevant": FactorInterval(0.0, 99.0)},
        frozenset(),
        2,
    )

    assert [action.action_id for action in available_actions(state)] == [
        "factor:a1",
        "factor:a2",
        "factor:b1",
        "factor:b2",
        "share:A:1",
        "share:B:1",
    ]


def test_nine_node_expectation_is_midpoint_quantile_and_deterministic() -> None:
    state = _symmetric_state()
    action = next(
        action for action in available_actions(state) if action.action_id == "factor:a1"
    )

    first = expectation_nodes(state, action)
    second = expectation_nodes(state, action)

    assert first == second
    assert len(first) == EXPECTATION_NODE_COUNT == 9
    assert first[0].value == pytest.approx(1.0 + (0.5 / 9.0) * 2.0)
    assert first[-1].value == pytest.approx(1.0 + (8.5 / 9.0) * 2.0)
    assert sum(node.weight for node in first) == pytest.approx(1.0)


def test_b0_never_selects_factors_and_b1_never_selects_shares() -> None:
    state = _symmetric_state()

    assert B0ShareOnly().choose_action(state, REGIME).action.kind is ActionKind.SHARE
    assert B1FactorOnly().choose_action(state, REGIME).action.kind is ActionKind.FACTOR
    share_run = run_implementable_policy(
        B0ShareOnly(), state, REGIME, _symmetric_observations()
    )
    factor_run = run_implementable_policy(
        B1FactorOnly(), state, REGIME, _symmetric_observations()
    )
    assert all(item.action_id.startswith("share:") for item in share_run.acquisitions)
    assert all(item.action_id.startswith("factor:") for item in factor_run.acquisitions)


def test_b2_follows_frozen_regime_type_sequence() -> None:
    state = _symmetric_state()
    policy = B2FixedStaged()

    for coarse_regime in (
        StartingShareRegime.ORDER_ONLY,
        StartingShareRegime.PLUS_MINUS_5PP,
        StartingShareRegime.PLUS_MINUS_2PP,
    ):
        coarse_first = policy.choose_action(state, coarse_regime)
        assert coarse_first is not None
        assert coarse_first.action.kind is ActionKind.SHARE
    coarse_first = policy.choose_action(state, StartingShareRegime.ORDER_ONLY)
    assert coarse_first is not None
    coarse_updated = apply_observation(
        state, coarse_first.action.acquisition, observed_value=0.7
    )
    coarse_second = policy.choose_action(coarse_updated, StartingShareRegime.ORDER_ONLY)
    assert coarse_second is not None
    assert coarse_second.action.kind is ActionKind.FACTOR

    tight_first = policy.choose_action(state, StartingShareRegime.PLUS_MINUS_1PP)
    assert tight_first is not None
    assert tight_first.action.kind is ActionKind.FACTOR
    tight_updated = apply_observation(
        state, tight_first.action.acquisition, observed_value=2.0
    )
    tight_second = policy.choose_action(
        tight_updated, StartingShareRegime.PLUS_MINUS_1PP
    )
    assert tight_second is not None
    assert tight_second.action.kind is ActionKind.SHARE


def test_b3_maximizes_expected_width_reduction_on_symmetric_fixture() -> None:
    decision = B3WidthMixed().choose_action(_symmetric_state(), REGIME)

    assert decision is not None
    assert decision.action.action_id == "factor:a1"
    assert decision.selected_score.expected_width_reduction == pytest.approx(1.0)
    assert decision.selected_score.expected_width_reduction == pytest.approx(
        max(score.expected_width_reduction for score in decision.scores)
    )


def test_synthetic_case_a_is_share_first_and_case_b_is_factor_first() -> None:
    share_decision = B4OneStepVoi().choose_action(_share_first_case(), REGIME)
    factor_decision = B4OneStepVoi().choose_action(_factor_first_case(), REGIME)

    assert share_decision is not None
    assert share_decision.action.action_id == "share:A:1"
    assert share_decision.selected_score.expected_certification == pytest.approx(1 / 9)
    assert factor_decision is not None
    assert factor_decision.action.action_id == "factor:a1"
    assert factor_decision.selected_score.expected_certification == pytest.approx(6 / 9)


def _brute_force_two_step_scores(
    state: Stage26PairState,
) -> dict[str, float]:
    scores: dict[str, float] = {}
    for first in available_actions(state):
        expected = 0.0
        for first_node in expectation_nodes(state, first):
            branch = apply_observation(
                state, first.acquisition, observed_value=first_node.value
            )
            if state_value(branch).certified:
                branch_best = 1.0
            else:
                second_values = []
                for second in available_actions(branch):
                    second_expected = 0.0
                    for second_node in expectation_nodes(branch, second):
                        terminal = apply_observation(
                            branch,
                            second.acquisition,
                            observed_value=second_node.value,
                        )
                        second_expected += second_node.weight * float(
                            state_value(terminal).certified
                        )
                    second_values.append(second_expected)
                branch_best = max(second_values, default=0.0)
            expected += first_node.weight * branch_best
        scores[first.action_id] = expected
    return scores


def test_oasa_matches_independent_exhaustive_two_step_enumeration() -> None:
    state = _non_myopic_case()
    decision = OasaTwoStep().choose_action(state, REGIME)
    exhaustive = _brute_force_two_step_scores(state)

    assert decision is not None
    assert {
        score.action.action_id: score.expected_certification
        for score in decision.scores
    } == pytest.approx(exhaustive)
    assert decision.selected_score.expected_certification == pytest.approx(
        max(exhaustive.values())
    )


def test_synthetic_case_c_oasa_has_non_myopic_two_step_advantage() -> None:
    state = _non_myopic_case()
    myopic = B4OneStepVoi().choose_action(state, REGIME)
    rollout = OasaTwoStep().choose_action(state, REGIME)

    assert myopic is not None and rollout is not None
    assert myopic.action.action_id == "factor:b1"
    assert rollout.action.action_id == "share:B:1"
    rollout_by_action = {
        score.action.action_id: score.expected_certification for score in rollout.scores
    }
    assert rollout_by_action["share:B:1"] == pytest.approx(54 / 81)
    assert rollout_by_action["factor:b1"] == pytest.approx(53 / 81)


def test_policy_cannot_see_latent_truth_before_action_selection() -> None:
    state = _non_myopic_case()
    policy = OasaTwoStep()
    low_truth = LatentObservations(
        0.61,
        0.56,
        {"a1": 3.3, "a2": 2.8, "b1": 3.45, "b2": 0.96},
    )
    high_truth = LatentObservations(
        0.89,
        0.74,
        {"a1": 4.0, "a2": 4.6, "b1": 4.2, "b2": 1.58},
    )

    first = policy.choose_action(state, REGIME)
    second = policy.choose_action(state, REGIME)
    assert first is not None and second is not None
    assert first.action == second.action
    assert low_truth != high_truth
    assert "latent" not in signature(policy.choose_action).parameters
    assert "observations" not in signature(policy.choose_action).parameters
    assert "latent" not in signature(score_immediate_action).parameters
    assert "observations" not in signature(score_immediate_action).parameters


def test_oasa_may_change_after_an_actual_observation() -> None:
    state = _non_myopic_case()
    policy = OasaTwoStep()
    first = policy.choose_action(state, REGIME)
    assert first is not None and first.action.action_id == "share:B:1"

    lower_branch = apply_observation(state, first.action.acquisition, 0.60)
    upper_branch = apply_observation(state, first.action.acquisition, 0.70)
    lower_next = policy.choose_action(lower_branch, REGIME)
    upper_next = policy.choose_action(upper_branch, REGIME)

    assert lower_next is not None and upper_next is not None
    assert lower_next.action.action_id == "factor:a2"
    assert upper_next.action.action_id == "factor:b1"


def test_acquired_actions_are_unavailable_and_budget_is_never_exceeded() -> None:
    state = _symmetric_state()
    acquired = apply_observation(state, ShareAcquisition(FoodSide.A), 0.7)

    assert "share:A:1" not in {
        action.action_id for action in available_actions(acquired)
    }
    acquired = apply_observation(acquired, FactorAcquisition("a1"), 2.0)
    assert acquired.spent == acquired.budget == 2
    assert "factor:a1" not in {
        action.action_id for action in available_actions(acquired)
    }


def test_already_certified_state_stops_without_unnecessary_cost() -> None:
    state = _state(
        ("0.5", "0.6"),
        ("0.5", "0.6"),
        ((0.1, 0.2), (0.1, 0.2), (10.0, 11.0), (10.0, 11.0)),
    )
    assert state_value(state).certified

    run = run_implementable_policy(B4OneStepVoi(), state, REGIME, _observations())

    assert run.acquisitions == ()
    assert run.cost == 0
    assert run.terminal_certified


def test_deterministic_ties_use_canonical_action_id() -> None:
    decision = B0ShareOnly().choose_action(_symmetric_state(), REGIME)

    assert decision is not None
    assert decision.action.action_id == "share:A:1"
    assert decision.tied_best_count == 2


def test_hindsight_ceiling_is_not_below_any_implementable_policy() -> None:
    state = _non_myopic_case()
    observations = _observations()
    policies = (
        B0ShareOnly(),
        B1FactorOnly(),
        B2FixedStaged(),
        B3WidthMixed(),
        B4OneStepVoi(),
        OasaTwoStep(),
    )
    runs = [
        run_implementable_policy(policy, state, REGIME, observations)
        for policy in policies
    ]
    hindsight = run_hindsight_ceiling(state, observations)

    assert int(hindsight.terminal_certified) >= max(
        int(run.terminal_certified) for run in runs
    )
    assert hindsight.cost <= state.budget
    assert all(run.cost <= state.budget for run in runs)
    assert PolicyId.H_HINDSIGHT not in BASELINE_ORDER


def test_training_baseline_champion_uses_frozen_order_for_ties() -> None:
    scores = {policy_id: 0.5 for policy_id in BASELINE_ORDER}

    champion = select_baseline_champion(scores)

    assert champion.policy_id is PolicyId.B0_SHARE_ONLY
    assert champion.had_tie
    assert champion.tied_policy_ids == BASELINE_ORDER


def test_training_champion_macro_averages_exactly_four_regimes() -> None:
    coverage = {
        policy_id: {
            regime: float(index) / 10.0
            for index, regime in enumerate(StartingShareRegime)
        }
        for policy_id in BASELINE_ORDER
    }
    coverage[PolicyId.B3_WIDTH_MIXED][StartingShareRegime.PLUS_MINUS_1PP] = 1.0

    champion = select_macro_average_baseline_champion(coverage)

    assert champion.policy_id is PolicyId.B3_WIDTH_MIXED
    assert champion.training_score == pytest.approx((0.0 + 0.1 + 0.2 + 1.0) / 4)
