"""Verified raw-source ingestion without research-specific selection."""

from .datafield import load_datafield
from .datafield_normalized import (
    DatafieldFactorObservation,
    NormalizedDatafieldFactors,
    NumericValueStatus,
    canonical_fcid_code,
    normalize_datafield_factors,
)
from .fcid import FCID_REQUIRED_COLUMNS, FcidSource, detect_csv_encoding, load_fcid
from .fcid_normalized import (
    EXPECTED_FCID_RECIPE_TOTAL,
    CompositionStatus,
    LinkageStatus,
    NormalizedFcid,
    NormalizedFcidIngredient,
    NormalizedFcidRecipe,
    RecipeNormalizationStatus,
    normalize_fcid,
)
from .guan import load_guan
from .mapping import (
    CommodityMappingRecord,
    MappingAudit,
    MappingStatus,
    audit_fcid_datafield_mapping,
)
from .provenance import (
    FileVerification,
    ProvenanceMismatchError,
    SourceFileMissingError,
    SourceManifest,
    SourceManifestEntry,
    load_source_manifest,
    sha256_file,
    verify_source_file,
)
from .workbook import (
    DuplicateCounts,
    HeaderRequirement,
    SourceSchemaError,
    WorkbookSource,
    WorksheetSource,
    duplicate_key_counts,
    load_workbook_source,
)

__all__ = [
    "FCID_REQUIRED_COLUMNS",
    "EXPECTED_FCID_RECIPE_TOTAL",
    "CommodityMappingRecord",
    "CompositionStatus",
    "DatafieldFactorObservation",
    "DuplicateCounts",
    "FcidSource",
    "FileVerification",
    "HeaderRequirement",
    "LinkageStatus",
    "MappingAudit",
    "MappingStatus",
    "NormalizedDatafieldFactors",
    "NormalizedFcid",
    "NormalizedFcidIngredient",
    "NormalizedFcidRecipe",
    "NumericValueStatus",
    "ProvenanceMismatchError",
    "RecipeNormalizationStatus",
    "SourceFileMissingError",
    "SourceManifest",
    "SourceManifestEntry",
    "SourceSchemaError",
    "WorkbookSource",
    "WorksheetSource",
    "audit_fcid_datafield_mapping",
    "canonical_fcid_code",
    "detect_csv_encoding",
    "duplicate_key_counts",
    "load_datafield",
    "load_fcid",
    "load_guan",
    "load_source_manifest",
    "load_workbook_source",
    "normalize_datafield_factors",
    "normalize_fcid",
    "sha256_file",
    "verify_source_file",
]
