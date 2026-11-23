"""Lossless, read-only workbook loading primitives for raw sources."""

from __future__ import annotations

from collections import Counter
from collections.abc import Hashable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from .provenance import (
    FileVerification,
    SourceFileMissingError,
    SourceManifestEntry,
    verify_source_file,
)


class SourceSchemaError(ValueError):
    """Raised when a raw source lacks an explicitly required schema element."""


@dataclass(frozen=True, slots=True)
class DuplicateCounts:
    """Duplicate-key counts for inspection without filtering source rows."""

    extra_occurrences: int
    duplicate_groups: int


@dataclass(frozen=True, slots=True)
class HeaderRequirement:
    """Required source columns on a one-based worksheet row."""

    row: int
    columns: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WorksheetSource:
    """One worksheet with source values and formulas preserved."""

    title: str
    max_row: int
    max_column: int
    rows: tuple[tuple[object, ...], ...]

    def row(self, row_number: int) -> tuple[object, ...]:
        """Return a one-based worksheet row."""

        if not 1 <= row_number <= len(self.rows):
            raise IndexError(f"worksheet row out of range: {row_number}")
        return self.rows[row_number - 1]


@dataclass(frozen=True, slots=True)
class WorkbookSource:
    """A raw workbook loaded without cleaning, filtering, or recalculation."""

    path: Path
    sheets: tuple[WorksheetSource, ...]
    verification: FileVerification | None
    data_only: bool

    @property
    def sheet_names(self) -> tuple[str, ...]:
        """Return workbook sheet names in source order."""

        return tuple(sheet.title for sheet in self.sheets)

    def sheet(self, title: str) -> WorksheetSource:
        """Return a worksheet by its exact source title."""

        for sheet in self.sheets:
            if sheet.title == title:
                return sheet
        raise KeyError(f"worksheet not found: {title}")


def duplicate_key_counts(
    rows: Iterable[Sequence[object]], column_indexes: Sequence[int]
) -> DuplicateCounts:
    """Count repeated keys without changing or removing source rows."""

    indexes = tuple(column_indexes)
    if not indexes:
        raise ValueError("at least one duplicate-key column is required")
    counts: Counter[tuple[Hashable, ...]] = Counter()
    for row in rows:
        try:
            key_values = tuple(row[index] for index in indexes)
        except IndexError as error:
            raise ValueError("duplicate-key column index is outside a row") from error
        if not all(isinstance(value, Hashable) for value in key_values):
            raise TypeError("duplicate-key values must be hashable")
        key = tuple(value for value in key_values if isinstance(value, Hashable))
        counts[key] += 1
    return DuplicateCounts(
        extra_occurrences=sum(count - 1 for count in counts.values() if count > 1),
        duplicate_groups=sum(count > 1 for count in counts.values()),
    )


def _validate_schema(
    source: WorkbookSource,
    required_sheets: Sequence[str],
    required_headers: dict[str, HeaderRequirement],
) -> None:
    missing_sheets = [
        sheet_name
        for sheet_name in required_sheets
        if sheet_name not in source.sheet_names
    ]
    if missing_sheets:
        names = ", ".join(missing_sheets)
        raise SourceSchemaError(f"workbook is missing required sheets: {names}")

    for sheet_name, requirement in required_headers.items():
        sheet = source.sheet(sheet_name)
        header = sheet.row(requirement.row)
        missing_columns = [
            column for column in requirement.columns if column not in header
        ]
        if missing_columns:
            names = ", ".join(missing_columns)
            raise SourceSchemaError(
                f"sheet {sheet_name!r} row {requirement.row} is missing "
                f"required columns: {names}"
            )


def load_workbook_source(
    path: str | Path,
    *,
    expected: SourceManifestEntry | None = None,
    data_only: bool = False,
    required_sheets: Sequence[str] = (),
    required_headers: dict[str, HeaderRequirement] | None = None,
) -> WorkbookSource:
    """Load every sheet as formulas or stored values without recalculation."""

    source_path = Path(path)
    if not source_path.is_file():
        raise SourceFileMissingError(f"source file not found: {source_path}")
    verification = (
        verify_source_file(source_path, expected) if expected is not None else None
    )
    try:
        workbook = load_workbook(
            source_path,
            read_only=True,
            data_only=data_only,
            keep_links=True,
        )
    except (BadZipFile, InvalidFileException, OSError) as error:
        raise ValueError(f"cannot load workbook source: {source_path}") from error

    try:
        sheets = tuple(
            WorksheetSource(
                title=worksheet.title,
                max_row=worksheet.max_row,
                max_column=worksheet.max_column,
                rows=tuple(tuple(row) for row in worksheet.iter_rows(values_only=True)),
            )
            for worksheet in workbook.worksheets
        )
    finally:
        workbook.close()

    source = WorkbookSource(source_path, sheets, verification, data_only)
    _validate_schema(
        source,
        required_sheets,
        {} if required_headers is None else required_headers,
    )
    return source
