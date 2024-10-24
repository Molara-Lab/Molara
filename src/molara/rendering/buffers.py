"""Contains functions to set up vertex attribute objects and vertex buffer objects."""

from __future__ import annotations

import ctypes
from typing import TYPE_CHECKING

import numpy as np
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_DYNAMIC_DRAW,
    GL_ELEMENT_ARRAY_BUFFER,
    GL_FALSE,
    GL_FLOAT,
    GL_STATIC_DRAW,
    GL_UNSIGNED_INT,
    glBindBuffer,
    glBindVertexArray,
    glBufferData,
    glEnableVertexAttribArray,
    glGenBuffers,
    glGenVertexArrays,
    glVertexAttribDivisor,
    glVertexAttribIPointer,
    glVertexAttribPointer,
)

if TYPE_CHECKING:
    import numpy as np

__copyright__ = "Copyright 2024, Molara"


def setup_vao(
    vertices: np.ndarray,
    indices: np.ndarray | None,
    model_matrices: np.ndarray,
    colors: np.ndarray,
) -> tuple[int, list[int]]:
    """Set up a vertex attribute object and binds it to the GPU.

    :param vertices: Vertices in the following order x,y,z,r,g,b,nx,ny,nz,..., where xyz are the cartesian coordinates,
        rgb are the color values [0,1], and nxnynz are the components of the normal vector.
    :param indices: Gives the connectivity of the vertices.
    :param model_matrices: Each matrix gives the transformation from object space to world.
    :param colors: Colors of the vertices.
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
    if indices is not None:
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    else:
        ebo = None

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
    if indices is not None:
        buffers = [vbo, ebo, instance_vbo_color, instance_vbo_model]
    else:
        buffers = [vbo, instance_vbo_color, instance_vbo_model]
    glBindVertexArray(0)

    return vao, buffers


def setup_vao_numbers(digits: np.ndarray, positions_3d: np.ndarray) -> tuple[int, list[int]]:
    """Set up a vertex attribute object and binds it to the GPU.

    :param digits: The digits to be displayed.
    :param positions_3d: The 3D positions of the atoms.
    :return: Returns a bound vertex attribute object
    """
    # Generate and bind VAO
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Generate and bind VBO for instance data
    instance_vbo_digits = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instance_vbo_digits)
    glBufferData(GL_ARRAY_BUFFER, digits, GL_DYNAMIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribIPointer(0, 1, GL_UNSIGNED_INT, digits.itemsize, ctypes.c_void_p(0))

    # Generate and bind VBO for instance data
    instance_vbo_positions_3d = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, instance_vbo_positions_3d)
    glBufferData(GL_ARRAY_BUFFER, positions_3d, GL_DYNAMIC_DRAW)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, instance_vbo_positions_3d.itemsize * 3, ctypes.c_void_p(0))

    buffers = [instance_vbo_digits, instance_vbo_positions_3d]
    glBindVertexArray(0)

    return vao, buffers
