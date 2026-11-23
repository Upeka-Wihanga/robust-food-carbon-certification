"""Lossless loader for the raw FCID/WWEIA recipe-commodity CSV."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .provenance import (
    FileVerification,
    SourceFileMissingError,
    SourceManifestEntry,
    verify_source_file,
)
from .workbook import DuplicateCounts, SourceSchemaError, duplicate_key_counts

FCID_REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "Food_Code",
    "Mod_Code",
    "Ingredient_Num",
    "FCID_Code",
    "Cooked_Status",
    "Food_Form",
    "Cooking_Method",
    "Commodity_Weight",
    "CSFII_9498_IND",
    "WWEIA_9904_IND",
    "WWEIA_0510_IND",
)


@dataclass(frozen=True, slots=True)
class FcidSource:
    """Raw FCID CSV values preserved as source strings."""

    path: Path
    encoding: str
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    verification: FileVerification | None

    def duplicate_counts(self, *columns: str) -> DuplicateCounts:
        """Count duplicate keys for named columns without filtering rows."""

        if not columns:
            raise ValueError("at least one duplicate-key column is required")
        try:
            indexes = tuple(self.columns.index(column) for column in columns)
        except ValueError as error:
            raise KeyError(f"unknown FCID column: {error}") from error
        return duplicate_key_counts(self.rows, indexes)


def detect_csv_encoding(path: str | Path) -> str:
    """Detect the supported source encoding without replacement decoding."""

    source_path = Path(path)
    if not source_path.is_file():
        raise SourceFileMissingError(f"source file not found: {source_path}")
    content = source_path.read_bytes()
    if content.startswith(b"\xef\xbb\xbf"):
        content.decode("utf-8-sig")
        return "utf-8-sig"
    try:
        content.decode("utf-8")
    except UnicodeDecodeError:
        content.decode("cp1252")
        return "cp1252"
    return "utf-8"


def load_fcid(
    path: str | Path,
    *,
    expected: SourceManifestEntry | None = None,
    required_columns: tuple[str, ...] = FCID_REQUIRED_COLUMNS,
    encoding: str | None = None,
) -> FcidSource:
    """Load an FCID source without cleaning, filtering, or type coercion."""

    source_path = Path(path)
    if not source_path.is_file():
        raise SourceFileMissingError(f"source file not found: {source_path}")
    verification = (
        verify_source_file(source_path, expected) if expected is not None else None
    )
    selected_encoding = (
        detect_csv_encoding(source_path) if encoding is None else encoding
    )

    with source_path.open(encoding=selected_encoding, newline="") as stream:
        reader = csv.reader(stream)
        try:
            columns = tuple(next(reader))
        except StopIteration as error:
            raise SourceSchemaError("FCID source is empty") from error
        missing_columns = [
            column for column in required_columns if column not in columns
        ]
        if missing_columns:
            names = ", ".join(missing_columns)
            raise SourceSchemaError(f"FCID source is missing required columns: {names}")

        rows: list[tuple[str, ...]] = []
        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(columns):
                raise SourceSchemaError(
                    f"FCID row {line_number} has {len(row)} fields; "
                    f"expected {len(columns)}"
                )
            rows.append(tuple(row))

    return FcidSource(
        path=source_path,
        encoding=selected_encoding,
        columns=columns,
        rows=tuple(rows),
        verification=verification,
    )
