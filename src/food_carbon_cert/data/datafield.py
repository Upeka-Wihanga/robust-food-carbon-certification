"""Validated raw loader for the dataFIELD workbook."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from .provenance import SourceManifestEntry
from .workbook import HeaderRequirement, WorkbookSource, load_workbook_source

DATAFIELD_REQUIRED_SHEETS: Final[tuple[str, ...]] = (
    "DESCRIPTION",
    "FCID linkages",
    "literature entries",
    "Pivot Table_GHG",
    "Pivot Table_CED",
    "PROXY def'ns",
    "MassConv",
)

DATAFIELD_REQUIRED_HEADERS: Final[dict[str, HeaderRequirement]] = {
    "FCID linkages": HeaderRequirement(
        row=3,
        columns=(
            "FCID_Code",
            "FCID_Desc",
            "MJ / kg",
            "CO2 eq / kg",
            "Std. Dev",
            "scaled SD (group SD*food mean/group mean)",
        ),
    ),
    "literature entries": HeaderRequirement(
        row=1,
        columns=(
            "Indexing number",
            "FOOD TYPE",
            "SUB TYPE",
            "ACTIVE     GHGE, FARM GATE (kg CO2e/kg)",
            "reported variance",
        ),
    ),
    "MassConv": HeaderRequirement(
        row=1,
        columns=("FCID_Code", "FCID_Desc", "Commodity_base"),
    ),
}


def load_datafield(
    path: str | Path,
    *,
    expected: SourceManifestEntry | None = None,
) -> WorkbookSource:
    """Load dataFIELD without evaluating formulas, mapping, or filtering rows."""

    return load_workbook_source(
        path,
        expected=expected,
        required_sheets=DATAFIELD_REQUIRED_SHEETS,
        required_headers=DATAFIELD_REQUIRED_HEADERS,
    )
