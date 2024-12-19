"""This module contains the polygons classe.

It is used to draw a polygon.
"""

import numpy as np
from molara.rendering.object3d import Object3D



class Polygon(Object3D):
    """Creates a Polygon object, containing its vertices and colors."""

    def __init__(self,
                 vertices: np.ndarray,
                 color: np.ndarray,
                 wire_frame: bool = False) -> None:
        """Create a Cylinder object to be drawn."""
        self.wire_frame = wire_frame
        super().__init__()
        self.vertices = vertices
        self.indices = None
        self.number_of_instances = 1
        # // 6 because each vertex has 3 coordinates and 3 normals!
        self.number_of_vertices = len(vertices) // 6
        self.model_matrices = np.array([np.identity(4, dtype=np.float32)])

        self.colors = color[0]
        self.generate_buffers()


    def calculate_scaling_matrices(self, dimensions: np.ndarray) -> None:
        """Dummy function."""
        return

    def calculate_translation_matrices(self, positions: np.ndarray) -> None:
        """Dummy function."""
        return

    def calculate_rotation_matrices(self, directions: np.ndarray) -> None:
        """Dummy function."""
        return

    def calculate_model_matrices(self) -> None:
        """Dummy function."""
        return
