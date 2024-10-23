"""Utility functions for testing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    import pyrr


def assert_vectors_equal(
    vector1: pyrr.Vector3 | pyrr.Quaternion | np.ndarray | pyrr.Matrix33 | pyrr.Matrix44,
    vector2: pyrr.Vector3 | pyrr.Quaternion | np.ndarray | pyrr.Matrix33 | pyrr.Matrix44,
) -> None:
    """Assert that two lists are equal."""
    np.testing.assert_allclose(
        np.array(vector1),
        np.array(vector2),
        atol=1e-7,
    )
