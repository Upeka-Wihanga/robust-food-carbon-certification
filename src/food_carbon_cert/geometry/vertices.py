"""Numerical helpers for composition-polytope vertices."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from numpy.typing import ArrayLike, NDArray


def is_ordered_simplex_point(point: ArrayLike, *, atol: float = 1e-12) -> bool:
    """Return whether a vector satisfies the ordered-simplex constraints."""

    values = np.asarray(point, dtype=np.float64)
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
        return False
    if np.any(values < -atol):
        return False
    if np.any(values[:-1] + atol < values[1:]):
        return False
    return bool(np.isclose(values.sum(), 1.0, rtol=0.0, atol=atol))


def deduplicate_vertices(
    candidates: Iterable[ArrayLike], *, atol: float = 1e-12
) -> NDArray[np.float64]:
    """Remove numerically duplicate vertices and return deterministic order."""

    if atol < 0.0:
        raise ValueError("atol must be nonnegative")

    unique: list[NDArray[np.float64]] = []
    dimension: int | None = None
    for candidate in candidates:
        point = np.asarray(candidate, dtype=np.float64)
        if point.ndim != 1:
            raise ValueError("every candidate vertex must be one-dimensional")
        if dimension is None:
            dimension = point.size
        elif point.size != dimension:
            raise ValueError("candidate vertices must have the same dimension")
        if not any(np.allclose(point, other, rtol=0.0, atol=atol) for other in unique):
            unique.append(point.copy())

    if not unique:
        width = 0 if dimension is None else dimension
        return np.empty((0, width), dtype=np.float64)

    unique.sort(key=lambda point: tuple(float(value) for value in point))
    return np.vstack(unique)
