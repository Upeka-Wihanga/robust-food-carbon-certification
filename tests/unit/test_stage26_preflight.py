from __future__ import annotations

from collections import Counter
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from food_carbon_cert.data import load_guan, load_source_manifest
from food_carbon_cert.stage26 import (
    FROZEN_M2_P25,
    FROZEN_M2_P75,
    WORLD_SEEDS,
    StartingShareRegime,
    build_loco_folds,
    build_m2_factor_model,
    build_within_cuisine_pairs,
    generate_factor_world,
    generate_frozen_factor_worlds,
    make_starting_share_disclosure,
    normalize_guan_factor_table,
    reconstruct_guan_cohort,
    select_recipe_share_rank,
    select_share_rank,
)
from food_carbon_cert.uncertainty import FactorInterval

PROJECT_ROOT = Path(__file__).parents[2]
RAW_GUAN = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "Carbon footprint and nutrition estimation of Chinese cuisines.xlsx"
)


@pytest.fixture(scope="module")
def frozen_guan():
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
    return cohort, factors, m2


def test_frozen_guan61_reconstruction(frozen_guan) -> None:
    cohort, _, _ = frozen_guan

    assert cohort.source_row_count == 320
    assert cohort.parseable_count == 308
    assert cohort.eligible_count == 61
    assert cohort.cuisine_counts == {
        "Chuan Cuisine": 6,
        "Hui Cuisine": 12,
        "Lu Cuisine": 8,
        "Min Cuisine": 5,
        "Su Cuisine": 6,
        "Xiang Cuisine": 8,
        "Yue Cuisine": 10,
        "Zhe Cuisine": 6,
    }
    assert cohort.pair_count == 222


def test_sanhe_and_sweet_barbecue_regressions(frozen_guan) -> None:
    cohort, _, _ = frozen_guan
    recipes = {recipe.english_name: recipe for recipe in cohort.parseable_recipes}

    sanhe = recipes["Sanhe Rice Dumplings"]
    assert sanhe.parsed_total_g == Decimal("300.0")
    assert not sanhe.eligible
    pork = next(item for item in sanhe.ingredients if item.name == "Pork")
    assert pork.weight_g == Decimal("15.0")
    assert pork.is_major

    sweet = recipes["Sweet Barbecue Pork"]
    assert sweet.parsed_total_g == Decimal("300.2")
    assert not sweet.eligible
    sugar = next(item for item in sweet.ingredients if item.name == "Sugar")
    assert sugar.weight_g == Decimal("15.0")
    assert not sugar.is_major


def test_frozen_m2_construction_and_shared_identity(frozen_guan) -> None:
    cohort, _, m2 = frozen_guan

    assert m2.p25 == FROZEN_M2_P25
    assert m2.p75 == FROZEN_M2_P75
    assert len(m2.intervals) == 210
    assert m2.direct_key_count == 105
    assert m2.fallback_key_count == 105
    assert m2.direct_occurrence_count == 404
    assert m2.fallback_occurrence_count == 227
    assert sum(len(recipe.ingredients) for recipe in cohort.eligible_recipes) == 631

    occurrences: dict[str, FactorInterval] = {}
    for recipe in cohort.eligible_recipes:
        for ingredient in recipe.ingredients:
            interval = m2.intervals[ingredient.factor_key]
            assert occurrences.setdefault(ingredient.factor_key, interval) == interval


def test_rank_selection_uses_frozen_score_and_lowest_rank_tie_break() -> None:
    intervals = {
        "a": FactorInterval(3.0, 5.0),
        "b": FactorInterval(1.0, 3.0),
    }
    selection = select_share_rank(("a", "b"), intervals)

    assert selection.rank == 1
    assert selection.score == Decimal("2.00")

    tied = {
        "a": FactorInterval(2.0, 2.0),
        "b": FactorInterval(2.0, 2.0),
    }
    assert select_share_rank(("a", "b"), tied).rank == 1


def test_rank_selection_does_not_read_hidden_recipe_shares(frozen_guan) -> None:
    cohort, _, m2 = frozen_guan
    recipe = cohort.eligible_recipes[0]
    changed_ingredients = tuple(
        replace(
            ingredient,
            weight_g=Decimal(index + 1),
            share=Decimal(index + 1) / Decimal(len(recipe.ingredients) + 1),
        )
        for index, ingredient in enumerate(recipe.ingredients)
    )
    hidden_truth_changed = replace(recipe, ingredients=changed_ingredients)

    assert select_recipe_share_rank(recipe, m2.intervals) == select_recipe_share_rank(
        hidden_truth_changed, m2.intervals
    )


def test_all_starting_disclosures_contain_latent_truth(frozen_guan) -> None:
    cohort, _, m2 = frozen_guan
    failures: list[tuple[str, StartingShareRegime]] = []

    for recipe in cohort.eligible_recipes:
        selection = select_recipe_share_rank(recipe, m2.intervals)
        latent = recipe.ingredients[selection.rank - 1].share
        for regime in StartingShareRegime:
            disclosure = make_starting_share_disclosure(
                ingredient_count=len(recipe.ingredients),
                rank=selection.rank,
                latent_share=latent,
                regime=regime,
            )
            if not disclosure.interval.contains(latent):
                failures.append((recipe.recipe_id, regime))

    assert failures == []


def test_half_up_starting_disclosure_is_not_centered_on_hidden_truth() -> None:
    disclosure = make_starting_share_disclosure(
        ingredient_count=4,
        rank=1,
        latent_share=Decimal("0.349"),
        regime=StartingShareRegime.PLUS_MINUS_5PP,
    )

    assert disclosure.published_share == Decimal("0.3")
    assert disclosure.interval.lower == Decimal("0.25")
    assert disclosure.interval.upper == Decimal("0.35")
    assert disclosure.interval.contains(Decimal("0.349"))


def test_frozen_factor_worlds_are_deterministic_and_contained(frozen_guan) -> None:
    _, _, m2 = frozen_guan
    worlds = generate_frozen_factor_worlds(m2.intervals)

    assert tuple(worlds) == WORLD_SEEDS
    assert len(worlds) == 100
    assert worlds[26000] == generate_factor_world(m2.intervals, 26000)
    assert worlds == generate_frozen_factor_worlds(m2.intervals)
    assert all(
        m2.intervals[key].lower <= value <= m2.intervals[key].upper
        for world in worlds.values()
        for key, value in world.items()
    )


def test_loco_folds_are_group_disjoint_and_partition_all_pairs(frozen_guan) -> None:
    cohort, _, _ = frozen_guan
    pairs = build_within_cuisine_pairs(cohort.eligible_recipes)
    folds = build_loco_folds(cohort.eligible_recipes, pairs)

    assert len(pairs) == 222
    assert len(folds) == 8
    assert len({fold.held_out_cuisine for fold in folds}) == 8
    assert all(
        fold.training_recipe_ids.isdisjoint(fold.held_out_recipe_ids) for fold in folds
    )
    held_out_pair_counts = Counter(
        pair_id for fold in folds for pair_id in fold.held_out_pair_ids
    )
    assert set(held_out_pair_counts) == {pair.pair_id for pair in pairs}
    assert set(held_out_pair_counts.values()) == {1}
