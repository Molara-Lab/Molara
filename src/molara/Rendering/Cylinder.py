from __future__ import annotations

from typing import Optional

import numpy as np


class Cylinder:
    """Creates a Cylinder object, containing its vertices and indices.

    :param color: Color of the cylinder.
    :param subdivisions: Number of subdivisions of the cylinder.
    """

    def __init__(self, color: np.ndarray = None, subdivisions: int = -1) -> None:
        self.color = color
        self.subdivisions = subdivisions
        if subdivisions != -1 and color is not None:
            vertices, indices = generate_cylinder(self.color, self.subdivisions)
            self.vertices = vertices
            self.indices = indices
        else:
            self.vertices = None
            self.indices = None


class Cylinders(Cylinder):
    """Creates a Cylinders object containing multiple cylinders of the same color and the model matrices to draw multiple
    instances.

    :param color: Color of the cylinder.
    :param subdivisions: Number of subdivisions of the cylinder.
    """

    def __init__(self, color: np.ndarray = None, subdivisions: int = -1) -> None:
        super().__init__(color, subdivisions)
        self.model_matrices = None


def generate_cylinder(color: np.ndarray, subdivisions: int) -> (np.ndarray, np.ndarray):
    """Calculates the vertices and indices of a cylinder for a given color and number of subdivisions.

    :param color: Color of the cylinder.
    :param subdivisions: Number of subdivisions of the cylinder.
    :returns:
        - **vertices** (numpy.array of numpy.float32) - Vertices in the following order x,y,z,r,g,b,nx,ny,nz,..., where\
         xyz are the cartesian coordinates,rgb are the color values [0,1], and nxnynz are the components of the normal\
          vector.
        - **indices** (numpy.array of numpy.uint32) - Gives the connectivity of the vertices.
    """
    vertices = []
    indices = []

    height = 1.0
    radius = 0.5
    vertices.extend([0.0, -height / 2, 0.0, color[0], color[1], color[2], 0.0, -1, 0.0])
    vertices.extend([0.0, height / 2, 0.0, color[0], color[1], color[2], 0.0, 1, 0.0])
    for i in range(subdivisions):
        # vertices
        theta = 2 * np.pi * i / subdivisions
        x = radius * np.cos(theta)
        y = -height / 2
        z = radius * np.sin(theta)
        normal = [x, 0, z]
        normal /= np.linalg.norm(normal)
        vertices.extend([x, y, z, color[0], color[1], color[2], 0, -1, 0])
        vertices.extend([x, y, z, color[0], color[1], color[2], normal[0], normal[1], normal[2]])

        vertices.extend([x, y + height, z, color[0], color[1], color[2], 0, 1, 0])
        vertices.extend([x, y + height, z, color[0], color[1], color[2], normal[0], normal[1], normal[2]])

        # indices
        if i == subdivisions - 1:
            # top
            indices.extend([0, 2 + 4 * i, 2])
            # bottom
            indices.extend([1, 4 + 4 * i, 4])
            # side
            indices.extend([3 + 4 * i, 3, 5])
            indices.extend([5 + 4 * i, 3 + 4 * i, 5])

        else:
            # top
            indices.extend([0, 2 + 4 * i, 6 + 4 * i])
            # bottom
            indices.extend([1, 4 + 4 * i, 8 + 4 * i])
            # side
            indices.extend([3 + 4 * i, 7 + 4 * i, 5 + 4 * i])
            indices.extend([5 + 4 * i, 7 + 4 * i, 9 + 4 * i])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)