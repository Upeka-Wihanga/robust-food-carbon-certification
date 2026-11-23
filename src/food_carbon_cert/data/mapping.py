"""Deterministic mapping audit between FCID ingredients and dataFIELD factors."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .datafield_normalized import (
    DatafieldFactorObservation,
    NormalizedDatafieldFactors,
    NumericValueStatus,
)
from .fcid_normalized import NormalizedFcid


class MappingStatus(StrEnum):
    """Unresolved or direct status of one unique FCID commodity code."""

    DIRECT = "DIRECT"
    UNMAPPED = "UNMAPPED"
    AMBIGUOUS = "AMBIGUOUS"
    INVALID_FACTOR_VALUE = "INVALID_FACTOR_VALUE"


@dataclass(frozen=True, slots=True)
class CommodityMappingRecord:
    """Mapping evidence for one unique nonmissing FCID commodity code."""

    fcid_code: str
    status: MappingStatus
    ingredient_row_count: int
    candidate_count: int
    candidate_source_rows: tuple[int, ...]
    candidate_descriptions: tuple[str | None, ...]


@dataclass(frozen=True, slots=True)
class MappingAudit:
    """Machine-readable mapping status table and source-level diagnostics."""

    records: tuple[CommodityMappingRecord, ...]
    missing_fcid_code_rows: int

    @property
    def unique_fcid_code_count(self) -> int:
        return len(self.records)

    def count(self, status: MappingStatus) -> int:
        """Count unique codes with one mapping status."""

        return sum(record.status is status for record in self.records)

    @property
    def multiple_candidate_count(self) -> int:
        """Count unique FCID codes with multiple candidate factor rows."""

        return sum(record.candidate_count > 1 for record in self.records)


def audit_fcid_datafield_mapping(
    fcid: NormalizedFcid,
    datafield: NormalizedDatafieldFactors,
) -> MappingAudit:
    """Audit exact canonical-code matches without resolving ambiguity."""

    ingredient_counts: dict[str, int] = {}
    missing_code_rows = 0
    for recipe in fcid.recipes:
        for ingredient in recipe.ingredients:
            if ingredient.fcid_code is None:
                missing_code_rows += 1
                continue
            ingredient_counts[ingredient.fcid_code] = (
                ingredient_counts.get(ingredient.fcid_code, 0) + 1
            )

    factors_by_code: dict[str, list[DatafieldFactorObservation]] = {}
    for factor in datafield.factors:
        if factor.factor_id is not None:
            factors_by_code.setdefault(factor.factor_id, []).append(factor)

    records: list[CommodityMappingRecord] = []
    for code in sorted(ingredient_counts):
        candidates = factors_by_code.get(code, [])
        if not candidates:
            status = MappingStatus.UNMAPPED
        elif len(candidates) > 1:
            status = MappingStatus.AMBIGUOUS
        elif candidates[0].factor_value_status is not NumericValueStatus.PRESENT:
            status = MappingStatus.INVALID_FACTOR_VALUE
        else:
            status = MappingStatus.DIRECT
        records.append(
            CommodityMappingRecord(
                fcid_code=code,
                status=status,
                ingredient_row_count=ingredient_counts[code],
                candidate_count=len(candidates),
                candidate_source_rows=tuple(
                    candidate.source_row for candidate in candidates
                ),
                candidate_descriptions=tuple(
                    candidate.description for candidate in candidates
                ),
            )
        )
    return MappingAudit(tuple(records), missing_code_rows)
