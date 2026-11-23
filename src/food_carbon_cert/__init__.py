"""Robust food-carbon certification reconstructed research baseline."""

from .certification import (
    CertificationResult,
    Decision,
    FoodUncertainty,
    certify_pair,
)
from .uncertainty import FactorInterval

__version__ = "0.1.0"

__all__ = [
    "CertificationResult",
    "Decision",
    "FactorInterval",
    "FoodUncertainty",
    "certify_pair",
]
