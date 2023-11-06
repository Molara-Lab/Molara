"""Contains the rendering function for the opengl widget."""

# mypy: disable-error-code="name-defined"
from __future__ import annotations

from typing import TYPE_CHECKING

import pyrr
from OpenGL.GL import *

from molara.Rendering.buffers import setup_vao

if TYPE_CHECKING:
    import numpy as np

    from molara.Rendering.camera import Camera

atoms_vao: dict = {"vao": 0, "n_atoms": 0, "n_vertices": 0, "buffers": []}
bonds_vao: dict = {"vao": 0, "n_bonds": 0, "n_vertices": 0, "buffers": []}


class Renderer:
    """Contains the rendering function for the opengl widget."""

    def __init__(self) -> None:
        """Creates a Renderer object."""
        self.atoms_vao: dict = {"vao": 0, "n_atoms": 0, "n_vertices": 0, "buffers": []}
        self.bonds_vao: dict = {"vao": 0, "n_bonds": 0, "n_vertices": 0, "buffers": []}
        self.shader: GLuint = 0

    def set_shader(self, shader: GLuint) -> None:
        """Sets the shader program for the opengl widget.

        :param shader: The shader program of the opengl widget.
        :type shader: pyopengl program
        """
        self.shader = shader

    def update_atoms_vao(
        self,
        vertices: np.ndarray,
        indices: np.ndarray,
        model_matrices: np.ndarray,
        colors: np.ndarray,
    ) -> None:
        """Updates the vertex attribute object for the atoms.

        :param vertices: Vertices in the following order x,y,z,nx,ny,nz,..., where xyz are the cartesian coordinates.
        :type vertices: numpy.array of numpy.float32
        :param indices: Gives the connectivity of the vertices.
        :type indices: numpy.array of numpy.uint32
        :param model_matrices: Each matrix gives the transformation from object space to world.
        :type model_matrices: numpy.array of numpy.float32
        :param colors: Colors of the atoms.
        :type colors: numpy.array of numpy.float32
        :return:
        """
        if self.atoms_vao["vao"] == 0:
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            for buffer in atoms_vao["buffers"]:
                glDeleteBuffers(1, buffer)
            glDeleteVertexArrays(1, atoms_vao["vao"])
        self.atoms_vao["vao"], atoms_vao["buffers"] = setup_vao(
            vertices,
            indices,
            model_matrices,
            colors,
        )
        self.atoms_vao["n_atoms"] = len(model_matrices)
        self.atoms_vao["n_vertices"] = len(vertices)

    def update_bonds_vao(
        self,
        vertices: np.ndarray,
        indices: np.ndarray,
        model_matrices: np.ndarray,
        colors: np.ndarray,
    ) -> None:
        """Updates the vertex attribute object for the bonds.

        :param vertices: Vertices in the following order x,y,z,nx,ny,nz,..., where xyz are the cartesian coordinates.
        :type vertices: numpy.array of numpy.float32
        :param indices: Gives the connectivity of the vertices.
        :type indices: numpy.array of numpy.uint32
        :param model_matrices: Each matrix gives the transformation from object space to world.
        :type model_matrices: numpy.array of numpy.float32
        :param colors: Colors of the bonds.
        :type colors: numpy.array of numpy.float32
        :return:
        """
        if self.bonds_vao["vao"] == 0:
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            for buffer in bonds_vao["buffers"]:
                glDeleteBuffers(1, buffer)
            glDeleteVertexArrays(1, bonds_vao["vao"])
        self.bonds_vao["vao"], bonds_vao["buffers"] = setup_vao(
            vertices,
            indices,
            model_matrices,
            colors,
        )
        self.bonds_vao["n_bonds"] = len(model_matrices)
        self.bonds_vao["n_vertices"] = len(vertices)

    def draw_scene(
        self,
        camera: Camera,
    ) -> None:
        """Draws the contents of the given vaos from the given camera perspective.

        :param shader: The shader program of the opengl widget.
        :type shader: pyopengl program
        :param camera: The camera object to capture the scene.
        :type camera: Camera
        :param vaos: The vertex array object pointers for the opengl draw call.
        :type vaos: GL_INT
        """
        view_mat = pyrr.matrix44.create_look_at(
            pyrr.Vector3(camera.position),
            pyrr.Vector3(camera.target),
            pyrr.Vector3(camera.up_vector),
        )

        light_direction_loc = glGetUniformLocation(self.shader, "light_direction")
        proj_loc = glGetUniformLocation(self.shader, "projection")
        camera_loc = glGetUniformLocation(self.shader, "camera_position")
        view_loc = glGetUniformLocation(self.shader, "view")

        light_direction = -camera.position - camera.up_vector * camera.distance_from_target * 0.5
        glUniform3fv(light_direction_loc, 1, light_direction)
        glUniform3fv(camera_loc, 1, camera.position)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, camera.projection_matrix)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_mat)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBindVertexArray(self.atoms_vao["vao"])
        glDrawElementsInstanced(
            GL_TRIANGLES,
            self.atoms_vao["n_vertices"],
            GL_UNSIGNED_INT,
            None,
            self.atoms_vao["n_atoms"],
        )
        glBindVertexArray(self.bonds_vao["vao"])
        glDrawElementsInstanced(
            GL_TRIANGLES,
            self.bonds_vao["n_vertices"],
            GL_UNSIGNED_INT,
            None,
            self.bonds_vao["n_bonds"],
        )
        glBindVertexArray(0)
