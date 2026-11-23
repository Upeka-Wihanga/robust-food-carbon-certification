"""Raw-source manifest loading and byte-for-byte provenance verification."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class SourceFileMissingError(FileNotFoundError):
    """Raised when an explicitly requested raw source does not exist."""


class ProvenanceMismatchError(ValueError):
    """Raised when a raw source does not match its expected hash and size."""


@dataclass(frozen=True, slots=True)
class SourceManifestEntry:
    """Expected identity and handling policy for one raw source file."""

    expected_filename: str
    source_category: str
    sha256: str
    bytes: int
    local_expected_path: str
    commit_to_git: bool
    redistribution_status: str


@dataclass(frozen=True, slots=True)
class SourceManifest:
    """Typed contents of the raw-source manifest."""

    manifest_version: int
    files: tuple[SourceManifestEntry, ...]

    def by_category(self, source_category: str) -> SourceManifestEntry:
        """Return the unique entry for a source category."""

        matches = [
            entry for entry in self.files if entry.source_category == source_category
        ]
        if len(matches) != 1:
            raise KeyError(
                f"expected one manifest entry for {source_category!r}, "
                f"found {len(matches)}"
            )
        return matches[0]


@dataclass(frozen=True, slots=True)
class FileVerification:
    """Expected and observed identity of one local source file."""

    path: Path
    expected_sha256: str
    actual_sha256: str
    expected_bytes: int
    actual_bytes: int

    @property
    def matches(self) -> bool:
        """Return whether both hash and byte length match."""

        return (
            self.expected_sha256 == self.actual_sha256
            and self.expected_bytes == self.actual_bytes
        )


def _required_value(mapping: dict[str, Any], key: str, kind: type[Any]) -> Any:
    try:
        value = mapping[key]
    except KeyError as error:
        raise ValueError(f"manifest entry is missing {key!r}") from error
    if not isinstance(value, kind):
        raise ValueError(f"manifest field {key!r} must be {kind.__name__}")
    return value


def load_source_manifest(path: str | Path) -> SourceManifest:
    """Load and validate the machine-readable raw-source manifest."""

    manifest_path = Path(path)
    if not manifest_path.is_file():
        raise SourceFileMissingError(f"source manifest not found: {manifest_path}")
    loaded: object = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("source manifest root must be an object")

    version = loaded.get("manifest_version")
    file_entries = loaded.get("files")
    if isinstance(version, bool) or not isinstance(version, int):
        raise ValueError("manifest_version must be an integer")
    if not isinstance(file_entries, list):
        raise ValueError("manifest files must be an array")

    entries: list[SourceManifestEntry] = []
    for raw_entry in file_entries:
        if not isinstance(raw_entry, dict):
            raise ValueError("every manifest file entry must be an object")
        entry: dict[str, Any] = raw_entry
        byte_count = _required_value(entry, "bytes", int)
        commit_to_git = _required_value(entry, "commit_to_git", bool)
        if isinstance(byte_count, bool) or byte_count < 0:
            raise ValueError("manifest bytes must be a nonnegative integer")
        digest = _required_value(entry, "sha256", str)
        if len(digest) != 64 or any(
            character not in "0123456789abcdef" for character in digest
        ):
            raise ValueError("manifest sha256 must be 64 lowercase hexadecimal digits")
        entries.append(
            SourceManifestEntry(
                expected_filename=_required_value(entry, "expected_filename", str),
                source_category=_required_value(entry, "source_category", str),
                sha256=digest,
                bytes=byte_count,
                local_expected_path=_required_value(entry, "local_expected_path", str),
                commit_to_git=commit_to_git,
                redistribution_status=_required_value(
                    entry, "redistribution_status", str
                ),
            )
        )
    return SourceManifest(version, tuple(entries))


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Calculate a file's SHA-256 digest without loading it all into memory."""

    source_path = Path(path)
    if not source_path.is_file():
        raise SourceFileMissingError(f"source file not found: {source_path}")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    digest = hashlib.sha256()
    with source_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_source_file(
    path: str | Path,
    expected: SourceManifestEntry,
    *,
    raise_on_mismatch: bool = True,
) -> FileVerification:
    """Verify a source against its manifest hash and byte length."""

    source_path = Path(path)
    if not source_path.is_file():
        raise SourceFileMissingError(f"source file not found: {source_path}")
    result = FileVerification(
        path=source_path,
        expected_sha256=expected.sha256,
        actual_sha256=sha256_file(source_path),
        expected_bytes=expected.bytes,
        actual_bytes=source_path.stat().st_size,
    )
    if raise_on_mismatch and not result.matches:
        raise ProvenanceMismatchError(
            f"provenance mismatch for {source_path}: "
            f"sha256 expected {result.expected_sha256}, "
            f"actual {result.actual_sha256}; bytes expected "
            f"{result.expected_bytes}, actual {result.actual_bytes}"
        )
    return result
