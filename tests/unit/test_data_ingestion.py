from __future__ import annotations

from pathlib import Path

import pytest

from food_carbon_cert.data import (
    HeaderRequirement,
    ProvenanceMismatchError,
    SourceFileMissingError,
    SourceManifestEntry,
    SourceSchemaError,
    load_datafield,
    load_fcid,
    load_guan,
    load_source_manifest,
    load_workbook_source,
    verify_source_file,
)

FIXTURES = Path(__file__).parents[1] / "fixtures" / "data"
FCID_FIXTURE = FIXTURES / "synthetic_fcid.csv"
PROJECT_ROOT = Path(__file__).parents[2]


def _expected_fcid(
    *,
    sha256: str = "6a16b67838c51717a0899a1cfd109d85234d0660333c55a21d9c1d9730105b10",
    byte_count: int = 240,
) -> SourceManifestEntry:
    return SourceManifestEntry(
        expected_filename=FCID_FIXTURE.name,
        source_category="synthetic_fcid",
        sha256=sha256,
        bytes=byte_count,
        local_expected_path=str(FCID_FIXTURE),
        commit_to_git=True,
        redistribution_status="SYNTHETIC",
    )


def test_valid_sha_and_size_verification() -> None:
    result = verify_source_file(FCID_FIXTURE, _expected_fcid())

    assert result.matches
    assert result.actual_sha256 == result.expected_sha256
    assert result.actual_bytes == result.expected_bytes == 240


def test_source_manifest_loads_typed_entries() -> None:
    manifest = load_source_manifest(
        PROJECT_ROOT / "data" / "manifests" / "source_files.json"
    )

    assert manifest.manifest_version == 1
    assert len(manifest.files) == 3
    assert (
        manifest.by_category("fcid_wweia_recipe_commodity_source").expected_filename
        == "Recipes_WWEIA_FCID_0510.csv"
    )


def test_incorrect_sha_is_a_blocking_failure() -> None:
    with pytest.raises(ProvenanceMismatchError, match="provenance mismatch"):
        verify_source_file(FCID_FIXTURE, _expected_fcid(sha256="0" * 64))


def test_missing_source_fails_clearly(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"

    with pytest.raises(SourceFileMissingError, match="source file not found"):
        verify_source_file(missing, _expected_fcid())
    with pytest.raises(SourceFileMissingError, match="source file not found"):
        load_fcid(missing)


def test_csv_loader_preserves_source_strings_and_detects_duplicates() -> None:
    source = load_fcid(FCID_FIXTURE, expected=_expected_fcid())

    assert source.encoding == "utf-8"
    assert len(source.rows) == 2
    assert source.rows[0][0] == "001"
    assert source.rows[0][2] == "01"
    assert source.rows[0][5] == "  source spacing  "
    assert source.rows[1][7] == ""
    duplicates = source.duplicate_counts("Food_Code")
    assert duplicates.extra_occurrences == 1
    assert duplicates.duplicate_groups == 1


def test_csv_loader_rejects_missing_expected_columns() -> None:
    with pytest.raises(SourceSchemaError, match="missing required columns"):
        load_fcid(FCID_FIXTURE, required_columns=("not_a_source_column",))


def test_datafield_loader_preserves_sheets_values_and_formulas() -> None:
    source = load_datafield(FIXTURES / "synthetic_datafield.xlsx")

    assert source.sheet_names == (
        "DESCRIPTION",
        "FCID linkages",
        "literature entries",
        "Pivot Table_GHG",
        "Pivot Table_CED",
        "PROXY def'ns",
        "MassConv",
    )
    linkage = source.sheet("FCID linkages")
    assert linkage.row(4)[0] == "001"
    assert linkage.row(4)[1] == "  source spacing  "
    assert linkage.row(4)[2] == "=1+1"


def test_guan_loader_preserves_recipe_and_factor_source_values() -> None:
    source = load_guan(FIXTURES / "synthetic_guan.xlsx")

    recipe = source.sheet("Recipe")
    factors = source.sheet("Greenhouse gas emission factors")
    assert recipe.row(2)[3] == "{'Ingredient A': 10.0}"
    assert recipe.row(2)[7] == "=SUM(E2:G2)"
    assert factors.row(2)[1] == " Ingredient A"


def test_workbook_loader_rejects_malformed_expected_columns() -> None:
    with pytest.raises(SourceSchemaError, match="missing required columns"):
        load_workbook_source(
            FIXTURES / "synthetic_datafield.xlsx",
            required_sheets=("FCID linkages",),
            required_headers={
                "FCID linkages": HeaderRequirement(
                    row=3,
                    columns=("not_a_source_column",),
                )
            },
        )
