"""Contain an abstract class for objects to inherit."""
import numpy as np
from molara.rendering.buffers import Buffers, setup_texture_buffer, setup_vao
from molara.rendering.matrices import (calculate_model_matrices, calculate_rotation_matrices,
                                       calculate_scale_matrices, calculate_translation_matrices)
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_ELEMENT_ARRAY_BUFFER,
    glBindBuffer,
    glBindVertexArray,
    glDeleteBuffers,
    glDeleteVertexArrays,
)


class Object3D:
    """General class for object to be rendered."""

    def __init__(self) -> None:
        """Initialize the Object3D class."""
        self.vao: int = 0
        self.wire_frame: bool = False
        self.number_of_instances = 0
        self.buffers = Buffers()
        self.number_of_vertices = 0
        self.colors = np.array([])

        self.translation_matrices = np.array([])
        self.rotation_matrices = np.array([])
        self.scaling_matrices = np.array([])
        self.model_matrices = np.array([])

        self.indices = np.array([])
        self.vertices = np.array([])
        self.texture = None

    def calculate_translation_matrices(self, positions: np.ndarray):
        """Calculates the translation matrices for the cylinders.

        :param positions: Positions the object should be translated to.
        """
        self.translation_matrices = calculate_translation_matrices(positions)

    def calculate_scaling_matrices(self, dimensions: np.ndarray):
        """Calculates the translation matrices for the cylinders.

        :param dimensions: Dimensions (in x, y, and z) the object should be scaled to.
        """
        self.scaling_matrices = calculate_scale_matrices(dimensions)

    def calculate_rotation_matrices(self, directions: np.ndarray):
        """Calculates the rotation matrices for the cylinders.

        :param directions: Direction the object should be rotated to (original direction must be y axis).
        """
        self.rotation_matrices = calculate_rotation_matrices(directions)

    def calculate_model_matrices(self) -> None:
        """Calculate the model matrices."""
        self.model_matrices = calculate_model_matrices(
            self.translation_matrices, self.scaling_matrices, self.rotation_matrices
        )

    def generate_buffers(self) -> None:
        """Generate the vertex attribute objects and buffers for a given object."""
        # remember to put the buffer association into the setup function!!!
        self.vao, buffers = setup_vao(
            self.vertices,
            self.indices,
            self.number_of_instances,
            self.model_matrices,
            self.colors,
            self.texture,
        )
        if self.texture is not None:
            texture_buffer = setup_texture_buffer(self.texture)
        else:
            texture_buffer = -1
        self.buffers.save_buffer(vbo=buffers[0], ebo=buffers[1],
                                 instance_vbo_color=buffers[2],
                                 instance_vbo_model=buffers[3],
                                 texture=texture_buffer)

    def __del__(self) -> None:
        """Free the GPU memory."""
        if self.vao != 0:
            glBindVertexArray(self.vao)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            buffers = [self.buffers.vbo, self.buffers.ebo,
                       self.buffers.instance_vbo_color, self.buffers.instance_vbo_model]
            for buffer in buffers:
                if buffer != -1:
                    glDeleteBuffers(1, [buffer])
            glDeleteVertexArrays(1, [self.vao])
        glBindVertexArray(0)
