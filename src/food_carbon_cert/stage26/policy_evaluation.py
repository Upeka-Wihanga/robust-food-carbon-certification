"""Separated observation execution and evaluation-only hindsight ceiling."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from .policies import (
    POLICY_SCORE_TOLERANCE,
    CandidateAction,
    PolicyComputationCache,
    PolicyDecision,
    PolicyId,
    available_actions,
    state_value,
)
from .preflight import StartingShareRegime
from .state import (
    FactorAcquisition,
    FoodSide,
    ShareAcquisition,
    Stage26PairState,
    apply_observation,
)


class AcquisitionPolicy(Protocol):
    """Implementable policy API, deliberately excluding latent truth."""

    policy_id: PolicyId
    cache: PolicyComputationCache

    def choose_action(
        self, state: Stage26PairState, regime: StartingShareRegime
    ) -> PolicyDecision | None: ...


@dataclass(frozen=True, slots=True)
class LatentObservations:
    """Actual observations held outside implementable policy state."""

    share_a: float
    share_b: float
    factors: Mapping[str, float]

    def reveal(self, action: CandidateAction) -> float:
        """Reveal a value only after an action has been returned."""

        acquisition = action.acquisition
        if isinstance(acquisition, ShareAcquisition):
            return self.share_a if acquisition.side is FoodSide.A else self.share_b
        if isinstance(acquisition, FactorAcquisition):
            try:
                return self.factors[acquisition.factor_key]
            except KeyError as error:
                raise KeyError(
                    f"latent factor is missing: {acquisition.factor_key!r}"
                ) from error
        raise TypeError("unknown Stage-26 acquisition")


@dataclass(frozen=True, slots=True)
class ExecutedAcquisition:
    """One selected action and its subsequently revealed value."""

    action_id: str
    observed_value: float
    spent_after: int
    certified_after: bool
    width_after: float
    tied_best_count: int


@dataclass(frozen=True, slots=True)
class PolicyRun:
    """One deterministic policy trajectory."""

    policy_id: PolicyId
    initial_spent: int
    terminal_state: Stage26PairState
    acquisitions: tuple[ExecutedAcquisition, ...]
    terminal_certified: bool
    terminal_width: float

    @property
    def cost(self) -> int:
        return self.terminal_state.spent - self.initial_spent

    @property
    def tie_event_count(self) -> int:
        return sum(item.tied_best_count > 1 for item in self.acquisitions)


def run_implementable_policy(
    policy: AcquisitionPolicy,
    initial_state: Stage26PairState,
    regime: StartingShareRegime,
    observations: LatentObservations,
) -> PolicyRun:
    """Execute a policy, revealing truth only after each policy decision."""

    state = initial_state
    records: list[ExecutedAcquisition] = []
    while state.remaining_budget > 0:
        current = state_value(state, policy.cache)
        if current.certified:
            break
        decision = policy.choose_action(state, regime)
        if decision is None:
            break
        observed = observations.reveal(decision.action)
        state = apply_observation(
            state, decision.action.acquisition, observed_value=observed
        )
        updated = state_value(state, policy.cache)
        records.append(
            ExecutedAcquisition(
                decision.action.action_id,
                observed,
                state.spent,
                updated.certified,
                updated.width,
                decision.tied_best_count,
            )
        )
    terminal = state_value(state, policy.cache)
    if state.spent > state.budget:
        raise AssertionError("policy execution exceeded its frozen budget")
    return PolicyRun(
        policy.policy_id,
        initial_state.spent,
        state,
        tuple(records),
        terminal.certified,
        terminal.width,
    )


@dataclass(frozen=True, slots=True)
class _HindsightCandidate:
    state: Stage26PairState
    actions: tuple[ExecutedAcquisition, ...]
    certified: bool
    width: float


def _better_hindsight(
    left: _HindsightCandidate, right: _HindsightCandidate
) -> _HindsightCandidate:
    if left.certified != right.certified:
        return left if left.certified else right
    if left.width < right.width - POLICY_SCORE_TOLERANCE:
        return left
    if right.width < left.width - POLICY_SCORE_TOLERANCE:
        return right
    left_ids = tuple(item.action_id for item in left.actions)
    right_ids = tuple(item.action_id for item in right.actions)
    return left if left_ids <= right_ids else right


def run_hindsight_ceiling(
    initial_state: Stage26PairState,
    observations: LatentObservations,
    cache: PolicyComputationCache | None = None,
) -> PolicyRun:
    """Enumerate the best actual-observation sequence under the same budget."""

    def search(
        state: Stage26PairState,
        records: tuple[ExecutedAcquisition, ...],
    ) -> _HindsightCandidate:
        current = state_value(state, cache)
        best = _HindsightCandidate(state, records, current.certified, current.width)
        if current.certified or state.remaining_budget == 0:
            return best
        for action in available_actions(state, cache):
            observed = observations.reveal(action)
            updated = apply_observation(
                state, action.acquisition, observed_value=observed
            )
            value = state_value(updated, cache)
            record = ExecutedAcquisition(
                action.action_id,
                observed,
                updated.spent,
                value.certified,
                value.width,
                1,
            )
            candidate = search(updated, records + (record,))
            best = _better_hindsight(best, candidate)
        return best

    result = search(initial_state, ())
    return PolicyRun(
        PolicyId.H_HINDSIGHT,
        initial_state.spent,
        result.state,
        result.actions,
        result.certified,
        result.width,
    )
