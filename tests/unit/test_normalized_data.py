from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from food_carbon_cert.data import (
    CompositionStatus,
    MappingStatus,
    NumericValueStatus,
    RecipeNormalizationStatus,
    audit_fcid_datafield_mapping,
    load_datafield,
    load_fcid,
    normalize_datafield_factors,
    normalize_fcid,
)

FIXTURES = Path(__file__).parents[1] / "fixtures" / "data"


def _normalized_fcid():
    source = load_fcid(FIXTURES / "synthetic_fcid_normalization.csv")
    return normalize_fcid(source)


def _normalized_datafield():
    path = FIXTURES / "synthetic_datafield_normalization.xlsx"
    formulas = load_datafield(path, data_only=False)
    cached = load_datafield(path, data_only=True)
    return normalize_datafield_factors(formulas, cached)


def test_fcid_grouping_order_and_source_provenance_are_preserved() -> None:
    normalized = _normalized_fcid()

    assert normalized.food_count == 4
    assert len(normalized.recipes) == 4
    assert normalized.ingredient_count == 6
    first = normalized.recipes[0]
    assert (first.food_code, first.mod_code) == ("001", "A")
    assert [ingredient.ingredient_number for ingredient in first.ingredients] == [
        1,
        2,
    ]
    assert [ingredient.rank for ingredient in first.ingredients] == [1, 2]
    assert first.ordering_valid
    assert first.ingredients[0].source_row == 2
    assert first.ingredients[0].source_values[0] == "001"
    assert first.ingredients[0].ingredient_description is None
    assert first.ingredients[0].description_status == "NOT_PRESENT_IN_FCID_SOURCE"
    assert not normalized.recipes[3].ordering_valid


def test_fcid_share_normalization_is_explicit_decimal_unit_mass() -> None:
    normalized = _normalized_fcid()

    first = normalized.recipes[0]
    assert first.source_total == Decimal("100")
    assert first.source_total_matches_expected
    assert [ingredient.normalized_share for ingredient in first.ingredients] == [
        Decimal("0.3"),
        Decimal("0.7"),
    ]

    second = normalized.recipes[1]
    assert second.source_total == Decimal("5")
    assert not second.source_total_matches_expected
    assert [ingredient.normalized_share for ingredient in second.ingredients] == [
        Decimal("0.4"),
        Decimal("0.6"),
    ]
    assert sum(
        ingredient.normalized_share or Decimal("0") for ingredient in second.ingredients
    ) == Decimal("1.0")


def test_fcid_missing_values_are_retained_without_invented_linkages() -> None:
    normalized = _normalized_fcid()

    missing_link = normalized.recipes[0].ingredients[1]
    assert missing_link.fcid_code is None
    assert missing_link.raw_fcid_code == ""

    incomplete = normalized.recipes[2]
    assert (
        incomplete.normalization_status is RecipeNormalizationStatus.MISSING_COMPOSITION
    )
    assert incomplete.ingredients[0].composition_status is CompositionStatus.MISSING
    assert incomplete.ingredients[0].normalized_share is None


def test_datafield_factor_extraction_preserves_statistics_and_provenance() -> None:
    normalized = _normalized_datafield()

    assert len(normalized.factors) == 4
    factor = normalized.factors[0]
    assert factor.factor_id == "100"
    assert factor.factor_kg_co2e_per_kg == Decimal("1.0")
    assert factor.observation_count == Decimal("2")
    assert factor.mean == Decimal("1.0")
    assert factor.standard_deviation == Decimal("0.1")
    assert factor.scaled_standard_deviation == Decimal("0.2")
    assert factor.minimum is None
    assert factor.maximum is None
    assert factor.min_max_status == "NOT_PRESENT_ON_FCID_LINKAGE_SHEET"
    assert factor.source_sheet == "FCID linkages"
    assert factor.source_row == 4
    assert factor.source_values[0] == 100
    assert factor.cached_values[6] == 1


def test_mapping_audit_retains_ambiguous_unmapped_and_invalid_cases() -> None:
    audit = audit_fcid_datafield_mapping(_normalized_fcid(), _normalized_datafield())

    assert audit.unique_fcid_code_count == 5
    assert audit.count(MappingStatus.DIRECT) == 1
    assert audit.count(MappingStatus.AMBIGUOUS) == 1
    assert audit.count(MappingStatus.UNMAPPED) == 2
    assert audit.count(MappingStatus.INVALID_FACTOR_VALUE) == 1
    assert audit.multiple_candidate_count == 1
    assert audit.missing_fcid_code_rows == 1

    by_code = {record.fcid_code: record for record in audit.records}
    assert by_code["101"].candidate_count == 2
    assert by_code["101"].candidate_source_rows == (5, 6)
    assert by_code["999"].candidate_count == 0
    invalid = next(
        factor
        for factor in _normalized_datafield().factors
        if factor.factor_id == "300"
    )
    assert invalid.factor_value_status is NumericValueStatus.MISSING
