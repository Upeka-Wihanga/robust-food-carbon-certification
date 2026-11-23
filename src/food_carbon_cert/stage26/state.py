"""Stage-26 observation and budget state primitives.

Policy selection is intentionally absent. Latent values are supplied only to
the update operation after an action has already been chosen.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from food_carbon_cert.certification import CertificationResult
from food_carbon_cert.disclosure import (
    DisclosureSet,
    FoodDisclosure,
    ShareInterval,
    certify_disclosure_pair,
)
from food_carbon_cert.uncertainty import FactorInterval


class FoodSide(StrEnum):
    """The food whose preselected share is acquired."""

    A = "A"
    B = "B"


@dataclass(frozen=True, slots=True)
class Stage26FoodState:
    """Current uncertainty for one food's preselected rank."""

    recipe_id: str
    factor_keys: tuple[str, ...]
    selected_rank: int
    share_interval: ShareInterval
    share_observed: bool = False

    def __init__(
        self,
        recipe_id: str,
        factor_keys: Sequence[str],
        selected_rank: int,
        share_interval: ShareInterval,
        *,
        share_observed: bool = False,
    ) -> None:
        keys = tuple(factor_keys)
        if not keys:
            raise ValueError("food state requires at least one factor key")
        if not 1 <= selected_rank <= len(keys):
            raise ValueError("selected rank lies outside the food")
        object.__setattr__(self, "recipe_id", recipe_id)
        object.__setattr__(self, "factor_keys", keys)
        object.__setattr__(self, "selected_rank", selected_rank)
        object.__setattr__(self, "share_interval", share_interval)
        object.__setattr__(self, "share_observed", share_observed)


@dataclass(frozen=True, slots=True)
class ShareAcquisition:
    """Reveal the already-selected share for one food."""

    side: FoodSide
    cost: int = 1


@dataclass(frozen=True, slots=True)
class FactorAcquisition:
    """Reveal one shared factor."""

    factor_key: str
    cost: int = 1


Stage26Action = ShareAcquisition | FactorAcquisition


@dataclass(frozen=True, slots=True)
class Stage26PairState:
    """Current pair uncertainty and exact acquisition-budget accounting."""

    food_a: Stage26FoodState
    food_b: Stage26FoodState
    factor_intervals: Mapping[str, FactorInterval]
    observed_factor_keys: frozenset[str]
    budget: int
    spent: int = 0

    def __post_init__(self) -> None:
        if self.budget < 0 or self.spent < 0:
            raise ValueError("budget and spent cost must be nonnegative")
        if self.spent > self.budget:
            raise ValueError("spent cost cannot exceed budget")
        required = set(self.food_a.factor_keys) | set(self.food_b.factor_keys)
        missing = required.difference(self.factor_intervals)
        if missing:
            raise KeyError(f"state is missing factor intervals: {sorted(missing)}")

    @property
    def remaining_budget(self) -> int:
        return self.budget - self.spent


@dataclass(frozen=True, slots=True)
class ObservedStage26State:
    """An updated state and its recomputed robust certificate."""

    state: Stage26PairState
    certificate: CertificationResult


def _validate_action_cost(action: Stage26Action, state: Stage26PairState) -> None:
    if action.cost != 1:
        raise ValueError("frozen Stage-26 acquisitions must cost exactly one")
    if action.cost > state.remaining_budget:
        raise ValueError("acquisition exceeds remaining budget")


def observe_share(
    state: Stage26PairState, action: ShareAcquisition, observed_share: float
) -> Stage26PairState:
    """Apply one post-selection full share reveal."""

    _validate_action_cost(action, state)
    food = state.food_a if action.side is FoodSide.A else state.food_b
    if food.share_observed:
        raise ValueError("selected share has already been observed")
    if not food.share_interval.contains(observed_share):
        raise ValueError("observed share lies outside the current uncertainty set")
    updated_food = Stage26FoodState(
        food.recipe_id,
        food.factor_keys,
        food.selected_rank,
        ShareInterval.point(observed_share),
        share_observed=True,
    )
    return Stage26PairState(
        food_a=updated_food if action.side is FoodSide.A else state.food_a,
        food_b=updated_food if action.side is FoodSide.B else state.food_b,
        factor_intervals=dict(state.factor_intervals),
        observed_factor_keys=state.observed_factor_keys,
        budget=state.budget,
        spent=state.spent + action.cost,
    )


def observe_factor(
    state: Stage26PairState, action: FactorAcquisition, observed_factor: float
) -> Stage26PairState:
    """Apply one post-selection full factor reveal."""

    _validate_action_cost(action, state)
    if action.factor_key in state.observed_factor_keys:
        raise ValueError("factor has already been observed")
    try:
        interval = state.factor_intervals[action.factor_key]
    except KeyError as error:
        raise KeyError(f"unknown factor key {action.factor_key!r}") from error
    if not interval.lower <= observed_factor <= interval.upper:
        raise ValueError("observed factor lies outside the current uncertainty set")
    updated_intervals = dict(state.factor_intervals)
    updated_intervals[action.factor_key] = FactorInterval(
        observed_factor, observed_factor
    )
    return Stage26PairState(
        food_a=state.food_a,
        food_b=state.food_b,
        factor_intervals=updated_intervals,
        observed_factor_keys=state.observed_factor_keys | {action.factor_key},
        budget=state.budget,
        spent=state.spent + action.cost,
    )


def apply_observation(
    state: Stage26PairState,
    action: Stage26Action,
    observed_value: float,
) -> Stage26PairState:
    """Update state only from the value observed after the selected action."""

    if isinstance(action, ShareAcquisition):
        return observe_share(state, action, observed_value)
    return observe_factor(state, action, observed_value)


def certify_stage26_state(state: Stage26PairState) -> CertificationResult:
    """Recompute the robust certificate for the state's current uncertainty."""

    food_a = FoodDisclosure(
        state.food_a.factor_keys,
        state.food_a.selected_rank,
        DisclosureSet((state.food_a.share_interval,)),
    )
    food_b = FoodDisclosure(
        state.food_b.factor_keys,
        state.food_b.selected_rank,
        DisclosureSet((state.food_b.share_interval,)),
    )
    return certify_disclosure_pair(food_a, food_b, state.factor_intervals)


def observe_and_certify(
    state: Stage26PairState,
    action: Stage26Action,
    observed_value: float,
) -> ObservedStage26State:
    """Apply one observation and recompute its robust certificate."""

    updated = apply_observation(state, action, observed_value)
    return ObservedStage26State(updated, certify_stage26_state(updated))
