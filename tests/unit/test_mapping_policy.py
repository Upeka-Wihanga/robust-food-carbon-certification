from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from food_carbon_cert.data import (
    FCID_REQUIRED_COLUMNS,
    DatafieldFactorObservation,
    FcidSource,
    MappingPolicy,
    MappingStatus,
    NormalizedDatafieldFactors,
    NumericValueStatus,
    audit_fcid_datafield_mapping,
    normalize_fcid,
)
from food_carbon_cert.data.babyfood_mapping import (
    CONFIRMED_BABYFOOD_PARENT_MAP,
)


def _fcid(*codes: str):
    rows = tuple(
        (
            f"food-{index}",
            "0",
            "1",
            code,
            "1",
            "1",
            "1",
            "100",
            "1",
            "1",
            "1",
        )
        for index, code in enumerate(codes, start=1)
    )
    source = FcidSource(
        path=Path("synthetic-fcid.csv"),
        encoding="utf-8",
        columns=FCID_REQUIRED_COLUMNS,
        rows=rows,
        verification=None,
    )
    return normalize_fcid(source)


def _factor(code: str, source_row: int) -> DatafieldFactorObservation:
    return DatafieldFactorObservation(
        factor_id=code,
        source_fcid_code=code,
        description=f"synthetic factor {code}",
        weight_basis="synthetic mass",
        factor_kg_co2e_per_kg=Decimal("1"),
        factor_value_status=NumericValueStatus.PRESENT,
        observation_count=Decimal("5"),
        mean=Decimal("1"),
        minimum=None,
        maximum=None,
        standard_deviation=Decimal("0.1"),
        scaled_standard_deviation=Decimal("0.1"),
        scaled_sd_status=NumericValueStatus.PRESENT,
        proxy_or_category="DIRECT",
        linkage_source="synthetic",
        gate_code=1,
        factor_formula=None,
        min_max_status="NOT_PRESENT_ON_FCID_LINKAGE_SHEET",
        source_file="synthetic-datafield.xlsx",
        source_sheet="FCID linkages",
        source_row=source_row,
        source_values=(),
        cached_values=(),
    )


def _datafield(*codes: str) -> NormalizedDatafieldFactors:
    return NormalizedDatafieldFactors(
        source_file="synthetic-datafield.xlsx",
        factors=tuple(
            _factor(code, source_row) for source_row, code in enumerate(codes, start=4)
        ),
        source_rows_examined=len(codes),
        blank_source_rows=(),
    )


def _record(source_code: str, *factor_codes: str):
    audit = audit_fcid_datafield_mapping(
        _fcid(source_code),
        _datafield(*factor_codes),
        policy=MappingPolicy.EXACT_PLUS_CONFIRMED_BABYFOOD_PARENT,
    )
    return audit.records[0]


def test_exact_mapping_takes_precedence_over_confirmed_parent() -> None:
    source = "101050001"
    parent = CONFIRMED_BABYFOOD_PARENT_MAP[source]

    record = _record(source, source, parent)

    assert record.status is MappingStatus.EXACT_DATAFIELD
    assert record.mapped_fcid_code == source
    assert not record.weight_basis_warning


def test_confirmed_babyfood_variant_maps_to_explicit_parent() -> None:
    source = "101052001"
    parent = CONFIRMED_BABYFOOD_PARENT_MAP[source]

    record = _record(source, parent)

    assert record.status is MappingStatus.CONFIRMED_BABYFOOD_PARENT_PROXY
    assert record.mapped_fcid_code == parent
    assert record.mapping_policy is (MappingPolicy.EXACT_PLUS_CONFIRMED_BABYFOOD_PARENT)
    assert "New reconstructed policy" in record.mapping_reason


def test_exact_only_does_not_apply_confirmed_parent_policy() -> None:
    source = "101052001"
    audit = audit_fcid_datafield_mapping(
        _fcid(source),
        _datafield(CONFIRMED_BABYFOOD_PARENT_MAP[source]),
        policy=MappingPolicy.EXACT_ONLY,
    )

    assert audit.records[0].status is MappingStatus.UNMAPPED
    assert audit.records[0].mapped_fcid_code is None


def test_parent_mapping_preserves_original_fcid_code() -> None:
    source = "101052001"
    record = _record(source, CONFIRMED_BABYFOOD_PARENT_MAP[source])

    assert record.fcid_code == source
    assert record.mapped_fcid_code != record.fcid_code


def test_parentless_verified_exception_remains_unmapped() -> None:
    for source, hypothetical_parent in (
        ("3600225001", "3600225000"),
        ("3700222501", "3700222500"),
    ):
        record = _record(source, hypothetical_parent)
        assert record.status is MappingStatus.UNMAPPED
        assert record.mapped_fcid_code is None


def test_unknown_terminal_one_code_is_not_rewritten() -> None:
    record = _record("9999999991", "9999999990")

    assert record.status is MappingStatus.UNMAPPED
    assert record.mapped_fcid_code is None


def test_terminal_zero_unmapped_code_remains_unmapped() -> None:
    record = _record("101084000", "101078000")

    assert record.status is MappingStatus.UNMAPPED
    assert record.mapped_fcid_code is None


def test_confirmed_crosswalk_has_no_parent_collisions() -> None:
    parents = tuple(CONFIRMED_BABYFOOD_PARENT_MAP.values())

    assert len(CONFIRMED_BABYFOOD_PARENT_MAP) == 118
    assert len(set(parents)) == len(parents)


def test_weight_basis_warning_is_propagated_only_for_flagged_pair() -> None:
    warned_source = "101050001"
    ordinary_source = "101052001"
    audit = audit_fcid_datafield_mapping(
        _fcid(warned_source, ordinary_source),
        _datafield(
            CONFIRMED_BABYFOOD_PARENT_MAP[warned_source],
            CONFIRMED_BABYFOOD_PARENT_MAP[ordinary_source],
        ),
        policy=MappingPolicy.EXACT_PLUS_CONFIRMED_BABYFOOD_PARENT,
    )
    by_code = {record.fcid_code: record for record in audit.records}

    assert by_code[warned_source].weight_basis_warning
    assert not by_code[ordinary_source].weight_basis_warning
    assert audit.weight_basis_warning_count == 1
