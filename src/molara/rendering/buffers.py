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
    GL_LINEAR,
    GL_REPEAT,
    GL_RGBA,
    GL_STATIC_DRAW,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_UNSIGNED_BYTE,
    glBindBuffer,
    glBindTexture,
    glBindVertexArray,
    glBufferData,
    glEnableVertexAttribArray,
    glGenBuffers,
    glGenTextures,
    glGenVertexArrays,
    glTexImage2D,
    glTexParameteri,
    glVertexAttribDivisor,
    glVertexAttribPointer,
)
from PIL import Image

if TYPE_CHECKING:
    import numpy as np


__copyright__ = "Copyright 2024, Molara"


class Buffers:
    """Store the different buffers for rendering."""

    def __init__(self) -> None:
        """Initialize the Buffer class."""
        self.vbo = -1
        self.ebo = -1
        self.instance_vbo_color = -1
        self.instance_vbo_model = -1
        self.texture = -1

    def save_buffer(
        self,
        vbo: int = -1,
        instance_vbo_color: int = -1,
        instance_vbo_model: int = -1,
        ebo: int = -1,
        texture: int = -1,
    ) -> None:
        """Save the buffers to delete or modify later.

        :param vbo: Pointer to the vbo object.
        :param instance_vbo_color: Pointer to the instance_vbo_color object.
        :param instance_vbo_model: Pointer to the instance_vbo_model object.
        :param texture: Pointer to the texture buffer.
        :param ebo: Pointer to the ebo object.
        """
        self.vbo = vbo
        self.ebo = ebo
        self.instance_vbo_color = instance_vbo_color
        self.instance_vbo_model = instance_vbo_model
        self.texture = texture


def setup_vao(  # noqa: PLR0913
    vertices: np.ndarray,
    indices: np.ndarray | None,
    num_instances: int,
    model_matrices: np.ndarray,
    colors: None | np.ndarray,
    texture: bool = False,
) -> tuple[int, list[int]]:
    """Set up a vertex attribute object and binds it to the GPU.

    :param vertices: Vertices in the following order x,y,z,r,g,b,nx,ny,nz,..., where xyz are the cartesian coordinates,
        rgb are the color values [0,1], and nxnynz are the components of the normal vector.
    :param indices: Gives the connectivity of the vertices.
    :param num_instances: Number of instances of the object.
    :param model_matrices: Each matrix gives the transformation from object space to world.
    :param colors: Colors of the vertices.
    :param texture: If True, the object has a texture and the vao pointers need to be adapted
    :return: Returns a bound vertex attribute object
    """
    vertex_attribute_positions_pointer_start = 0
    vertex_attribute_normals_pointer_start = 12
    vertex_attribute_texture_pointer_start = 24
    vertex_attribute_pointer_offset = 8 if texture else 6

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
        vertices.itemsize * vertex_attribute_pointer_offset,
        ctypes.c_void_p(vertex_attribute_positions_pointer_start),
    )

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(
        1,
        3,
        GL_FLOAT,
        GL_FALSE,
        vertices.itemsize * vertex_attribute_pointer_offset,
        ctypes.c_void_p(vertex_attribute_normals_pointer_start),
    )
    if texture:
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(
            2,
            2,
            GL_FLOAT,
            GL_FALSE,
            vertices.itemsize * vertex_attribute_pointer_offset,
            ctypes.c_void_p(vertex_attribute_texture_pointer_start),
        )
    if indices is not None:
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    else:
        ebo = -1

    # Instance colors
    if colors is not None:
        instance_vbo_color = glGenBuffers(1)
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
    else:
        instance_vbo_color = -1

    # Instance matrices
    instance_vbo_model = glGenBuffers(1)
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


def setup_texture_buffer(texture: bool | Image.Image) -> int:
    """Set up the texture buffer.

    :param texture: The texture to be used, as a PIL Image object.
    """
    assert isinstance(texture, Image.Image)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    img_data = texture.convert("RGBA").tobytes()

    # Set texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Upload the texture data
    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        texture.width,
        texture.height,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        img_data,
    )

    # glBindTexture(GL_TEXTURE_2D, 0)  # Unbind the texture
    return texture_id
