"""This module contains the Sphere and Spheres classes."""

import numpy as np
from molara.tools.mathtools import norm
from molara.rendering.object3d import Object3D
from molara.rendering.matrices import calculate_scale_matrices

class Spheres(Object3D):
    """Creates a Sphere object, containing its vertices and indices.

    :param subdivisions: Number of subdivisions of the sphere.
    """

    def __init__(self, subdivisions: int,
                 positions: np.ndarray,
                 radii: np.ndarray,
                 colors: np.ndarray,
                 wire_frame: bool = False,) -> None:
        """Creates a Sphere object, containing its vertices and indices.

        :param subdivisions: Number of subdivisions of the sphere.
        :param positions: Positions of the spheres. A 2D numpy array of shape (n, 3).
        :param radii: Radii of the spheres. A 1D numpy array of shape (n,).
        :param colors: Colors of the spheres. A 2D numpy array of shape (n, 3).
        :param wire_frame: If True, the sphere will be rendered as a wire frame."""
        self.subdivisions = subdivisions
        vertices, indices = generate_sphere(self.subdivisions)
        super().__init__()
        self.wire_frame = wire_frame
        self.vertices = vertices
        self.indices = indices
        self.number_of_instances = len(positions)
        self.number_of_vertices = len(vertices)
        self.number_of_indices = len(indices)

        self.calculate_translation_matrices(positions)
        self.calculate_scaling_matrices(radii)
        eye_matrix = np.eye(4, dtype=np.float32)
        self.rotation_matrices = np.array([eye_matrix for _ in range(self.number_of_instances)], dtype=np.float32)
        self.calculate_model_matrices()

        self.colors = colors

    def calculate_scaling_matrices(self, radii: np.ndarray) -> None:
        """Calculates the scaling matrices for the spheres.

        This is a special case as, a sphere needs to be scaled uniformly.
        :param radii: Dimensions of the spheres.
        """
        dimensions = np.zeros((self.number_of_instances, 3), dtype=np.float32)
        dimensions[:, 0] = radii
        dimensions[:, 1] = radii
        dimensions[:, 2] = radii
        self.scaling_matrices = calculate_scale_matrices(dimensions)


def generate_sphere(
    subdivisions: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculates the vertices and indices of a sphere for a given number of subdivisions.

    :param subdivisions: Number of subdivisions of the sphere.
    :returns:
        - **vertices** (numpy.array of numpy.float32) - Vertices in the following order x,y,z,nx,ny,nz,..., where\
         xyz are the cartesian coordinates and nxnynz are the components of the normal\
          vector.
        - **indices** (numpy.array of numpy.uint32) - Gives the connectivity of the vertices.
    """
    vertices = []
    indices = []

    for i in range(subdivisions + 1):
        phi = np.pi * (i / subdivisions - 0.5)
        y = np.sin(phi)

        for j in range(subdivisions * 2 + 1):
            theta = 2 * np.pi * j / (subdivisions * 2)
            x = np.cos(theta) * np.cos(phi)
            z = np.sin(theta) * np.cos(phi)

            normal = np.array([x, y, z])
            normal /= norm(normal)
            vertices.extend(
                [
                    x,
                    y,
                    z,
                    normal[0],
                    normal[1],
                    normal[2],
                ],
            )
            if j < subdivisions * 2 and i < subdivisions:
                p1 = i * (subdivisions * 2 + 1) + j
                p2 = p1 + 1
                p3 = p1 + subdivisions * 2 + 1
                p4 = p3 + 1

                indices.extend([p1, p2, p3, p3, p2, p4])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)
