"""Frozen Stage-26 implementable acquisition policies.

Policy scoring receives only the current uncertainty state. Actual latent
observations are intentionally absent from every policy API and enter through
the separate execution layer only after a policy returns an action.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import isclose

import numpy as np

from food_carbon_cert.certification import Decision
from food_carbon_cert.geometry import one_rank_slab_vertices

from .preflight import StartingShareRegime
from .state import (
    FactorAcquisition,
    FoodSide,
    ShareAcquisition,
    Stage26Action,
    Stage26FoodState,
    Stage26PairState,
    apply_observation,
    certify_stage26_state,
)

EXPECTATION_NODE_COUNT = 9
POLICY_SCORE_TOLERANCE = 1e-12


class ActionKind(StrEnum):
    """Acquisition-variable type."""

    SHARE = "SHARE"
    FACTOR = "FACTOR"


class PolicyId(StrEnum):
    """Canonical Stage-26 policy identifiers."""

    B0_SHARE_ONLY = "B0"
    B1_FACTOR_ONLY = "B1"
    B2_FIXED_STAGED = "B2"
    B3_WIDTH_MIXED = "B3"
    B4_ONE_STEP_VOI = "B4"
    P_OASA = "P"
    H_HINDSIGHT = "H"


BASELINE_ORDER = (
    PolicyId.B0_SHARE_ONLY,
    PolicyId.B1_FACTOR_ONLY,
    PolicyId.B2_FIXED_STAGED,
    PolicyId.B3_WIDTH_MIXED,
    PolicyId.B4_ONE_STEP_VOI,
)


@dataclass(frozen=True, slots=True)
class CandidateAction:
    """One deterministic, currently available acquisition."""

    action_id: str
    kind: ActionKind
    acquisition: Stage26Action


@dataclass(frozen=True, slots=True)
class ObservationNode:
    """One equal-probability prospective observation node."""

    value: float
    weight: float


@dataclass(frozen=True, slots=True)
class StateValue:
    """Robust certification indicator and interval width."""

    certified: bool
    width: float


@dataclass(frozen=True, slots=True)
class ActionScore:
    """Prospective one- or two-step policy score."""

    action: CandidateAction
    expected_certification: float
    expected_terminal_width: float
    expected_width_reduction: float


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    """A selected action with complete prospective scores."""

    policy_id: PolicyId
    action: CandidateAction
    selected_score: ActionScore
    scores: tuple[ActionScore, ...]
    tied_best_count: int


@dataclass(frozen=True, slots=True)
class BaselineChampion:
    """Training-only baseline selection result."""

    policy_id: PolicyId
    training_score: float
    tied_policy_ids: tuple[PolicyId, ...]

    @property
    def had_tie(self) -> bool:
        return len(self.tied_policy_ids) > 1


def canonical_action_id(action: Stage26Action, state: Stage26PairState) -> str:
    """Return the frozen canonical identifier for an acquisition."""

    if isinstance(action, ShareAcquisition):
        food = state.food_a if action.side is FoodSide.A else state.food_b
        return f"share:{action.side.value}:{food.selected_rank}"
    return f"factor:{action.factor_key}"


def _food_key_share_bounds(
    food: Stage26FoodState,
) -> dict[str, tuple[float, float]]:
    vertices = one_rank_slab_vertices(
        len(food.factor_keys),
        food.selected_rank,
        float(food.share_interval.lower),
        float(food.share_interval.upper),
    )
    bounds: dict[str, tuple[float, float]] = {}
    for key in set(food.factor_keys):
        indexes = [
            index
            for index, factor_key in enumerate(food.factor_keys)
            if factor_key == key
        ]
        shares = np.sum(vertices[:, indexes], axis=1)
        bounds[key] = float(np.min(shares)), float(np.max(shares))
    return bounds


def factor_can_affect_comparison(
    state: Stage26PairState,
    factor_key: str,
    *,
    tolerance: float = POLICY_SCORE_TOLERANCE,
) -> bool:
    """Return whether a factor can have a nonzero current A-minus-B coefficient."""

    lower_a, upper_a = _food_key_share_bounds(state.food_a).get(factor_key, (0.0, 0.0))
    lower_b, upper_b = _food_key_share_bounds(state.food_b).get(factor_key, (0.0, 0.0))
    coefficient_lower = lower_a - upper_b
    coefficient_upper = upper_a - lower_b
    return coefficient_lower < -tolerance or coefficient_upper > tolerance


def available_actions(state: Stage26PairState) -> tuple[CandidateAction, ...]:
    """Construct only unresolved, pair-relevant Stage-26 actions."""

    actions: list[CandidateAction] = []
    for side, food in (
        (FoodSide.A, state.food_a),
        (FoodSide.B, state.food_b),
    ):
        if not food.share_observed and not food.share_interval.is_point:
            share_acquisition = ShareAcquisition(side)
            actions.append(
                CandidateAction(
                    canonical_action_id(share_acquisition, state),
                    ActionKind.SHARE,
                    share_acquisition,
                )
            )

    bounds_a = _food_key_share_bounds(state.food_a)
    bounds_b = _food_key_share_bounds(state.food_b)
    pair_keys = set(bounds_a) | set(bounds_b)
    for key in sorted(pair_keys):
        interval = state.factor_intervals[key]
        lower_a, upper_a = bounds_a.get(key, (0.0, 0.0))
        lower_b, upper_b = bounds_b.get(key, (0.0, 0.0))
        can_affect = (
            lower_a - upper_b < -POLICY_SCORE_TOLERANCE
            or upper_a - lower_b > POLICY_SCORE_TOLERANCE
        )
        if (
            key not in state.observed_factor_keys
            and interval.lower < interval.upper
            and can_affect
        ):
            factor_acquisition = FactorAcquisition(key)
            actions.append(
                CandidateAction(
                    canonical_action_id(factor_acquisition, state),
                    ActionKind.FACTOR,
                    factor_acquisition,
                )
            )
    return tuple(sorted(actions, key=lambda action: action.action_id))


def expectation_nodes(
    state: Stage26PairState, action: CandidateAction
) -> tuple[ObservationNode, ...]:
    """Return the frozen nine midpoint-quantile nodes for one action."""

    if action.kind is ActionKind.SHARE:
        acquisition = action.acquisition
        if not isinstance(acquisition, ShareAcquisition):
            raise TypeError("share candidate must contain a share acquisition")
        food = state.food_a if acquisition.side is FoodSide.A else state.food_b
        lower = float(food.share_interval.lower)
        upper = float(food.share_interval.upper)
    else:
        acquisition = action.acquisition
        if not isinstance(acquisition, FactorAcquisition):
            raise TypeError("factor candidate must contain a factor acquisition")
        interval = state.factor_intervals[acquisition.factor_key]
        lower, upper = interval.lower, interval.upper

    if not lower < upper:
        raise ValueError("prospective expectation requires an unresolved interval")
    weight = 1.0 / EXPECTATION_NODE_COUNT
    nodes = tuple(
        ObservationNode(
            lower + ((index + 0.5) / EXPECTATION_NODE_COUNT) * (upper - lower),
            weight,
        )
        for index in range(EXPECTATION_NODE_COUNT)
    )
    if action.kind is ActionKind.SHARE:
        share_acquisition = action.acquisition
        if not isinstance(share_acquisition, ShareAcquisition):
            raise TypeError("share candidate must contain a share acquisition")
        share_food = (
            state.food_a if share_acquisition.side is FoodSide.A else state.food_b
        )
        for node in nodes:
            try:
                apply_observation(state, action.acquisition, node.value)
                one_rank_slab_vertices(
                    len(share_food.factor_keys),
                    share_food.selected_rank,
                    node.value,
                    node.value,
                )
            except ValueError as error:
                raise AssertionError(
                    f"infeasible prospective share node for {action.action_id}: "
                    f"{node.value}"
                ) from error
    return nodes


def state_value(state: Stage26PairState) -> StateValue:
    """Return the frozen binary certificate value and robust interval width."""

    result = certify_stage26_state(state)
    return StateValue(
        result.decision is not Decision.ABSTAIN,
        result.upper_bound - result.lower_bound,
    )


def _state_cache_key(state: Stage26PairState) -> tuple[object, ...]:
    def food_key(food: Stage26FoodState) -> tuple[object, ...]:
        return (
            food.recipe_id,
            food.factor_keys,
            food.selected_rank,
            str(food.share_interval.lower),
            str(food.share_interval.upper),
            food.share_interval.lower_included,
            food.share_interval.upper_included,
            food.share_observed,
        )

    return (
        food_key(state.food_a),
        food_key(state.food_b),
        tuple(
            (key, interval.lower, interval.upper)
            for key, interval in sorted(state.factor_intervals.items())
        ),
        tuple(sorted(state.observed_factor_keys)),
        state.budget,
        state.spent,
    )


def _cached_state_value(
    state: Stage26PairState,
    cache: dict[tuple[object, ...], StateValue],
) -> StateValue:
    key = _state_cache_key(state)
    result = cache.get(key)
    if result is None:
        result = state_value(state)
        cache[key] = result
    return result


def score_immediate_action(
    state: Stage26PairState, action: CandidateAction
) -> ActionScore:
    """Score one action under the common frozen nine-node model."""

    current = state_value(state)
    expected_certification = 0.0
    expected_width = 0.0
    for node in expectation_nodes(state, action):
        hypothetical = apply_observation(
            state, action.acquisition, observed_value=node.value
        )
        value = state_value(hypothetical)
        expected_certification += node.weight * float(value.certified)
        expected_width += node.weight * value.width
    return ActionScore(
        action,
        expected_certification,
        expected_width,
        current.width - expected_width,
    )


def _equal(left: float, right: float) -> bool:
    return isclose(
        left,
        right,
        rel_tol=0.0,
        abs_tol=POLICY_SCORE_TOLERANCE,
    )


def _select_score(
    scores: tuple[ActionScore, ...],
    *,
    primary: str,
    secondary: str,
) -> tuple[ActionScore, int]:
    if not scores:
        raise ValueError("at least one action score is required")

    def value(score: ActionScore, field: str) -> float:
        return float(getattr(score, field))

    best_primary = max(value(score, primary) for score in scores)
    primary_ties = tuple(
        score for score in scores if _equal(value(score, primary), best_primary)
    )
    best_secondary = max(value(score, secondary) for score in primary_ties)
    final_ties = tuple(
        score
        for score in primary_ties
        if _equal(value(score, secondary), best_secondary)
    )
    selected = min(final_ties, key=lambda score: score.action.action_id)
    return selected, len(final_ties)


def _already_terminal(state: Stage26PairState) -> bool:
    return state.remaining_budget == 0 or state_value(state).certified


class ImmediatePolicy:
    """Base for B0, B1, B3, and B4 immediate policies."""

    policy_id: PolicyId
    allowed_kind: ActionKind | None = None
    primary_score_field = "expected_certification"
    secondary_score_field = "expected_width_reduction"

    def choose_action(
        self, state: Stage26PairState, regime: StartingShareRegime
    ) -> PolicyDecision | None:
        del regime
        if _already_terminal(state):
            return None
        candidates = available_actions(state)
        if self.allowed_kind is not None:
            candidates = tuple(
                action for action in candidates if action.kind is self.allowed_kind
            )
        if not candidates:
            return None
        scores = tuple(score_immediate_action(state, action) for action in candidates)
        selected, tie_count = _select_score(
            scores,
            primary=self.primary_score_field,
            secondary=self.secondary_score_field,
        )
        return PolicyDecision(
            self.policy_id, selected.action, selected, scores, tie_count
        )


class B0ShareOnly(ImmediatePolicy):
    policy_id = PolicyId.B0_SHARE_ONLY
    allowed_kind = ActionKind.SHARE


class B1FactorOnly(ImmediatePolicy):
    policy_id = PolicyId.B1_FACTOR_ONLY
    allowed_kind = ActionKind.FACTOR


class B3WidthMixed(ImmediatePolicy):
    policy_id = PolicyId.B3_WIDTH_MIXED
    primary_score_field = "expected_width_reduction"
    secondary_score_field = "expected_certification"


class B4OneStepVoi(ImmediatePolicy):
    policy_id = PolicyId.B4_ONE_STEP_VOI


class B2FixedStaged:
    """Frozen regime-specific SHARE/FACTOR two-step baseline."""

    policy_id = PolicyId.B2_FIXED_STAGED

    def choose_action(
        self, state: Stage26PairState, regime: StartingShareRegime
    ) -> PolicyDecision | None:
        if _already_terminal(state):
            return None
        if state.spent >= 2:
            raise ValueError("the frozen B2 type sequence is defined only through B=2")
        share_first = regime in {
            StartingShareRegime.ORDER_ONLY,
            StartingShareRegime.PLUS_MINUS_5PP,
            StartingShareRegime.PLUS_MINUS_2PP,
        }
        sequence = (
            (ActionKind.SHARE, ActionKind.FACTOR)
            if share_first
            else (ActionKind.FACTOR, ActionKind.SHARE)
        )
        candidates = available_actions(state)
        preferred = tuple(
            action for action in candidates if action.kind is sequence[state.spent]
        )
        considered = preferred or tuple(
            action for action in candidates if action.kind is not sequence[state.spent]
        )
        if not considered:
            return None
        scores = tuple(score_immediate_action(state, action) for action in considered)
        selected, tie_count = _select_score(
            scores,
            primary="expected_certification",
            secondary="expected_width_reduction",
        )
        return PolicyDecision(
            self.policy_id, selected.action, selected, scores, tie_count
        )


def _select_terminal_score(
    scores: tuple[ActionScore, ...],
) -> tuple[ActionScore, int]:
    if not scores:
        raise ValueError("at least one terminal score is required")
    best_certification = max(score.expected_certification for score in scores)
    certification_ties = tuple(
        score
        for score in scores
        if _equal(score.expected_certification, best_certification)
    )
    best_width = min(score.expected_terminal_width for score in certification_ties)
    final_ties = tuple(
        score
        for score in certification_ties
        if _equal(score.expected_terminal_width, best_width)
    )
    return min(final_ties, key=lambda score: score.action.action_id), len(final_ties)


def _one_step_terminal_scores(
    state: Stage26PairState,
    *,
    value_cache: dict[tuple[object, ...], StateValue] | None = None,
) -> tuple[ActionScore, ...]:
    cache = {} if value_cache is None else value_cache
    current = _cached_state_value(state, cache)
    scores: list[ActionScore] = []
    for action in available_actions(state):
        expected_certification = 0.0
        expected_width = 0.0
        for node in expectation_nodes(state, action):
            terminal = apply_observation(state, action.acquisition, node.value)
            value = _cached_state_value(terminal, cache)
            expected_certification += node.weight * float(value.certified)
            expected_width += node.weight * value.width
        scores.append(
            ActionScore(
                action,
                expected_certification,
                expected_width,
                current.width - expected_width,
            )
        )
    return tuple(scores)


class OasaTwoStep:
    """Frozen B=2 observation-aware two-step budget-aware rollout."""

    policy_id = PolicyId.P_OASA

    def choose_action(
        self, state: Stage26PairState, regime: StartingShareRegime
    ) -> PolicyDecision | None:
        del regime
        if _already_terminal(state):
            return None
        if state.remaining_budget > 2:
            raise ValueError("frozen OASA rollout supports at most two remaining units")
        if state.remaining_budget == 1:
            scores = _one_step_terminal_scores(state)
            if not scores:
                return None
            selected, tie_count = _select_terminal_score(scores)
            return PolicyDecision(
                self.policy_id, selected.action, selected, scores, tie_count
            )

        value_cache: dict[tuple[object, ...], StateValue] = {}
        current = _cached_state_value(state, value_cache)
        first_scores: list[ActionScore] = []
        for first_action in available_actions(state):
            expected_terminal_certification = 0.0
            expected_terminal_width = 0.0
            for first_node in expectation_nodes(state, first_action):
                branch = apply_observation(
                    state, first_action.acquisition, first_node.value
                )
                branch_value = _cached_state_value(branch, value_cache)
                if branch_value.certified:
                    terminal_certification = 1.0
                    terminal_width = branch_value.width
                else:
                    second_scores = _one_step_terminal_scores(
                        branch, value_cache=value_cache
                    )
                    if second_scores:
                        best_second, _ = _select_terminal_score(second_scores)
                        terminal_certification = best_second.expected_certification
                        terminal_width = best_second.expected_terminal_width
                    else:
                        terminal_certification = 0.0
                        terminal_width = branch_value.width
                expected_terminal_certification += (
                    first_node.weight * terminal_certification
                )
                expected_terminal_width += first_node.weight * terminal_width
            first_scores.append(
                ActionScore(
                    first_action,
                    expected_terminal_certification,
                    expected_terminal_width,
                    current.width - expected_terminal_width,
                )
            )
        scores = tuple(first_scores)
        if not scores:
            return None
        selected, tie_count = _select_terminal_score(scores)
        return PolicyDecision(
            self.policy_id, selected.action, selected, scores, tie_count
        )


def select_baseline_champion(
    training_scores: Mapping[PolicyId, float],
) -> BaselineChampion:
    """Select a training-only baseline with frozen canonical tie order."""

    if set(training_scores) != set(BASELINE_ORDER):
        raise ValueError("training scores must contain exactly B0 through B4")
    best_score = max(training_scores.values())
    tied = tuple(
        policy_id
        for policy_id in BASELINE_ORDER
        if _equal(training_scores[policy_id], best_score)
    )
    return BaselineChampion(tied[0], best_score, tied)


def select_macro_average_baseline_champion(
    training_coverage_by_regime: Mapping[PolicyId, Mapping[StartingShareRegime, float]],
) -> BaselineChampion:
    """Select B0–B4 from training-only macro coverage across all four regimes."""

    expected_regimes = set(StartingShareRegime)
    if set(training_coverage_by_regime) != set(BASELINE_ORDER):
        raise ValueError("training coverage must contain exactly B0 through B4")
    macro_scores: dict[PolicyId, float] = {}
    for policy_id in BASELINE_ORDER:
        regime_scores = training_coverage_by_regime[policy_id]
        if set(regime_scores) != expected_regimes:
            raise ValueError(
                "each baseline requires training coverage for all four regimes"
            )
        macro_scores[policy_id] = sum(regime_scores.values()) / len(expected_regimes)
    return select_baseline_champion(macro_scores)
