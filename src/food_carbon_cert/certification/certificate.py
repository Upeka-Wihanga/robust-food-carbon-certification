"""Structured robust-certification decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Decision(StrEnum):
    """Possible robust comparison decisions."""

    A_LOWER = "A_LOWER"
    B_LOWER = "B_LOWER"
    ABSTAIN = "ABSTAIN"


@dataclass(frozen=True, slots=True)
class CertificationResult:
    """Auditable result of one robust food comparison."""

    lower_bound: float
    upper_bound: float
    decision: Decision
    tolerance: float
    vertex_count_a: int
    vertex_count_b: int
    union_factor_count: int
    evaluated_vertex_pairs: int
    metadata: dict[str, Any] = field(default_factory=dict)
