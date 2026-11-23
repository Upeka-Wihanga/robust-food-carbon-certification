from __future__ import annotations

import random
from dataclasses import replace
from pathlib import Path

import pytest

from food_carbon_cert.data import load_guan, load_source_manifest
from food_carbon_cert.disclosure import ShareInterval
from food_carbon_cert.stage26 import (
    B0ShareOnly,
    B1FactorOnly,
    B2FixedStaged,
    B3WidthMixed,
    B4OneStepVoi,
    FactorAcquisition,
    OasaTwoStep,
    PolicyComputationCache,
    Stage26FoodState,
    Stage26PairState,
    StartingShareRegime,
    apply_observation,
    build_m2_factor_model,
    build_within_cuisine_pairs,
    certify_stage26_state,
    expectation_nodes,
    make_starting_share_disclosure,
    normalize_guan_factor_table,
    observable_state_key,
    reconstruct_guan_cohort,
    select_recipe_share_rank,
    state_value,
)
from food_carbon_cert.uncertainty import FactorInterval

PROJECT_ROOT = Path(__file__).parents[2]
RAW_GUAN = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "Carbon footprint and nutrition estimation of Chinese cuisines.xlsx"
)
SCORE_TOLERANCE = 1e-12


def _small_state(
    share_a: tuple[str, str],
    share_b: tuple[str, str],
    factor_bounds: tuple[tuple[float, float], ...],
    *,
    recipe_prefix: str = "fixture",
) -> Stage26PairState:
    keys = ("a1", "a2", "b1", "b2")
    return Stage26PairState(
        Stage26FoodState(f"{recipe_prefix}-a", keys[:2], 1, ShareInterval(*share_a)),
        Stage26FoodState(f"{recipe_prefix}-b", keys[2:], 1, ShareInterval(*share_b)),
        {
            key: FactorInterval(*bounds)
            for key, bounds in zip(keys, factor_bounds, strict=True)
        },
        frozenset(),
        2,
    )


def _assert_decision_parity(left, right) -> None:
    assert (left is None) == (right is None)
    if left is None or right is None:
        return
    assert left.action.action_id == right.action.action_id
    assert left.tied_best_count == right.tied_best_count
    left_scores = {score.action.action_id: score for score in left.scores}
    right_scores = {score.action.action_id: score for score in right.scores}
    assert set(left_scores) == set(right_scores)
    for action_id in left_scores:
        left_score = left_scores[action_id]
        right_score = right_scores[action_id]
        assert left_score.expected_certification == pytest.approx(
            right_score.expected_certification, abs=SCORE_TOLERANCE
        )
        assert left_score.expected_terminal_width == pytest.approx(
            right_score.expected_terminal_width, abs=SCORE_TOLERANCE
        )
        assert left_score.expected_width_reduction == pytest.approx(
            right_score.expected_width_reduction, abs=SCORE_TOLERANCE
        )


def test_optimized_oasa_matches_cache_disabled_non_myopic_reference() -> None:
    state = _small_state(
        ("0.6", "0.9"),
        ("0.55", "0.75"),
        (
            (3.291, 4.023),
            (2.797, 4.662),
            (3.443, 4.208),
            (0.950, 1.584),
        ),
    )
    optimized = OasaTwoStep(PolicyComputationCache(enabled=True))
    reference = OasaTwoStep(PolicyComputationCache(enabled=False))

    optimized_first = optimized.choose_action(state, StartingShareRegime.ORDER_ONLY)
    reference_first = reference.choose_action(state, StartingShareRegime.ORDER_ONLY)
    _assert_decision_parity(optimized_first, reference_first)
    assert optimized_first is not None

    for node in expectation_nodes(state, optimized_first.action):
        branch = apply_observation(
            state, optimized_first.action.acquisition, node.value
        )
        _assert_decision_parity(
            optimized.choose_action(branch, StartingShareRegime.ORDER_ONLY),
            reference.choose_action(branch, StartingShareRegime.ORDER_ONLY),
        )


def test_all_implementable_policies_match_with_cache_enabled_and_disabled() -> None:
    state = _small_state(
        ("0.6", "0.9"),
        ("0.55", "0.75"),
        (
            (3.291, 4.023),
            (2.797, 4.662),
            (3.443, 4.208),
            (0.950, 1.584),
        ),
    )
    policy_types = (
        B0ShareOnly,
        B1FactorOnly,
        B2FixedStaged,
        B3WidthMixed,
        B4OneStepVoi,
        OasaTwoStep,
    )
    for policy_type in policy_types:
        optimized = policy_type(PolicyComputationCache(enabled=True))
        reference = policy_type(PolicyComputationCache(enabled=False))
        _assert_decision_parity(
            optimized.choose_action(state, StartingShareRegime.ORDER_ONLY),
            reference.choose_action(state, StartingShareRegime.ORDER_ONLY),
        )


def test_optimized_oasa_matches_reference_on_twenty_random_small_states() -> None:
    generator = random.Random(26026)
    compared = 0
    attempts = 0
    while compared < 20 and attempts < 200:
        attempts += 1
        share_a = generator.choice((("0.5", "1"), ("0.5", "0.8"), ("0.6", "0.9")))
        share_b = generator.choice((("0.5", "1"), ("0.55", "0.75"), ("0.6", "0.9")))
        factor_bounds = []
        for _ in range(4):
            center = generator.uniform(0.5, 8.0)
            radius = generator.choice((0.1, 0.25, 0.5)) * center
            factor_bounds.append((max(0.01, center - radius), center + radius))
        state = _small_state(
            share_a,
            share_b,
            tuple(factor_bounds),
            recipe_prefix=f"random-{attempts}",
        )
        if state_value(state).certified:
            continue
        optimized_value = state_value(state, PolicyComputationCache(enabled=True))
        reference_certificate = certify_stage26_state(state)
        assert optimized_value.certified == (
            reference_certificate.decision.value != "ABSTAIN"
        )
        assert optimized_value.width == pytest.approx(
            reference_certificate.upper_bound - reference_certificate.lower_bound,
            abs=SCORE_TOLERANCE,
        )

        optimized = OasaTwoStep(PolicyComputationCache(enabled=True))
        reference = OasaTwoStep(PolicyComputationCache(enabled=False))
        optimized_first = optimized.choose_action(state, StartingShareRegime.ORDER_ONLY)
        reference_first = reference.choose_action(state, StartingShareRegime.ORDER_ONLY)
        _assert_decision_parity(optimized_first, reference_first)
        assert optimized_first is not None

        actual_node = expectation_nodes(state, optimized_first.action)[4]
        branch = apply_observation(
            state, optimized_first.action.acquisition, actual_node.value
        )
        _assert_decision_parity(
            optimized.choose_action(branch, StartingShareRegime.ORDER_ONLY),
            reference.choose_action(branch, StartingShareRegime.ORDER_ONLY),
        )
        compared += 1

    assert compared == 20


def test_observable_cache_keys_separate_pairs_states_and_observations() -> None:
    state = _small_state(
        ("0.5", "1"),
        ("0.5", "1"),
        ((1.0, 3.0),) * 4,
    )
    changed_pair = replace(
        state,
        food_a=replace(state.food_a, recipe_id="different-pair-a"),
    )
    changed_share = apply_observation(
        state,
        FactorAcquisition("a1"),
        2.0,
    )

    assert observable_state_key(state) != observable_state_key(changed_pair)
    assert observable_state_key(state) != observable_state_key(changed_share)


def test_latent_truth_does_not_enter_preobservation_cache_key() -> None:
    state = _small_state(
        ("0.6", "0.9"),
        ("0.55", "0.75"),
        (
            (3.291, 4.023),
            (2.797, 4.662),
            (3.443, 4.208),
            (0.950, 1.584),
        ),
    )
    cache = PolicyComputationCache()
    policy = OasaTwoStep(cache)

    first = policy.choose_action(state, StartingShareRegime.ORDER_ONLY)
    cache_size = len(cache.decisions)
    second = policy.choose_action(state, StartingShareRegime.ORDER_ONLY)

    assert first == second
    assert len(cache.decisions) == cache_size


@pytest.fixture(scope="module")
def guan_policy_states():
    if not RAW_GUAN.is_file():
        pytest.skip("licensed Guan source is not locally available")
    manifest = load_source_manifest(
        PROJECT_ROOT / "data" / "manifests" / "source_files.json"
    )
    expected = manifest.by_category("guan_external_recipe_workbook")
    source = load_guan(RAW_GUAN, expected=expected)
    factors = normalize_guan_factor_table(source)
    cohort = reconstruct_guan_cohort(source, factors=factors)
    m2 = build_m2_factor_model(cohort.eligible_recipes, factors)
    recipes = {recipe.recipe_id: recipe for recipe in cohort.eligible_recipes}
    training_pairs = [
        pair
        for pair in build_within_cuisine_pairs(cohort.eligible_recipes)
        if pair.cuisine != "Chuan Cuisine"
    ]
    selected_pairs = sorted(
        training_pairs,
        key=lambda pair: (
            len(recipes[pair.recipe_a_id].ingredients)
            + len(recipes[pair.recipe_b_id].ingredients),
            pair.pair_id,
        ),
    )[:3]

    states = []
    for pair_index, pair in enumerate(selected_pairs):
        recipe_a = recipes[pair.recipe_a_id]
        recipe_b = recipes[pair.recipe_b_id]
        selection_a = select_recipe_share_rank(recipe_a, m2.intervals)
        selection_b = select_recipe_share_rank(recipe_b, m2.intervals)
        for regime in StartingShareRegime:
            disclosure_a = make_starting_share_disclosure(
                ingredient_count=len(recipe_a.ingredients),
                rank=selection_a.rank,
                latent_share=recipe_a.ingredients[selection_a.rank - 1].share,
                regime=regime,
            )
            disclosure_b = make_starting_share_disclosure(
                ingredient_count=len(recipe_b.ingredients),
                rank=selection_b.rank,
                latent_share=recipe_b.ingredients[selection_b.rank - 1].share,
                regime=regime,
            )
            keys = {
                ingredient.factor_key
                for recipe in (recipe_a, recipe_b)
                for ingredient in recipe.ingredients
            }
            state = Stage26PairState(
                Stage26FoodState(
                    recipe_a.recipe_id,
                    tuple(ingredient.factor_key for ingredient in recipe_a.ingredients),
                    selection_a.rank,
                    disclosure_a.interval,
                ),
                Stage26FoodState(
                    recipe_b.recipe_id,
                    tuple(ingredient.factor_key for ingredient in recipe_b.ingredients),
                    selection_b.rank,
                    disclosure_b.interval,
                ),
                {key: m2.intervals[key] for key in keys},
                frozenset(),
                2,
            )
            states.append((pair_index, regime, state))
    return states


def test_optimized_oasa_matches_reference_on_ten_training_guan_states(
    guan_policy_states,
) -> None:
    # Four full initial states validate first-action parity. Six additional
    # post-first-observation states validate conditional final-action parity.
    initial_states = guan_policy_states[:4]
    compared = 0
    branches = []
    for _, regime, state in initial_states:
        optimized = OasaTwoStep(PolicyComputationCache(enabled=True))
        reference = OasaTwoStep(PolicyComputationCache(enabled=False))
        optimized_first = optimized.choose_action(state, regime)
        reference_first = reference.choose_action(state, regime)
        _assert_decision_parity(optimized_first, reference_first)
        compared += 1
        if optimized_first is not None:
            nodes = expectation_nodes(state, optimized_first.action)
            for node in nodes[:6]:
                branches.append(
                    (
                        regime,
                        apply_observation(
                            state, optimized_first.action.acquisition, node.value
                        ),
                    )
                )

    for regime, branch in branches[:6]:
        _assert_decision_parity(
            OasaTwoStep(PolicyComputationCache(enabled=True)).choose_action(
                branch, regime
            ),
            OasaTwoStep(PolicyComputationCache(enabled=False)).choose_action(
                branch, regime
            ),
        )
        compared += 1

    assert compared == 10
