"""This module contains the Cylinder and Cylinders classes.

They are used to create cylinders and multiple cylinders of the same color, respectively.
"""

from __future__ import annotations

import numpy as np
import pyrr


class Cylinder:
    """Creates a Cylinder object, containing its vertices and indices.

    :param color: Color of the cylinder.
    :param subdivisions: Number of subdivisions of the cylinder.
    """

    def __init__(self, subdivisions: int) -> None:
        """Creates a Cylinder object, containing its vertices and indices."""
        self.subdivisions = subdivisions
        vertices, indices = generate_cylinder(self.subdivisions)
        self.vertices = vertices
        self.indices = indices


def generate_cylinder(
    subdivisions: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculates the vertices and indices of a cylinder for a given number of subdivisions.

    :param color: Color of the cylinder.
    :param subdivisions: Number of subdivisions of the cylinder.
    :returns:
        - **vertices** (numpy.array of numpy.float32) - Vertices in the following order x,y,z,nx,ny,nz,..., where\
         xyz are the cartesian coordinates, and nxnynz are the components of the normal\
          vector.
        - **indices** (numpy.array of numpy.uint32) - Gives the connectivity of the vertices.
    """
    vertices = []
    indices = []

    height = 1.0
    radius = 0.5
    vertices.extend([0.0, -height / 2, 0.0, 0.0, -1, 0.0])
    vertices.extend([0.0, height / 2, 0.0, 0.0, 1, 0.0])
    for i in range(subdivisions):
        # vertices
        theta = 2 * np.pi * i / subdivisions
        x = radius * np.cos(theta)
        y = -height / 2
        z = radius * np.sin(theta)
        normal = np.array([x, 0, z])
        normal /= np.linalg.norm(normal)
        vertices.extend([x, y, z, 0, -1, 0])
        vertices.extend(
            [x, y, z, normal[0], normal[1], normal[2]],
        )

        vertices.extend([x, y + height, z, 0, 1, 0])
        vertices.extend(
            [
                x,
                y + height,
                z,
                normal[0],
                normal[1],
                normal[2],
            ],
        )

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


def calculate_cylinder_model_matrix(
    position: np.ndarray,
    radius: float,
    length: float,
    direction: np.ndarray,
) -> np.ndarray:
    """Calculates the model matrix for a cylinder.

    :param position: Position of the center of the cylinder.
    :param radius: Radius of the cylinder.
    :param length: Length of the cylinder.
    :param direction: Direction of the cylinder, does not need to be normalized.
    """
    y_axis = np.array([0, 1, 0], dtype=np.float32)
    direction = direction / np.linalg.norm(direction)
    if abs(y_axis @ direction) != 1:
        rotation_axis = np.cross(y_axis, direction)
        # Calculate the angle to rotate the cylinder to the correct orientation.
        rotation_angle = np.arccos(
            np.clip(
                np.dot(direction, y_axis) / (np.linalg.norm(direction)),
                -1,
                1,
            ),
        )
    else:
        rotation_axis = np.array([0, 0, 1], dtype=np.float32)
        rotation_angle = 0
    translation_matrix = pyrr.matrix44.create_from_translation(
        pyrr.Vector3(position),
    )
    rotation_matrix = pyrr.matrix44.create_from_axis_rotation(
        rotation_axis,
        rotation_angle,
    )
    scale = pyrr.Vector3([radius] * 3)
    scale[1] = length / 2
    scale_matrix = pyrr.matrix44.create_from_scale(pyrr.Vector3(scale))
    rotation_scale_matrix = scale_matrix @ rotation_matrix
    return np.array(np.array([rotation_scale_matrix @ translation_matrix], dtype=np.float32))
