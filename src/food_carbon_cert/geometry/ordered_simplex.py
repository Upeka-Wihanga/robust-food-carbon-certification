"""Geometry of ordered ingredient compositions.

The ordered simplex contains nonnegative ingredient shares in nonincreasing
order whose sum is one. Its vertices are the prefix-uniform compositions.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def _validate_ingredient_count(ingredient_count: int) -> None:
    if isinstance(ingredient_count, bool) or not isinstance(ingredient_count, int):
        raise TypeError("ingredient_count must be an integer")
    if ingredient_count < 1:
        raise ValueError("ingredient_count must be positive")


def _validate_rank(ingredient_count: int, rank: int) -> None:
    _validate_ingredient_count(ingredient_count)
    if isinstance(rank, bool) or not isinstance(rank, int):
        raise TypeError("rank must be an integer")
    if not 1 <= rank <= ingredient_count:
        raise ValueError(
            f"rank must be between 1 and {ingredient_count}, received {rank}"
        )


def ordered_simplex_vertices(ingredient_count: int) -> NDArray[np.float64]:
    """Return all prefix-uniform vertices of an ordered simplex.

    Args:
        ingredient_count: Number of ingredient positions.

    Returns:
        An ``(ingredient_count, ingredient_count)`` array. Row ``k - 1`` has
        value ``1 / k`` in its first ``k`` positions and zero elsewhere.
    """

    _validate_ingredient_count(ingredient_count)
    vertices = np.zeros((ingredient_count, ingredient_count), dtype=np.float64)
    for prefix_length in range(1, ingredient_count + 1):
        vertices[prefix_length - 1, :prefix_length] = 1.0 / prefix_length
    return vertices


def rank_feasible_interval(ingredient_count: int, rank: int) -> tuple[float, float]:
    """Return the complete feasible interval for a one-based ingredient rank."""

    _validate_rank(ingredient_count, rank)
    lower = 1.0 / ingredient_count if rank == 1 else 0.0
    upper = 1.0 / rank
    return lower, upper
