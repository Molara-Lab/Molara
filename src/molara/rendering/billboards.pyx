"""This module contains the Cylinder and Cylinders classes.

They are used to create cylinders and multiple cylinders of the same color, respectively.
"""

from typing import TYPE_CHECKING

cimport numpy as npc
import numpy as np
from molara.tools.mathtools import norm_float
from molara.rendering.object3d import Object3D

if TYPE_CHECKING:
    from PIL import Image



class Billboards(Object3D):
    """Creates a Cylinder object, containing its vertices and indices."""

    def __init__(self,
                 positions: np.ndarray,
                 normals: np.ndarray,
                 sizes: np.ndarray,
                 texture: Image,) -> None:
        """Create a Cylinder object to be drawn."""
        vertices, indices = generate_billboard()
        super().__init__()
        self.vertices = vertices
        self.indices = indices
        self.number_of_instances = len(positions)
        self.number_of_vertices = len(vertices)
        for i in range(self.number_of_instances):
            model_matrix = calculate_billboard_model_matrix(
                np.array(positions[i], dtype=np.float32),
                np.array(sizes[i], dtype=np.float32),
                np.array(normals[i], dtype=np.float32),
            )
            model_matrices = model_matrix if i == 0 else np.concatenate((model_matrices, model_matrix))
        self.model_matrices = model_matrices
        self.texture = texture
        self.colors = None

        self.generate_buffers()

def generate_billboard() -> tuple[np.ndarray, np.ndarray]:
    """Calculates the vertices and indices of a board in the yz plane.

    :returns:
        - **vertices** (numpy.array of numpy.float32) - Vertices in the following order x,y,z,nx,ny,nz,tx,ty, where\
         xyz are the cartesian coordinates, and nxnynz are the components of the normal\
          vector and tx,ty are the texture coordinates.
        - **indices** (numpy.array of numpy.uint32) - Gives the connectivity of the vertices.
    """
        # position      normal         texture coords
    vertices = [
        0.0, -0.5,  0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
        0.0,  0.5,  0.5, 1.0, 0.0, 0.0, 1.0, 0.0,
        0.0,  0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 1.0,
        0.0, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 1.0,
        ]

    indices = [0, 1, 2, 0, 2, 3]

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

cpdef calculate_billboard_model_matrix(
    npc.ndarray[float, ndim=1] position,
    npc.ndarray[float, ndim=1] size,
    npc.ndarray[float, ndim=1] normal,):
    """Calculates the model matrix for a biilboard.

    :param position: Position of the center of the Billboard.
    :param size: size of the billborad.
    :param normal: normal of the billboard, does not need to be normalized.
    """
    cdef npc.ndarray[float, ndim=1] rotation_axis = np.empty(3, dtype=np.float32)
    cdef float rotation_angle, x, y, z, c, s, t
    cdef npc.ndarray[float, ndim=2] rotation_scale_matrix
    cdef npc.ndarray[float, ndim=2] scale_matrix
    cdef npc.ndarray[float, ndim=2] rotation_matrix
    cdef npc.ndarray[float, ndim=2] translation_matrix
    cdef float[3] x_axis = np.array([1, 0, 0], dtype=np.float32)
    cdef float normal_norm = norm_float(normal)
    normal = normal / normal_norm
    cdef float dot = np.dot(normal, x_axis)
    if abs(dot) != 1:
        rotation_axis = np.array([
        x_axis[1] * normal[2] - x_axis[2] * normal[1],
        x_axis[2] * normal[0] - x_axis[0] * normal[2],
        x_axis[0] * normal[1] - x_axis[1] * normal[0]
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

    scale_matrix =np.array([[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]], dtype=np.float32)
    scale_matrix[0, 0] = size[0]
    scale_matrix[1, 1] = size[1]
    scale_matrix[2, 2] = size[2]
    rotation_scale_matrix = scale_matrix @ rotation_matrix
    return np.array([rotation_scale_matrix @ translation_matrix], dtype=np.float32)
