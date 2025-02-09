"""Contains the Cones class."""

import numpy as np

from molara.rendering.object3d import Object3D


class Cones(Object3D):
    """Creates a Cones object, containing its vertices, indices, and transformation matrices."""

    def __init__(
        self,
        subdivisions: int,
        positions: np.ndarray,
        directions: np.ndarray,
        dimensions: np.ndarray,
        colors: np.ndarray,
    ) -> None:
        """Create cones object to be drawn."""
        self.subdivisions = subdivisions
        vertices, indices = generate_cone(self.subdivisions)
        super().__init__()
        self.vertices = vertices
        self.indices = indices
        self.number_of_instances = len(positions)
        self.number_of_vertices = len(vertices)
        self.number_of_indices = len(indices)

        self.calculate_translation_matrices(positions)
        self.calculate_scaling_matrices(dimensions)
        self.calculate_rotation_matrices(directions)
        self.calculate_model_matrices()

        self.colors = colors


def generate_cone(
    subdivisions: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate the vertices and indices of a cone for a given number of subdivisions.

    :param subdivisions: Number of subdivisions of the cone.
    :returns:
        - **vertices** (numpy.array of numpy.float32) - Vertices in the following order x,y,z,nx,ny,nz,..., where\
         xyz are the cartesian coordinates, and nxnynz are the components of the normal\
          vector.
        - **indices** (numpy.array of numpy.uint32) - Gives the connectivity of the vertices.
    """
    vertices = []
    indices = []

    height = 1.0
    radius = 1.0

    vertices.append([0, -height / 2, 0, 0, -1, 0])

    # Generate the vertices
    for i in range(subdivisions):
        theta = 2 * np.pi * i / subdivisions
        x = radius * np.cos(theta)
        z = radius * np.sin(theta)
        # bottom circle
        vertices.append([x, -height / 2, z, 0, -1, 0])
        indices.append(0)
        indices.append(i + 1)
        if i == subdivisions - 1:
            indices.append(1)
        else:
            indices.append(i + 2)
        # cone
    for i in range(subdivisions):
        theta1 = 2 * np.pi * i / subdivisions
        x1 = radius * np.cos(theta1)
        z1 = radius * np.sin(theta1)
        theta2 = 2 * np.pi * (i + 1) / subdivisions
        x2 = radius * np.cos(theta2)
        z2 = radius * np.sin(theta2)

        # calculate y component of normal vector
        y = np.sqrt(x1**2 + z1**2) / np.sqrt(x1**2 + z1**2 + height**2)
        normal1_ = np.array([x1, y, z1])
        normal2_ = np.array([x2, y, z2])
        # normalize all normals:
        normal1 = normal1_ / np.linalg.norm(normal1_)
        normal2 = normal2_ / np.linalg.norm(normal2_)
        normal_top = np.array([0, 0, 0])

        vertices.append([x1, -height / 2, z1, normal1[0], normal1[1], normal1[2]])
        indices.append(len(vertices) - 1)
        vertices.append([x2, -height / 2, z2, normal2[0], normal2[1], normal2[2]])
        indices.append(len(vertices) - 1)
        vertices.append([0, height / 2, 0, normal_top[0], normal_top[1], normal_top[2]])
        indices.append(len(vertices) - 1)

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)
