"""This module contains the Cylinder and Cylinders classes.

They are used to create cylinders and multiple cylinders of the same color, respectively.
"""

cimport numpy as npc
import numpy as np
from molara.tools.mathtools import norm_float


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
    radius = 1.0
    vertices.extend([0.0, -height / 2, 0.0, 0.0, -1, 0.0])
    vertices.extend([0.0, height / 2, 0.0, 0.0, 1, 0.0])
    for i in range(subdivisions):
        # vertices
        theta = 2 * np.pi * i / subdivisions
        x = radius * np.cos(theta)
        y = -height / 2
        z = radius * np.sin(theta)
        normal = np.array([x, 0, z],dtype=np.float32)
        normal /= norm_float(normal)
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


cpdef calculate_cylinder_model_matrix(
    npc.ndarray[float, ndim=1] position,
    float radius,
    float length,
    npc.ndarray[float, ndim=1] direction,
):
    """Calculates the model matrix for a cylinder.

    :param position: Position of the center of the cylinder.
    :param radius: Radius of the cylinder.
    :param length: Length of the cylinder.
    :param direction: Direction of the cylinder, does not need to be normalized.
    """
    cdef npc.ndarray[float, ndim=1] rotation_axis = np.empty(3, dtype=np.float32)
    cdef float rotation_angle, x, y, z, c, s, t
    cdef npc.ndarray[float, ndim=2] rotation_scale_matrix
    cdef npc.ndarray[float, ndim=2] scale_matrix
    cdef npc.ndarray[float, ndim=2] rotation_matrix
    cdef npc.ndarray[float, ndim=2] translation_matrix
    cdef float[3] y_axis = np.array([0, 1, 0], dtype=np.float32)
    cdef float direction_norm = norm_float(direction)
    direction = direction / direction_norm
    cdef float dot = np.dot(direction, y_axis)
    if abs(dot) != 1:
        rotation_axis = np.array([
        y_axis[1] * direction[2] - y_axis[2] * direction[1],
        y_axis[2] * direction[0] - y_axis[0] * direction[2],
        y_axis[0] * direction[1] - y_axis[1] * direction[0]
        ], dtype=np.float32)
        # Calculate the angle to rotate the cylinder to the correct orientation.
        rotation_angle = np.arccos(
            np.clip(
                dot,
                -1,
                1,
            ),
        )
    else:
        rotation_axis = np.array([0, 0, 1], dtype=np.float32)
        rotation_angle = 0
    translation_matrix = np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]], dtype=np.float32)
    translation_matrix[3, 0:3] = position

    rotation_matrix = np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]], dtype=np.float32)

    rotation_axis = rotation_axis / norm_float(rotation_axis)
    x, y, z = rotation_axis
    c = np.cos(rotation_angle)
    s = np.sin(rotation_angle)
    t = 1 - c

    rotation_matrix[:3, :3] = np.array([
        [t*x*x + c, t*x*y + s*z, t*x*z - s*y],
        [t*x*y - s*z, t*y*y + c, t*y*z + s*x],
        [t*x*z + s*y, t*y*z - s*x, t*z*z + c]]
    , dtype=np.float32)

    cdef float[3] scale = [radius, radius, radius]
    scale[1] = length
    scale_matrix =np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]], dtype=np.float32)
    scale_matrix[0, 0] = scale[0]
    scale_matrix[1, 1] = scale[1]
    scale_matrix[2, 2] = scale[2]
    rotation_scale_matrix = scale_matrix @ rotation_matrix
    return np.array([rotation_scale_matrix @ translation_matrix], dtype=np.float32)
