"""This module contains the Sphere and Spheres classes."""

import numpy as np
cimport numpy as npc
from molara.tools.mathtools import norm
from molara.rendering.object3d import Object3D

class Spheres(Object3D):
    """Creates a Sphere object, containing its vertices and indices.

    :param subdivisions: Number of subdivisions of the sphere.
    """

    def __init__(self, subdivisions: int,
                 positions: np.ndarray,
                 radii: np.ndarray,
                 colors: np.ndarray,
                 wire_frame: bool = False,) -> None:
        """Creates a Sphere object, containing its vertices and indices."""
        self.subdivisions = subdivisions
        vertices, indices = generate_sphere(self.subdivisions)
        super().__init__()
        self.wire_frame = wire_frame
        self.vertices = vertices
        self.indices = indices
        self.number_of_instances = len(positions)
        self.number_of_vertices = len(vertices)

        for i in range(self.number_of_instances):
            model_matrix = calculate_sphere_model_matrix(positions[i], radii[i])
            model_matrices = model_matrix if i == 0 else np.concatenate((model_matrices, model_matrix))
        self.model_matrices = model_matrices
        self.colors = colors

        self.generate_buffers()


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

def calculate_sphere_model_matrix(npc.ndarray position,
                                  float radius) -> np.ndarray:
    """Calculates the model matrix for a sphere.

    :param position: Position of the sphere.
    :param radius: Radius of the sphere.
    :return: Model matrix of the sphere.
    """

    cdef npc.ndarray[float, ndim=2] translation_matrix
    cdef npc.ndarray[float, ndim=2] scale_matrix
    cdef npc.ndarray[float, ndim=2] model_matrix

    translation_matrix = np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]], dtype=np.float32)
    translation_matrix[3, 0:3] = position

    scale_matrix =np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]], dtype=np.float32)
    scale_matrix[0,0] = radius
    scale_matrix[1,1] = radius
    scale_matrix[2,2] = radius

    model_matrix = scale_matrix @ translation_matrix
    return np.array(
        [model_matrix],
        dtype=np.float32,
    )
