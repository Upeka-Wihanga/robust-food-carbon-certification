"""Transparent FCID recipe normalization with row-level provenance."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from .fcid import FcidSource

EXPECTED_FCID_RECIPE_TOTAL = Decimal("100")


class LinkageStatus(StrEnum):
    """Availability of an FCID commodity linkage."""

    LINKED = "LINKED"
    MISSING_COMMODITY_CODE = "MISSING_COMMODITY_CODE"


class CompositionStatus(StrEnum):
    """Validity of a source commodity-weight value."""

    VALID = "VALID"
    MISSING = "MISSING"
    INVALID = "INVALID"
    NEGATIVE = "NEGATIVE"


class RecipeNormalizationStatus(StrEnum):
    """Whether a complete recipe could be normalized to unit mass."""

    NORMALIZED = "NORMALIZED"
    MISSING_COMPOSITION = "MISSING_COMPOSITION"
    INVALID_COMPOSITION = "INVALID_COMPOSITION"
    NONPOSITIVE_TOTAL = "NONPOSITIVE_TOTAL"


@dataclass(frozen=True, slots=True)
class NormalizedFcidIngredient:
    """One source ingredient row and its explicit derived share."""

    food_code: str
    mod_code: str
    ingredient_number: int | None
    rank: int
    ingredient_description: None
    description_status: str
    fcid_code: str | None
    raw_fcid_code: str
    linkage_status: LinkageStatus
    commodity_weight: Decimal | None
    raw_commodity_weight: str
    composition_status: CompositionStatus
    normalized_share: Decimal | None
    cooked_status: str | None
    food_form: str | None
    cooking_method: str | None
    csfii_9498_indicator: str | None
    wweia_9904_indicator: str | None
    wweia_0510_indicator: str | None
    source_file: str
    source_row: int
    source_values: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NormalizedFcidRecipe:
    """All FCID rows for one food/modification key in source order."""

    food_code: str
    mod_code: str
    ingredients: tuple[NormalizedFcidIngredient, ...]
    ordering_valid: bool
    known_weight_total: Decimal
    source_total: Decimal | None
    expected_source_total: Decimal
    source_total_matches_expected: bool
    normalization_status: RecipeNormalizationStatus


@dataclass(frozen=True, slots=True)
class NormalizedFcid:
    """Normalized FCID recipes with no source rows dropped."""

    source_file: str
    recipes: tuple[NormalizedFcidRecipe, ...]

    @property
    def food_count(self) -> int:
        """Return the number of distinct Food_Code values."""

        return len({recipe.food_code for recipe in self.recipes})

    @property
    def ingredient_count(self) -> int:
        """Return the number of retained source ingredient rows."""

        return sum(len(recipe.ingredients) for recipe in self.recipes)


def _optional_source_text(value: str) -> str | None:
    return value if value.strip() else None


def _parse_ingredient_number(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def _parse_weight(value: str) -> tuple[Decimal | None, CompositionStatus]:
    if not value.strip():
        return None, CompositionStatus.MISSING
    try:
        result = Decimal(value)
    except InvalidOperation:
        return None, CompositionStatus.INVALID
    if not result.is_finite():
        return None, CompositionStatus.INVALID
    if result < 0:
        return result, CompositionStatus.NEGATIVE
    return result, CompositionStatus.VALID


def normalize_fcid(source: FcidSource) -> NormalizedFcid:
    """Group source rows and normalize every complete positive recipe.

    Recipe identity is the exact ``(Food_Code, Mod_Code)`` pair. Source order
    is retained. For a recipe where every ``Commodity_Weight`` is finite and
    nonnegative and their total is positive, shares use decimal
    ``Commodity_Weight / sum(Commodity_Weight)`` in source order. The final
    share is the deterministic residual ``1 - sum(previous shares)`` so the
    stored unit-mass composition sums exactly despite finite decimal division.
    Incomplete or invalid recipes retain every row but receive no shares.
    """

    indexes = {name: source.columns.index(name) for name in source.columns}
    grouped: dict[tuple[str, str], list[tuple[int, tuple[str, ...]]]] = {}
    for source_row, values in enumerate(source.rows, start=2):
        key = (
            values[indexes["Food_Code"]],
            values[indexes["Mod_Code"]],
        )
        grouped.setdefault(key, []).append((source_row, values))

    recipes: list[NormalizedFcidRecipe] = []
    for (food_code, mod_code), rows in grouped.items():
        parsed: list[
            tuple[
                int,
                tuple[str, ...],
                int | None,
                str,
                str | None,
                LinkageStatus,
                str,
                Decimal | None,
                CompositionStatus,
            ]
        ] = []
        known_total = Decimal("0")
        for source_row, values in rows:
            ingredient_number = _parse_ingredient_number(
                values[indexes["Ingredient_Num"]]
            )
            raw_code = values[indexes["FCID_Code"]]
            fcid_code = raw_code.strip() or None
            linkage_status = (
                LinkageStatus.LINKED
                if fcid_code is not None
                else LinkageStatus.MISSING_COMMODITY_CODE
            )
            raw_weight = values[indexes["Commodity_Weight"]]
            weight, composition_status = _parse_weight(raw_weight)
            if weight is not None and composition_status is CompositionStatus.VALID:
                known_total += weight
            parsed.append(
                (
                    source_row,
                    values,
                    ingredient_number,
                    raw_code,
                    fcid_code,
                    linkage_status,
                    raw_weight,
                    weight,
                    composition_status,
                )
            )

        statuses = [row[8] for row in parsed]
        if CompositionStatus.MISSING in statuses:
            normalization_status = RecipeNormalizationStatus.MISSING_COMPOSITION
        elif any(
            status in {CompositionStatus.INVALID, CompositionStatus.NEGATIVE}
            for status in statuses
        ):
            normalization_status = RecipeNormalizationStatus.INVALID_COMPOSITION
        elif known_total <= 0:
            normalization_status = RecipeNormalizationStatus.NONPOSITIVE_TOTAL
        else:
            normalization_status = RecipeNormalizationStatus.NORMALIZED

        complete_total = (
            known_total
            if normalization_status is RecipeNormalizationStatus.NORMALIZED
            else None
        )
        ingredient_numbers = [row[2] for row in parsed]
        ordering_valid = ingredient_numbers == list(range(1, len(parsed) + 1))
        normalized_shares: list[Decimal | None] = [None] * len(parsed)
        if normalization_status is RecipeNormalizationStatus.NORMALIZED:
            running_total = Decimal("0")
            for index, row in enumerate(parsed):
                weight = row[7]
                if weight is None:
                    raise AssertionError("normalized recipe contains a missing weight")
                share = (
                    Decimal("1") - running_total
                    if index == len(parsed) - 1
                    else weight / known_total
                )
                normalized_shares[index] = share
                running_total += share
        ingredients: list[NormalizedFcidIngredient] = []
        for rank, row in enumerate(parsed, start=1):
            (
                source_row,
                values,
                ingredient_number,
                raw_code,
                fcid_code,
                linkage_status,
                raw_weight,
                weight,
                composition_status,
            ) = row
            normalized_share = normalized_shares[rank - 1]
            ingredients.append(
                NormalizedFcidIngredient(
                    food_code=food_code,
                    mod_code=mod_code,
                    ingredient_number=ingredient_number,
                    rank=rank,
                    ingredient_description=None,
                    description_status="NOT_PRESENT_IN_FCID_SOURCE",
                    fcid_code=fcid_code,
                    raw_fcid_code=raw_code,
                    linkage_status=linkage_status,
                    commodity_weight=weight,
                    raw_commodity_weight=raw_weight,
                    composition_status=composition_status,
                    normalized_share=normalized_share,
                    cooked_status=_optional_source_text(
                        values[indexes["Cooked_Status"]]
                    ),
                    food_form=_optional_source_text(values[indexes["Food_Form"]]),
                    cooking_method=_optional_source_text(
                        values[indexes["Cooking_Method"]]
                    ),
                    csfii_9498_indicator=_optional_source_text(
                        values[indexes["CSFII_9498_IND"]]
                    ),
                    wweia_9904_indicator=_optional_source_text(
                        values[indexes["WWEIA_9904_IND"]]
                    ),
                    wweia_0510_indicator=_optional_source_text(
                        values[indexes["WWEIA_0510_IND"]]
                    ),
                    source_file=str(source.path),
                    source_row=source_row,
                    source_values=values,
                )
            )
        recipes.append(
            NormalizedFcidRecipe(
                food_code=food_code,
                mod_code=mod_code,
                ingredients=tuple(ingredients),
                ordering_valid=ordering_valid,
                known_weight_total=known_total,
                source_total=complete_total,
                expected_source_total=EXPECTED_FCID_RECIPE_TOTAL,
                source_total_matches_expected=(
                    complete_total == EXPECTED_FCID_RECIPE_TOTAL
                ),
                normalization_status=normalization_status,
            )
        )
    return NormalizedFcid(str(source.path), tuple(recipes))
