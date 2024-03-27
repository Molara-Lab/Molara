"""Contains functions to set up vertex attribute objects and vertex buffer objects."""

from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING

from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_DYNAMIC_DRAW,
    GL_ELEMENT_ARRAY_BUFFER,
    GL_FALSE,
    GL_FLOAT,
    GL_STATIC_DRAW,
    glBindBuffer,
    glBindVertexArray,
    glBufferData,
    glEnableVertexAttribArray,
    glGenBuffers,
    glGenVertexArrays,
    glVertexAttribDivisor,
    glVertexAttribPointer,
)

if TYPE_CHECKING:
    import numpy as np

__copyright__ = "Copyright 2024, Molara"


def setup_vao(
    vertices: np.ndarray,
    indices: np.ndarray,
    model_matrices: np.ndarray,
    colors: np.ndarray,
) -> tuple[int, list[int]]:
    """Set up a vertex attribute object and binds it to the GPU.

    :param vertices: Vertices in the following order x,y,z,r,g,b,nx,ny,nz,..., where xyz are the cartesian coordinates,
        rgb are the color values [0,1], and nxnynz are the components of the normal vector.
    :type vertices: numpy.array of numpy.float32
    :param indices: Gives the connectivity of the vertices.
    :type indices: numpy.array of numpy.uint32
    :param model_matrices: Each matrix gives the transformation from object space to world.
    :type model_matrices: numpy.array of numpy.float32
    :param colors: Colors of the vertices.
    :type colors: numpy.array of numpy.float32
    :return: Returns a bound vertex attribute object
    """
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Vertex positions
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(
        0,
        3,
        GL_FLOAT,
        GL_FALSE,
        vertices.itemsize * 6,
        ctypes.c_void_p(0),
    )

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(
        1,
        3,
        GL_FLOAT,
        GL_FALSE,
        vertices.itemsize * 6,
        ctypes.c_void_p(12),
    )

    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # Instance colors
    instance_vbo_color = glGenBuffers(1)
    num_instances = len(colors)
    glBindBuffer(GL_ARRAY_BUFFER, instance_vbo_color)
    glBufferData(
        GL_ARRAY_BUFFER,
        num_instances * 3 * colors.itemsize,
        colors,
        GL_DYNAMIC_DRAW,
    )
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(
        2,
        3,
        GL_FLOAT,
        GL_FALSE,
        colors.itemsize * 3,
        ctypes.c_void_p(0),
    )
    glVertexAttribDivisor(2, 1)

    # Instance matrices
    instance_vbo_model = glGenBuffers(1)
    num_instances = len(model_matrices)
    glBindBuffer(GL_ARRAY_BUFFER, instance_vbo_model)
    glBufferData(
        GL_ARRAY_BUFFER,
        num_instances * 16 * model_matrices.itemsize,
        model_matrices,
        GL_DYNAMIC_DRAW,
    )

    for i in range(4):
        glEnableVertexAttribArray(3 + i)
        glVertexAttribPointer(
            3 + i,
            4,
            GL_FLOAT,
            GL_FALSE,
            16 * 4,
            ctypes.c_void_p(i * 16),
        )
        glVertexAttribDivisor(3 + i, 1)
    buffers = [vbo, ebo, instance_vbo_color, instance_vbo_model]
    glBindVertexArray(0)

    return vao, buffers
