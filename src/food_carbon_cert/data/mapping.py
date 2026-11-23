"""Deterministic mapping audit between FCID ingredients and dataFIELD factors."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .babyfood_mapping import (
    CONFIRMED_BABYFOOD_PARENT_MAP,
    WEIGHT_BASIS_WARNING_CODES,
)
from .datafield_normalized import (
    DatafieldFactorObservation,
    NormalizedDatafieldFactors,
    NumericValueStatus,
)
from .fcid_normalized import NormalizedFcid


class MappingPolicy(StrEnum):
    """Explicitly selected FCID-to-dataFIELD mapping policy."""

    EXACT_ONLY = "EXACT_ONLY"
    EXACT_PLUS_CONFIRMED_BABYFOOD_PARENT = "EXACT_PLUS_CONFIRMED_BABYFOOD_PARENT"


class MappingStatus(StrEnum):
    """Resolution and provenance status for one unique FCID commodity code."""

    EXACT_DATAFIELD = "EXACT_DATAFIELD"
    CONFIRMED_BABYFOOD_PARENT_PROXY = "CONFIRMED_BABYFOOD_PARENT_PROXY"
    UNMAPPED = "UNMAPPED"
    AMBIGUOUS = "AMBIGUOUS"
    INVALID_FACTOR_VALUE = "INVALID_FACTOR_VALUE"
    DIRECT = "EXACT_DATAFIELD"


@dataclass(frozen=True, slots=True)
class CommodityMappingRecord:
    """Mapping evidence for one unique nonmissing FCID commodity code."""

    fcid_code: str
    mapped_fcid_code: str | None
    mapping_policy: MappingPolicy
    status: MappingStatus
    mapping_reason: str
    weight_basis_warning: bool
    ingredient_row_count: int
    candidate_count: int
    candidate_source_rows: tuple[int, ...]
    candidate_descriptions: tuple[str | None, ...]

    @property
    def is_mapped(self) -> bool:
        """Whether this record resolves to one usable factor."""

        return self.status in {
            MappingStatus.EXACT_DATAFIELD,
            MappingStatus.CONFIRMED_BABYFOOD_PARENT_PROXY,
        }


@dataclass(frozen=True, slots=True)
class MappingAudit:
    """Machine-readable mapping status table and source-level diagnostics."""

    policy: MappingPolicy
    records: tuple[CommodityMappingRecord, ...]
    missing_fcid_code_rows: int
    complete_recipe_count: int
    incomplete_recipe_count: int

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

    @property
    def mapped_unique_code_count(self) -> int:
        """Count unique source codes resolved to usable factors."""

        return sum(record.is_mapped for record in self.records)

    @property
    def unmapped_unique_code_count(self) -> int:
        """Count unique source codes without a usable factor."""

        return sum(not record.is_mapped for record in self.records)

    @property
    def mapped_ingredient_row_count(self) -> int:
        """Count ingredient rows whose nonmissing source code resolves."""

        return sum(
            record.ingredient_row_count for record in self.records if record.is_mapped
        )

    @property
    def unmapped_ingredient_row_count(self) -> int:
        """Count unresolved ingredient rows, including missing source codes."""

        return self.missing_fcid_code_rows + sum(
            record.ingredient_row_count
            for record in self.records
            if not record.is_mapped
        )

    @property
    def weight_basis_warning_count(self) -> int:
        """Count mapped source codes with a documented weight-basis caution."""

        return sum(
            record.is_mapped and record.weight_basis_warning for record in self.records
        )


def _mapping_status(
    candidates: list[DatafieldFactorObservation],
    *,
    resolved_status: MappingStatus,
) -> MappingStatus:
    if not candidates:
        return MappingStatus.UNMAPPED
    if len(candidates) > 1:
        return MappingStatus.AMBIGUOUS
    if candidates[0].factor_value_status is not NumericValueStatus.PRESENT:
        return MappingStatus.INVALID_FACTOR_VALUE
    return resolved_status


def audit_fcid_datafield_mapping(
    fcid: NormalizedFcid,
    datafield: NormalizedDatafieldFactors,
    *,
    policy: MappingPolicy = MappingPolicy.EXACT_ONLY,
) -> MappingAudit:
    """Audit one explicit mapping policy without changing source identifiers.

    Exact matches always take precedence. The enhanced policy consults only the
    externally verified, literal baby-food/base-parent crosswalk; it never
    rewrites an arbitrary terminal digit.
    """

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
        mapped_code: str | None = None
        weight_basis_warning = False
        exact_candidates = factors_by_code.get(code, [])
        if exact_candidates:
            candidates = exact_candidates
            status = _mapping_status(
                candidates,
                resolved_status=MappingStatus.EXACT_DATAFIELD,
            )
            mapped_code = code if len(candidates) == 1 else None
            reason = "Original FCID code matched dataFIELD directly."
        elif (
            policy is MappingPolicy.EXACT_PLUS_CONFIRMED_BABYFOOD_PARENT
            and code in CONFIRMED_BABYFOOD_PARENT_MAP
        ):
            parent_code = CONFIRMED_BABYFOOD_PARENT_MAP[code]
            candidates = factors_by_code.get(parent_code, [])
            status = _mapping_status(
                candidates,
                resolved_status=MappingStatus.CONFIRMED_BABYFOOD_PARENT_PROXY,
            )
            mapped_code = parent_code if len(candidates) == 1 else None
            weight_basis_warning = code in WEIGHT_BASIS_WARNING_CODES
            reason = (
                "New reconstructed policy: official WWEIA-FCID metadata "
                "confirms this baby-food variant and its base parent."
            )
        else:
            candidates = []
            status = MappingStatus.UNMAPPED
            reason = "No usable mapping exists under the selected policy."
        records.append(
            CommodityMappingRecord(
                fcid_code=code,
                mapped_fcid_code=mapped_code,
                mapping_policy=policy,
                status=status,
                mapping_reason=reason,
                weight_basis_warning=weight_basis_warning,
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
    by_code = {record.fcid_code: record for record in records}
    complete_recipe_count = sum(
        all(
            ingredient.fcid_code is not None and by_code[ingredient.fcid_code].is_mapped
            for ingredient in recipe.ingredients
        )
        for recipe in fcid.recipes
    )
    return MappingAudit(
        policy=policy,
        records=tuple(records),
        missing_fcid_code_rows=missing_code_rows,
        complete_recipe_count=complete_recipe_count,
        incomplete_recipe_count=len(fcid.recipes) - complete_recipe_count,
    )
