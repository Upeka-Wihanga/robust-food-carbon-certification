from __future__ import annotations

import numpy as np
import pytest

from food_carbon_cert.geometry import (
    InfeasibleRankIntervalError,
    deduplicate_vertices,
    is_ordered_simplex_point,
    one_rank_slab_vertices,
    ordered_simplex_vertices,
    rank_feasible_interval,
)


@pytest.mark.parametrize(
    ("ingredient_count", "rank", "lower", "upper"),
    [(3, 1, 0.4, 0.6), (3, 2, 0.2, 0.4), (5, 5, 0.05, 0.15)],
)
def test_every_slab_vertex_is_feasible(
    ingredient_count: int, rank: int, lower: float, upper: float
) -> None:
    vertices = one_rank_slab_vertices(ingredient_count, rank, lower, upper)

    assert all(is_ordered_simplex_point(vertex) for vertex in vertices)
    assert np.all(vertices[:, rank - 1] >= lower - 1e-12)
    assert np.all(vertices[:, rank - 1] <= upper + 1e-12)


def test_point_disclosure_geometry_contains_both_line_endpoints() -> None:
    vertices = one_rank_slab_vertices(3, 2, 1.0 / 3.0, 1.0 / 3.0)
    expected = np.asarray([[1.0 / 3.0] * 3, [2.0 / 3.0, 1.0 / 3.0, 0.0]])

    assert vertices.shape == (2, 3)
    for point in expected:
        assert any(np.allclose(point, vertex, atol=1e-12) for vertex in vertices)


@pytest.mark.parametrize("ingredient_count", [2, 3, 5])
def test_full_rank_feasible_interval_recovers_simplex_vertices(
    ingredient_count: int,
) -> None:
    for rank in range(1, ingredient_count + 1):
        lower, upper = rank_feasible_interval(ingredient_count, rank)
        slab = one_rank_slab_vertices(ingredient_count, rank, lower, upper)
        simplex = ordered_simplex_vertices(ingredient_count)
        assert slab.shape == simplex.shape
        for point in simplex:
            assert any(np.allclose(point, vertex, atol=1e-12) for vertex in slab)


def test_infeasible_interval_is_rejected_without_silent_clipping() -> None:
    with pytest.raises(InfeasibleRankIntervalError):
        one_rank_slab_vertices(3, 1, 0.2, 0.6)
    with pytest.raises(InfeasibleRankIntervalError):
        one_rank_slab_vertices(3, 2, 0.6, 0.7)


def test_explicit_clipping_is_supported() -> None:
    clipped = one_rank_slab_vertices(3, 1, 0.2, 0.6, clip=True)
    explicit = one_rank_slab_vertices(3, 1, 1.0 / 3.0, 0.6)
    np.testing.assert_allclose(clipped, explicit, rtol=0.0, atol=1e-12)


def test_duplicate_elimination_is_numerical() -> None:
    vertices = deduplicate_vertices(
        [np.asarray([1.0, 0.0]), np.asarray([1.0 + 1e-14, -1e-14])]
    )
    assert vertices.shape == (1, 2)


def test_rank_one_and_last_rank_boundaries() -> None:
    rank_one = one_rank_slab_vertices(4, 1, 0.25, 0.5)
    last_rank = one_rank_slab_vertices(4, 4, 0.0, 0.2)
    assert np.all(rank_one[:, 0] >= 0.25 - 1e-12)
    assert np.all(rank_one[:, 0] <= 0.5 + 1e-12)
    assert np.all(last_rank[:, 3] >= -1e-12)
    assert np.all(last_rank[:, 3] <= 0.2 + 1e-12)


def test_stage14_rank_two_slab_contains_interior_breakpoint() -> None:
    vertices = one_rank_slab_vertices(3, 2, 0.325, 0.335)
    critical = np.asarray([1.0 / 3.0] * 3)
    assert any(np.allclose(vertex, critical, atol=1e-12) for vertex in vertices)
