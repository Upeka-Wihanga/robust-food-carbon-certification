"""Ordered-composition geometry."""

from .interval_polytope import InfeasibleRankIntervalError, one_rank_slab_vertices
from .ordered_simplex import ordered_simplex_vertices, rank_feasible_interval
from .vertices import deduplicate_vertices, is_ordered_simplex_point

__all__ = [
    "InfeasibleRankIntervalError",
    "deduplicate_vertices",
    "is_ordered_simplex_point",
    "one_rank_slab_vertices",
    "ordered_simplex_vertices",
    "rank_feasible_interval",
]
