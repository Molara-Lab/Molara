"""Contains the polygons class.

It is used to draw a polygon.
"""

import numpy as np
from numpy.typing import NDArray

from molara.rendering.object3d import Object3D


class Polygon(Object3D):
    """Creates a Polygon object, containing its vertices and colors."""

    def __init__(self, vertices: NDArray, color: NDArray, wire_frame: bool = False) -> None:
        """Create a Polygon object to be drawn."""
        self.wire_frame = wire_frame
        super().__init__()
        self.vertices = vertices
        self.indices = None
        self.number_of_instances = 1
        # // 6 because each vertex has 3 coordinates and 3 normals!
        self.number_of_vertices = len(vertices) // 6
        self.model_matrices = np.array([np.identity(4, dtype=np.float32)])

        self.colors = color[0]

    def calculate_scaling_matrices(self, dimensions: NDArray) -> None:  # noqa: ARG002
        """Contain dummy function."""
        return

    def calculate_translation_matrices(self, positions: NDArray) -> None:  # noqa: ARG002
        """Contain dummy function."""
        return

    def calculate_rotation_matrices(self, directions: NDArray) -> None:  # noqa: ARG002
        """Contain dummy function."""
        return

    def calculate_model_matrices(self) -> None:
        """Contain dummy function."""
        return
