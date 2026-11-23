"""Normalized dataFIELD factor observations with formula provenance."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum

from .workbook import WorkbookSource

DATAFIELD_FACTOR_SHEET = "FCID linkages"
DATAFIELD_FACTOR_HEADER_ROW = 3


class NumericValueStatus(StrEnum):
    """Availability and validity of a numeric source value."""

    PRESENT = "PRESENT"
    MISSING = "MISSING"
    INVALID = "INVALID"


@dataclass(frozen=True, slots=True)
class DatafieldFactorObservation:
    """One FCID-linkage factor row and its stored workbook statistics."""

    factor_id: str | None
    source_fcid_code: object
    description: str | None
    weight_basis: str | None
    factor_kg_co2e_per_kg: Decimal | None
    factor_value_status: NumericValueStatus
    observation_count: Decimal | None
    mean: Decimal | None
    minimum: None
    maximum: None
    standard_deviation: Decimal | None
    scaled_standard_deviation: Decimal | None
    scaled_sd_status: NumericValueStatus
    proxy_or_category: str | None
    linkage_source: str | None
    gate_code: object
    factor_formula: str | None
    min_max_status: str
    source_file: str
    source_sheet: str
    source_row: int
    source_values: tuple[object, ...]
    cached_values: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class NormalizedDatafieldFactors:
    """Factor observations plus an audit of blank formatted source rows."""

    source_file: str
    factors: tuple[DatafieldFactorObservation, ...]
    source_rows_examined: int
    blank_source_rows: tuple[int, ...]


def canonical_fcid_code(value: object) -> str | None:
    """Canonicalize an FCID identifier without guessing or padding digits."""

    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not value.is_integer():
            return None
        return str(int(value))
    if isinstance(value, Decimal):
        if not value.is_finite() or value != value.to_integral_value():
            return None
        return str(int(value))
    return None


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value if value.strip() else None
    return str(value)


def _decimal_value(value: object) -> tuple[Decimal | None, NumericValueStatus]:
    if value is None or value == "":
        return None, NumericValueStatus.MISSING
    if isinstance(value, bool):
        return None, NumericValueStatus.INVALID
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None, NumericValueStatus.INVALID
    if not result.is_finite():
        return None, NumericValueStatus.INVALID
    return result, NumericValueStatus.PRESENT


def normalize_datafield_factors(
    formula_source: WorkbookSource,
    cached_source: WorkbookSource,
) -> NormalizedDatafieldFactors:
    """Extract FCID-linkage factors while retaining formulas and stored values.

    ``formula_source`` must be loaded with ``data_only=False`` and
    ``cached_source`` from the same file with ``data_only=True``. Excel is not
    recalculated; the latter exposes only values already stored in the source
    workbook. Minima and maxima are explicit ``None`` because those statistics
    are not present on the FCID-linkage sheet and no category mapping is
    inferred from the separate pivot sheets.
    """

    if formula_source.data_only:
        raise ValueError("formula_source must be loaded with data_only=False")
    if not cached_source.data_only:
        raise ValueError("cached_source must be loaded with data_only=True")
    if formula_source.path.resolve() != cached_source.path.resolve():
        raise ValueError("formula and cached sources must refer to the same file")

    formula_sheet = formula_source.sheet(DATAFIELD_FACTOR_SHEET)
    cached_sheet = cached_source.sheet(DATAFIELD_FACTOR_SHEET)
    if (
        formula_sheet.max_row != cached_sheet.max_row
        or formula_sheet.max_column != cached_sheet.max_column
    ):
        raise ValueError("formula and cached factor sheets have different dimensions")

    factors: list[DatafieldFactorObservation] = []
    blank_rows: list[int] = []
    first_data_row = DATAFIELD_FACTOR_HEADER_ROW + 1
    for source_row in range(first_data_row, formula_sheet.max_row + 1):
        formula_values = formula_sheet.row(source_row)
        cached_values = cached_sheet.row(source_row)
        source_code = formula_values[0]
        factor_id = canonical_fcid_code(source_code)
        if factor_id is None and source_code in {None, ""}:
            blank_rows.append(source_row)
            continue

        cached_id = canonical_fcid_code(cached_values[0])
        if factor_id != cached_id:
            raise ValueError(
                f"formula/cached FCID code mismatch at row {source_row}: "
                f"{factor_id!r} != {cached_id!r}"
            )

        factor_value, factor_status = _decimal_value(cached_values[6])
        observation_count, _ = _decimal_value(cached_values[16])
        mean, _ = _decimal_value(cached_values[17])
        standard_deviation, _ = _decimal_value(cached_values[18])
        scaled_sd, scaled_sd_status = _decimal_value(cached_values[31])
        formula = formula_values[6]
        factors.append(
            DatafieldFactorObservation(
                factor_id=factor_id,
                source_fcid_code=source_code,
                description=_optional_text(formula_values[1]),
                weight_basis=_optional_text(formula_values[2]),
                factor_kg_co2e_per_kg=factor_value,
                factor_value_status=factor_status,
                observation_count=observation_count,
                mean=mean,
                minimum=None,
                maximum=None,
                standard_deviation=standard_deviation,
                scaled_standard_deviation=scaled_sd,
                scaled_sd_status=scaled_sd_status,
                proxy_or_category=_optional_text(cached_values[27]),
                linkage_source=_optional_text(formula_values[8]),
                gate_code=formula_values[9],
                factor_formula=(
                    formula
                    if isinstance(formula, str) and formula.startswith("=")
                    else None
                ),
                min_max_status="NOT_PRESENT_ON_FCID_LINKAGE_SHEET",
                source_file=str(formula_source.path),
                source_sheet=DATAFIELD_FACTOR_SHEET,
                source_row=source_row,
                source_values=formula_values,
                cached_values=cached_values,
            )
        )

    return NormalizedDatafieldFactors(
        source_file=str(formula_source.path),
        factors=tuple(factors),
        source_rows_examined=max(0, formula_sheet.max_row - first_data_row + 1),
        blank_source_rows=tuple(blank_rows),
    )
