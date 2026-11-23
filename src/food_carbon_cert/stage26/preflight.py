"""Frozen Stage-26 preflight geometry, worlds, and LOCO folds."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from itertools import combinations
from pathlib import Path

from food_carbon_cert.disclosure import ShareInterval
from food_carbon_cert.uncertainty import FactorInterval

from .cohort import GuanRecipe

WORLD_SEEDS = tuple(range(26000, 26100))


class StartingShareRegime(StrEnum):
    """Frozen Stage-26 starting share-information regimes."""

    ORDER_ONLY = "ORDER_ONLY"
    PLUS_MINUS_5PP = "PLUS_MINUS_5PP"
    PLUS_MINUS_2PP = "PLUS_MINUS_2PP"
    PLUS_MINUS_1PP = "PLUS_MINUS_1PP"

    @property
    def delta(self) -> Decimal | None:
        return {
            StartingShareRegime.ORDER_ONLY: None,
            StartingShareRegime.PLUS_MINUS_5PP: Decimal("0.05"),
            StartingShareRegime.PLUS_MINUS_2PP: Decimal("0.02"),
            StartingShareRegime.PLUS_MINUS_1PP: Decimal("0.01"),
        }[self]


@dataclass(frozen=True, slots=True)
class ShareRankSelection:
    """One leakage-free selected ingredient rank."""

    rank: int
    factor_key: str
    factor_midpoint: Decimal
    feasible_share_width: Decimal
    score: Decimal


@dataclass(frozen=True, slots=True)
class StartingShareDisclosure:
    """One initial disclosure generated from a rounded publication."""

    regime: StartingShareRegime
    rank: int
    latent_share: Decimal
    published_share: Decimal | None
    interval: ShareInterval


@dataclass(frozen=True, slots=True)
class RecipePair:
    """One frozen within-cuisine recipe pair."""

    pair_id: str
    cuisine: str
    recipe_a_id: str
    recipe_b_id: str


@dataclass(frozen=True, slots=True)
class LocoFold:
    """One leave-one-cuisine-out fold."""

    held_out_cuisine: str
    training_recipe_ids: frozenset[str]
    held_out_recipe_ids: frozenset[str]
    training_pair_ids: frozenset[str]
    held_out_pair_ids: frozenset[str]


def exact_rank_feasible_interval(
    ingredient_count: int, rank: int
) -> tuple[Decimal, Decimal]:
    """Return exact-decimal order-only geometry for a one-based rank."""

    if isinstance(ingredient_count, bool) or ingredient_count < 1:
        raise ValueError("ingredient_count must be positive")
    if isinstance(rank, bool) or not 1 <= rank <= ingredient_count:
        raise ValueError("rank must lie within the ingredient count")
    lower = Decimal(1) / Decimal(ingredient_count) if rank == 1 else Decimal(0)
    upper = Decimal(1) / Decimal(rank)
    return lower, upper


def select_share_rank(
    factor_keys: Sequence[str],
    factor_intervals: Mapping[str, FactorInterval],
) -> ShareRankSelection:
    """Select one rank without accepting or reading latent recipe shares."""

    if not factor_keys:
        raise ValueError("at least one factor key is required")
    selections: list[ShareRankSelection] = []
    count = len(factor_keys)
    for rank, key in enumerate(factor_keys, start=1):
        try:
            interval = factor_intervals[key]
        except KeyError as error:
            raise KeyError(f"missing factor interval for key {key!r}") from error
        midpoint = (Decimal(str(interval.lower)) + Decimal(str(interval.upper))) / 2
        lower, upper = exact_rank_feasible_interval(count, rank)
        width = upper - lower
        selections.append(
            ShareRankSelection(rank, key, midpoint, width, midpoint * width)
        )
    return max(selections, key=lambda selection: (selection.score, -selection.rank))


def select_recipe_share_rank(
    recipe: GuanRecipe,
    factor_intervals: Mapping[str, FactorInterval],
) -> ShareRankSelection:
    """Select a recipe rank from identities and intervals only."""

    return select_share_rank(
        tuple(ingredient.factor_key for ingredient in recipe.ingredients),
        factor_intervals,
    )


def _round_positive_half_up(value: Decimal, grid: Decimal) -> Decimal:
    units = (value / grid).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return units * grid


def make_starting_share_disclosure(
    *,
    ingredient_count: int,
    rank: int,
    latent_share: Decimal,
    regime: StartingShareRegime,
) -> StartingShareDisclosure:
    """Generate and invert one frozen rounded starting disclosure."""

    feasible_lower, feasible_upper = exact_rank_feasible_interval(
        ingredient_count, rank
    )
    if not feasible_lower <= latent_share <= feasible_upper:
        raise ValueError("latent share lies outside selected-rank geometry")

    delta = regime.delta
    if delta is None:
        return StartingShareDisclosure(
            regime,
            rank,
            latent_share,
            None,
            ShareInterval(feasible_lower, feasible_upper),
        )

    grid = Decimal(2) * delta
    published = _round_positive_half_up(latent_share, grid)
    lower = max(Decimal(0), published - delta, feasible_lower)
    upper = min(Decimal(1), published + delta, feasible_upper)
    upper_included = upper != published + delta
    interval = ShareInterval(
        lower,
        upper,
        lower_included=True,
        upper_included=upper_included,
    )
    if not interval.contains(latent_share):
        raise ValueError("rounded starting disclosure does not contain latent truth")
    return StartingShareDisclosure(regime, rank, latent_share, published, interval)


def generate_factor_world(
    factor_intervals: Mapping[str, FactorInterval], seed: int
) -> dict[str, float]:
    """Generate one deterministic world with a single value per shared key."""

    generator = random.Random(seed)
    world: dict[str, float] = {}
    for key in sorted(factor_intervals):
        interval = factor_intervals[key]
        draw = generator.random()
        world[key] = interval.lower + draw * (interval.upper - interval.lower)
    return world


def generate_frozen_factor_worlds(
    factor_intervals: Mapping[str, FactorInterval],
) -> dict[int, dict[str, float]]:
    """Generate exactly the 100 frozen worlds for seeds 26000 through 26099."""

    return {seed: generate_factor_world(factor_intervals, seed) for seed in WORLD_SEEDS}


def write_factor_worlds(
    worlds: Mapping[int, Mapping[str, float]], path: str | Path
) -> None:
    """Write local generated worlds as a deterministic JSON artifact."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        str(seed): {key: world[key] for key in sorted(world)}
        for seed, world in sorted(worlds.items())
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def build_within_cuisine_pairs(
    recipes: Sequence[GuanRecipe],
) -> tuple[RecipePair, ...]:
    """Construct all unordered pairs within each cuisine."""

    by_cuisine: defaultdict[str, list[GuanRecipe]] = defaultdict(list)
    for recipe in recipes:
        by_cuisine[recipe.cuisine].append(recipe)

    pairs: list[RecipePair] = []
    for cuisine in sorted(by_cuisine):
        ordered = sorted(by_cuisine[cuisine], key=lambda recipe: recipe.recipe_id)
        for recipe_a, recipe_b in combinations(ordered, 2):
            pair_id = f"{recipe_a.recipe_id}:{recipe_b.recipe_id}"
            pairs.append(
                RecipePair(
                    pair_id,
                    cuisine,
                    recipe_a.recipe_id,
                    recipe_b.recipe_id,
                )
            )
    return tuple(pairs)


def build_loco_folds(
    recipes: Sequence[GuanRecipe], pairs: Sequence[RecipePair]
) -> tuple[LocoFold, ...]:
    """Construct deterministic leave-one-cuisine-out folds."""

    cuisines = sorted({recipe.cuisine for recipe in recipes})
    folds: list[LocoFold] = []
    for cuisine in cuisines:
        held_out_recipes = frozenset(
            recipe.recipe_id for recipe in recipes if recipe.cuisine == cuisine
        )
        training_recipes = frozenset(
            recipe.recipe_id for recipe in recipes if recipe.cuisine != cuisine
        )
        held_out_pairs = frozenset(
            pair.pair_id for pair in pairs if pair.cuisine == cuisine
        )
        training_pairs = frozenset(
            pair.pair_id for pair in pairs if pair.cuisine != cuisine
        )
        folds.append(
            LocoFold(
                cuisine,
                training_recipes,
                held_out_recipes,
                training_pairs,
                held_out_pairs,
            )
        )
    return tuple(folds)
