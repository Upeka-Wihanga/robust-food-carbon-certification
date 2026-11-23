"""Validated raw loader for the Guan Chinese-cuisines workbook."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from .provenance import SourceManifestEntry
from .workbook import HeaderRequirement, WorkbookSource, load_workbook_source

GUAN_REQUIRED_SHEETS: Final[tuple[str, ...]] = (
    "Recipe",
    "Greenhouse gas emission factors",
    "Data_Source",
)

GUAN_REQUIRED_HEADERS: Final[dict[str, HeaderRequirement]] = {
    "Recipe": HeaderRequirement(
        row=1,
        columns=(
            "Recipe English name",
            "Recipe Chinese name",
            "Cuisine",
            "Ingredient (g)",
            "CF(gCO2e)_production",
            "CF(gCO2e)_post-farmgate",
            "CF(gCO2e)_cooking",
            "CF(gCO2e)_total",
        ),
    ),
    "Greenhouse gas emission factors": HeaderRequirement(
        row=1,
        columns=(
            "Food Categroy",
            "Ingredient ",
            "Greenhouse gas emission factors (kgCO2e/kg)_production",
            "Greenhouse gas emission factors "
            "(kgCO2e/kg)_postharvest handling, storage, and processing",
            "Greenhouse gas emission factors " "(kgCO2e/kg)_distribution and retailing",
        ),
    ),
    "Data_Source": HeaderRequirement(
        row=1,
        columns=("Data type", "Source"),
    ),
}


def load_guan(
    path: str | Path,
    *,
    expected: SourceManifestEntry | None = None,
) -> WorkbookSource:
    """Load Guan source sheets without parsing ingredients or selecting recipes."""

    return load_workbook_source(
        path,
        expected=expected,
        required_sheets=GUAN_REQUIRED_SHEETS,
        required_headers=GUAN_REQUIRED_HEADERS,
    )
