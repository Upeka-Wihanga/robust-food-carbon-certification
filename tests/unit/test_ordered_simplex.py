from __future__ import annotations

import numpy as np
import pytest

from food_carbon_cert.geometry import (
    is_ordered_simplex_point,
    ordered_simplex_vertices,
    rank_feasible_interval,
)


@pytest.mark.parametrize("ingredient_count", range(1, 9))
def test_prefix_uniform_vertices_are_feasible(ingredient_count: int) -> None:
    vertices = ordered_simplex_vertices(ingredient_count)

    assert vertices.shape == (ingredient_count, ingredient_count)
    assert all(is_ordered_simplex_point(vertex) for vertex in vertices)
    for prefix_length, vertex in enumerate(vertices, start=1):
        expected = np.zeros(ingredient_count)
        expected[:prefix_length] = 1.0 / prefix_length
        np.testing.assert_allclose(vertex, expected, rtol=0.0, atol=1e-15)


def test_rank_feasible_ranges() -> None:
    assert rank_feasible_interval(4, 1) == (0.25, 1.0)
    assert rank_feasible_interval(4, 2) == (0.0, 0.5)
    assert rank_feasible_interval(4, 4) == (0.0, 0.25)


@pytest.mark.parametrize("ingredient_count", [0, -1])
def test_invalid_ingredient_count_rejected(ingredient_count: int) -> None:
    with pytest.raises(ValueError):
        ordered_simplex_vertices(ingredient_count)
