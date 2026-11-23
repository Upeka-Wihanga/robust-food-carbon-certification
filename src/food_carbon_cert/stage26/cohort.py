"""Frozen Guan61 reconstruction and Stage-18 M2 factor construction.

This module implements a recovered project convention, not unavailable
historical source code. Ingredient quantities are parsed from their literal
workbook representation as :class:`~decimal.Decimal` values. The five-percent
source threshold is therefore tested without binary floating-point drift.
"""

from __future__ import annotations

import ast
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from food_carbon_cert.data.workbook import WorkbookSource
from food_carbon_cert.uncertainty import FactorInterval

MAJOR_SHARE_THRESHOLD = Decimal("0.05")
REPRODUCTION_ERROR_THRESHOLD = Decimal("0.01")
M2_RELATIVE_RADIUS = Decimal("0.25")
FROZEN_M2_P25 = Decimal("1.145000")
FROZEN_M2_P75 = Decimal("4.763000")

RECIPE_SHEET = "Recipe"
FACTOR_SHEET = "Greenhouse gas emission factors"


def normalize_guan_ingredient_name(name: str) -> str:
    """Return the shared Guan factor key for an ingredient name."""

    return " ".join(name.strip().casefold().split())


def _decimal_literal(node: ast.AST, source: str) -> Decimal:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        raise ValueError("ingredient quantity has no literal source segment")
    try:
        value = Decimal(segment)
    except InvalidOperation as error:
        raise ValueError("ingredient quantity is not a decimal literal") from error
    if not value.is_finite() or value < 0:
        raise ValueError("ingredient quantities must be finite and nonnegative")
    return value


def parse_guan_ingredient_dictionary(source: object) -> tuple[tuple[str, Decimal], ...]:
    """Parse one serialized ingredient dictionary using literal decimals.

    The source is required to be a Python dictionary literal with string keys
    and nonnegative decimal number literals. Python dictionary semantics are
    retained: a repeated key keeps its first position and its last value.
    """

    if not isinstance(source, str):
        raise ValueError("ingredient dictionary must be source text")
    try:
        expression = ast.parse(source, mode="eval").body
    except (SyntaxError, ValueError) as error:
        raise ValueError("ingredient dictionary is not parseable") from error
    if not isinstance(expression, ast.Dict):
        raise ValueError("ingredient source must be a dictionary literal")

    ordered_names: list[str] = []
    values: dict[str, Decimal] = {}
    for key_node, value_node in zip(expression.keys, expression.values, strict=True):
        if not isinstance(key_node, ast.Constant) or not isinstance(
            key_node.value, str
        ):
            raise ValueError("ingredient names must be string literals")
        name = key_node.value
        if name not in values:
            ordered_names.append(name)
        values[name] = _decimal_literal(value_node, source)
    if not ordered_names:
        raise ValueError("ingredient dictionary must not be empty")
    return tuple((name, values[name]) for name in ordered_names)


def is_major_source_ingredient(weight: Decimal, recipe_total: Decimal) -> bool:
    """Apply the exact frozen five-percent source threshold."""

    if recipe_total <= 0:
        raise ValueError("recipe total must be positive")
    if weight < 0:
        raise ValueError("ingredient weight must be nonnegative")
    return weight >= MAJOR_SHARE_THRESHOLD * recipe_total


@dataclass(frozen=True, slots=True)
class GuanFactor:
    """One unique normalized Guan production-factor mapping."""

    key: str
    production_factor: Decimal
    source_rows: tuple[int, ...]
    source_names: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GuanFactorTable:
    """Normalized direct factors and ambiguous normalized names."""

    factors: Mapping[str, GuanFactor]
    ambiguous_keys: frozenset[str]
    positive_observations: tuple[Decimal, ...]


@dataclass(frozen=True, slots=True)
class GuanIngredient:
    """One parsed Guan ingredient in source order."""

    name: str
    weight_g: Decimal
    share: Decimal
    rank: int
    factor_key: str
    direct_factor: Decimal | None
    is_major: bool


@dataclass(frozen=True, slots=True)
class GuanRecipe:
    """One parseable Guan recipe and its reconstruction audit."""

    recipe_id: str
    source_row: int
    english_name: str
    chinese_name: str | None
    cuisine: str
    ingredient_source: str
    ingredients: tuple[GuanIngredient, ...]
    parsed_total_g: Decimal
    published_production_gco2e: Decimal
    reconstructed_production_gco2e: Decimal
    relative_reproduction_error: Decimal
    all_major_ingredients_mapped: bool
    eligible: bool


@dataclass(frozen=True, slots=True)
class GuanCohort:
    """Complete source audit plus the frozen eligible cohort."""

    source_row_count: int
    parseable_recipes: tuple[GuanRecipe, ...]
    eligible_recipes: tuple[GuanRecipe, ...]

    @property
    def parseable_count(self) -> int:
        return len(self.parseable_recipes)

    @property
    def eligible_count(self) -> int:
        return len(self.eligible_recipes)

    @property
    def cuisine_counts(self) -> dict[str, int]:
        return dict(
            sorted(Counter(recipe.cuisine for recipe in self.eligible_recipes).items())
        )

    @property
    def pair_count(self) -> int:
        return sum(count * (count - 1) // 2 for count in self.cuisine_counts.values())


@dataclass(frozen=True, slots=True)
class M2FactorModel:
    """Shared M2 factor intervals and construction counts."""

    intervals: Mapping[str, FactorInterval]
    p25: Decimal
    p75: Decimal
    direct_occurrence_count: int
    fallback_occurrence_count: int
    direct_key_count: int
    fallback_key_count: int


def _headers(sheet_rows: tuple[tuple[object, ...], ...]) -> dict[str, int]:
    return {str(value): index for index, value in enumerate(sheet_rows[0])}


def _required_value(row: tuple[object, ...], index: int, label: str) -> object:
    value = row[index]
    if value is None:
        raise ValueError(f"missing required Guan value: {label}")
    return value


def normalize_guan_factor_table(source: WorkbookSource) -> GuanFactorTable:
    """Normalize the Guan production-factor table by ingredient name."""

    sheet = source.sheet(FACTOR_SHEET)
    headers = _headers(sheet.rows)
    name_index = headers["Ingredient "]
    factor_index = headers["Greenhouse gas emission factors (kgCO2e/kg)_production"]

    grouped: defaultdict[str, list[tuple[int, str, Decimal]]] = defaultdict(list)
    for source_row, row in enumerate(sheet.rows[1:], start=2):
        raw_name = row[name_index]
        raw_factor = row[factor_index]
        if raw_name is None and raw_factor is None:
            continue
        if not isinstance(raw_name, str):
            raise ValueError(f"invalid Guan factor name at row {source_row}")
        try:
            factor = Decimal(str(raw_factor))
        except InvalidOperation as error:
            raise ValueError(
                f"invalid Guan production factor at row {source_row}"
            ) from error
        if not factor.is_finite() or factor < 0:
            raise ValueError(
                f"Guan production factor must be finite and nonnegative at row "
                f"{source_row}"
            )
        grouped[normalize_guan_ingredient_name(raw_name)].append(
            (source_row, raw_name, factor)
        )

    factors: dict[str, GuanFactor] = {}
    ambiguous: set[str] = set()
    positive: list[Decimal] = []
    for key, observations in grouped.items():
        values = {factor for _, _, factor in observations}
        if len(values) != 1:
            ambiguous.add(key)
            continue
        factor = next(iter(values))
        factors[key] = GuanFactor(
            key=key,
            production_factor=factor,
            source_rows=tuple(row for row, _, _ in observations),
            source_names=tuple(name for _, name, _ in observations),
        )
        if factor > 0:
            positive.append(factor)
    return GuanFactorTable(factors, frozenset(ambiguous), tuple(positive))


def _recipe_identifier(
    source_row: int,
    english_name: str,
    chinese_name: str | None,
    cuisine: str,
    ingredient_source: str,
) -> str:
    payload = json.dumps(
        {
            "sheet": RECIPE_SHEET,
            "row": source_row,
            "english_name": english_name,
            "chinese_name": chinese_name,
            "cuisine": cuisine,
            "ingredient_source": ingredient_source,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def reconstruct_guan_cohort(
    source: WorkbookSource,
    *,
    factors: GuanFactorTable | None = None,
) -> GuanCohort:
    """Reconstruct the frozen Guan cohort with exact threshold semantics."""

    factor_table = normalize_guan_factor_table(source) if factors is None else factors
    sheet = source.sheet(RECIPE_SHEET)
    headers = _headers(sheet.rows)
    english_index = headers["Recipe English name"]
    chinese_index = headers["Recipe Chinese name"]
    cuisine_index = headers["Cuisine"]
    ingredients_index = headers["Ingredient (g)"]
    production_index = headers["CF(gCO2e)_production"]

    source_row_count = 0
    parseable: list[GuanRecipe] = []
    for source_row, row in enumerate(sheet.rows[1:], start=2):
        if not any(value is not None for value in row):
            continue
        source_row_count += 1
        ingredient_source = row[ingredients_index]
        try:
            parsed = parse_guan_ingredient_dictionary(ingredient_source)
        except ValueError:
            continue
        total = sum((weight for _, weight in parsed), Decimal("0"))
        if total <= 0:
            continue

        english_name = str(_required_value(row, english_index, "Recipe English name"))
        chinese_value = row[chinese_index]
        chinese_name = None if chinese_value is None else str(chinese_value)
        cuisine = str(_required_value(row, cuisine_index, "Cuisine"))
        published = Decimal(
            str(_required_value(row, production_index, "CF(gCO2e)_production"))
        )
        if not published.is_finite() or published == 0:
            raise ValueError(
                f"invalid published Guan production total at row {source_row}"
            )

        ingredients: list[GuanIngredient] = []
        reconstructed = Decimal("0")
        all_major_mapped = True
        ordered_parsed = sorted(parsed, key=lambda item: item[1], reverse=True)
        for rank, (name, weight) in enumerate(ordered_parsed, start=1):
            key = normalize_guan_ingredient_name(name)
            direct = factor_table.factors.get(key)
            factor = None if direct is None else direct.production_factor
            major = is_major_source_ingredient(weight, total)
            if major:
                if factor is None:
                    all_major_mapped = False
                else:
                    reconstructed += weight * factor
            ingredients.append(
                GuanIngredient(
                    name=name,
                    weight_g=weight,
                    share=weight / total,
                    rank=rank,
                    factor_key=key,
                    direct_factor=factor,
                    is_major=major,
                )
            )

        relative_error = abs(reconstructed - published) / abs(published)
        eligible = all_major_mapped and relative_error <= REPRODUCTION_ERROR_THRESHOLD
        ingredient_text = str(ingredient_source)
        parseable.append(
            GuanRecipe(
                recipe_id=_recipe_identifier(
                    source_row,
                    english_name,
                    chinese_name,
                    cuisine,
                    ingredient_text,
                ),
                source_row=source_row,
                english_name=english_name,
                chinese_name=chinese_name,
                cuisine=cuisine,
                ingredient_source=ingredient_text,
                ingredients=tuple(ingredients),
                parsed_total_g=total,
                published_production_gco2e=published,
                reconstructed_production_gco2e=reconstructed,
                relative_reproduction_error=relative_error,
                all_major_ingredients_mapped=all_major_mapped,
                eligible=eligible,
            )
        )

    eligible_recipes = tuple(recipe for recipe in parseable if recipe.eligible)
    return GuanCohort(source_row_count, tuple(parseable), eligible_recipes)


def decimal_linear_percentile(
    observations: Iterable[Decimal], quantile: Decimal
) -> Decimal:
    """Return the conventional linearly interpolated sample percentile."""

    values = sorted(observations)
    if not values:
        raise ValueError("at least one percentile observation is required")
    if not Decimal("0") <= quantile <= Decimal("1"):
        raise ValueError("quantile must lie between zero and one")
    position = Decimal(len(values) - 1) * quantile
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(values) - 1)
    fraction = position - Decimal(lower_index)
    return values[lower_index] + fraction * (values[upper_index] - values[lower_index])


def build_m2_factor_model(
    recipes: Iterable[GuanRecipe],
    factor_table: GuanFactorTable,
) -> M2FactorModel:
    """Build frozen Stage-18 M2 intervals with shared normalized keys."""

    p25 = decimal_linear_percentile(factor_table.positive_observations, Decimal("0.25"))
    p75 = decimal_linear_percentile(factor_table.positive_observations, Decimal("0.75"))
    if p25 != FROZEN_M2_P25 or p75 != FROZEN_M2_P75:
        raise ValueError(
            "Guan positive-factor percentiles do not match frozen M2 values: "
            f"P25={p25}, P75={p75}"
        )

    intervals: dict[str, FactorInterval] = {}
    direct_occurrences = 0
    fallback_occurrences = 0
    direct_keys: set[str] = set()
    fallback_keys: set[str] = set()
    for recipe in recipes:
        for ingredient in recipe.ingredients:
            if ingredient.direct_factor is not None and ingredient.direct_factor > 0:
                center = ingredient.direct_factor
                lower = center * (Decimal("1") - M2_RELATIVE_RADIUS)
                upper = center * (Decimal("1") + M2_RELATIVE_RADIUS)
                interval = FactorInterval(float(lower), float(upper))
                direct_occurrences += 1
                direct_keys.add(ingredient.factor_key)
            else:
                interval = FactorInterval(float(p25), float(p75))
                fallback_occurrences += 1
                fallback_keys.add(ingredient.factor_key)

            previous = intervals.get(ingredient.factor_key)
            if previous is not None and previous != interval:
                raise ValueError(
                    "shared Guan factor key produced conflicting M2 intervals: "
                    f"{ingredient.factor_key!r}"
                )
            intervals[ingredient.factor_key] = interval

    overlap = direct_keys & fallback_keys
    if overlap:
        raise ValueError(f"factor keys cannot be both direct and fallback: {overlap}")
    return M2FactorModel(
        intervals=intervals,
        p25=p25,
        p75=p75,
        direct_occurrence_count=direct_occurrences,
        fallback_occurrence_count=fallback_occurrences,
        direct_key_count=len(direct_keys),
        fallback_key_count=len(fallback_keys),
    )


def write_cohort_manifest(cohort: GuanCohort, path: str | Path) -> None:
    """Write a local machine-readable eligible-cohort identity manifest."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "provenance": "RECOVERED_PROJECT_CONVENTION",
        "source_row_count": cohort.source_row_count,
        "parseable_count": cohort.parseable_count,
        "eligible_count": cohort.eligible_count,
        "cuisine_counts": cohort.cuisine_counts,
        "within_cuisine_pair_count": cohort.pair_count,
        "recipes": [
            {
                "recipe_id": recipe.recipe_id,
                "source_row": recipe.source_row,
                "english_name": recipe.english_name,
                "cuisine": recipe.cuisine,
            }
            for recipe in cohort.eligible_recipes
        ],
    }
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
