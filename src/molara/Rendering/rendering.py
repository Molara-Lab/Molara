"""Contains the rendering function for the opengl widget."""

# mypy: disable-error-code="name-defined"
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_ELEMENT_ARRAY_BUFFER,
    GL_FALSE,
    GL_TRIANGLES,
    GL_UNSIGNED_INT,
    GLuint,
    glBindBuffer,
    glBindVertexArray,
    glClear,
    glDeleteBuffers,
    glDeleteVertexArrays,
    glDrawElementsInstanced,
    glGetUniformLocation,
    glUniform3fv,
    glUniformMatrix4fv,
)

from molara.Rendering.buffers import setup_vao
from molara.Rendering.cylinder import Cylinder, calculate_cylinder_model_matrix
from molara.Rendering.sphere import Sphere, calculate_sphere_model_matrix

if TYPE_CHECKING:
    from numpy import floating

    from molara.Rendering.camera import Camera

__copyright__ = "Copyright 2024, Molara"


class Renderer:
    """Contains the rendering function for the opengl widget."""

    def __init__(self) -> None:
        """Create a Renderer object."""
        self.atoms_vao: dict = {"vao": 0, "n_atoms": 0, "n_vertices": 0, "buffers": []}
        self.bonds_vao: dict = {"vao": 0, "n_bonds": 0, "n_vertices": 0, "buffers": []}
        self.spheres: list[dict] = []
        self.cylinders: list[dict] = []
        self.shader: GLuint = 0

    def set_shader(self, shader: GLuint) -> None:
        """Set the shader program for the opengl widget.

        :param shader: The shader program of the opengl widget.
        :type shader: pyopengl program
        """
        self.shader = shader

    def draw_cylinders(  # noqa: PLR0913
        self,
        positions: np.ndarray,
        directions: np.ndarray,
        radii: np.ndarray,
        lengths: np.ndarray,
        colors: np.ndarray,
        subdivisions: int,
    ) -> int:
        """Draws one or multiple cylinders.

        If only one cylinder is drawn, the positions, directions, radii, lengths and colors are given as np.ndarray
        containing only one array, for instance: positions = np.array([[0, 0, 0]]). If multiple cylinders are drawn,
        the positions, directions, radii, lengths and colors are given as np.ndarray containing multiple arrays, for
        instance: positions = np.array([[0, 0, 0], [1, 1, 1]]).

        :param positions: Positions of the cylinders.
        :type positions: numpy.array of numpy.float32
        :param directions: Directions of the cylinders.
        :type directions: numpy.array of numpy.float32
        :param radii: Radii of the cylinders.
        :type radii: numpy.array of numpy.float32
        :param lengths: Lengths of the cylinders.
        :type lengths: numpy.array of numpy.float32
        :param colors: Colors of the cylinders.
        :type colors: numpy.array of numpy.float32
        :param subdivisions: Number of subdivisions of the cylinder.
        :type subdivisions: int
        :return: Returns the index of the cylinder in the list of cylinders.
        """
        n_instances = len(positions)
        cylinder_mesh = Cylinder(subdivisions)

        model_matrices = np.array([])

        for i in range(n_instances):
            model_matrix = calculate_cylinder_model_matrix(
                np.array(positions[i], dtype=np.float32),
                float(radii[i]),
                float(lengths[i]),
                np.array(directions[i], dtype=np.float32),
            )
            model_matrices = model_matrix if i == 0 else np.concatenate((model_matrices, model_matrix))

        cylinder = {
            "vao": 0,
            "n_instances": n_instances,
            "n_vertices": len(cylinder_mesh.vertices),
            "buffers": [],
        }
        cylinder["vao"], cylinder["buffers"] = setup_vao(
            cylinder_mesh.vertices,
            cylinder_mesh.indices,
            model_matrices,
            colors,
        )

        # get index of new cylinder instances in list
        i_cylinder = -1

        if len(self.cylinders) == 0:
            i_cylinder = 0
            self.cylinders.append(cylinder)
            return i_cylinder

        for i, check_cylinder in enumerate(self.cylinders):
            if check_cylinder["vao"] == 0:
                i_cylinder = i
                self.cylinders[i_cylinder] = cylinder
                break

        if i_cylinder == -1:
            i_cylinder = len(self.cylinders)
            self.cylinders.append(cylinder)

        return i_cylinder

    def draw_cylinders_from_to(
        self,
        positions: np.ndarray,
        radii: np.ndarray,
        colors: np.ndarray,
        subdivisions: int,
    ) -> int:
        """Draws one or multiple cylinders.

        :param positions: Positions [[start, end], [start, end], ...] of the cylinders.
        :param radii: Radii of the cylinders.
        :param colors: Colors of the cylinders.
        :param subdivisions: Number of subdivisions of the cylinder.
        :return: Returns the index of the cylinder in the list of cylinders.
        """
        _directions: list[list[floating]] = []
        _lengths: list[floating] = []
        _positions_middle: list[list[list[floating]]] = []
        for pos12 in positions:
            pos1, pos2 = pos12
            _directions.append((pos2 - pos1).tolist())
            _lengths.append(np.linalg.norm(pos2 - pos1))
            _positions_middle.append((0.5 * (pos1 + pos2)).tolist())
        positions_middle = np.array(_positions_middle)
        lengths = np.array(_lengths)
        directions = np.array(_directions) / lengths[:, None]
        return self.draw_cylinders(positions_middle, -directions, radii, lengths, colors, subdivisions)

    def draw_spheres(
        self,
        positions: np.ndarray,
        radii: np.ndarray,
        colors: np.ndarray,
        subdivisions: int,
    ) -> int:
        """Draws one or multiple spheres.

        If only one sphere is drawn, the positions, radii and colors are given
        as np.ndarray containing only one array, for instance: positions = np.array([[0, 0, 0]]). If multiple
        spheres are drawn, the positions, radii and colors are given as np.ndarray containing multiple arrays, for
        instance: positions = np.array([[0, 0, 0], [1, 1, 1]]).

        :param positions: Positions of the spheres.
        :type positions: numpy.array of numpy.float32
        :param radii: Radii of the spheres.
        :type radii: numpy.array of numpy.float32
        :param colors: Colors of the spheres.
        :type colors: numpy.array of numpy.float32
        :param subdivisions: Number of subdivisions of the sphere.
        :type subdivisions: int
        :return: Returns the index of the sphere in the list of spheres.
        """
        n_instances = len(positions)
        sphere_mesh = Sphere(subdivisions)
        if n_instances == 1:
            model_matrices = calculate_sphere_model_matrix(positions[0], radii[0])
        else:
            for i in range(n_instances):
                model_matrix = calculate_sphere_model_matrix(positions[i], radii[i])
                model_matrices = model_matrix if i == 0 else np.concatenate((model_matrices, model_matrix))

        sphere = {
            "vao": 0,
            "n_instances": n_instances,
            "n_vertices": len(sphere_mesh.vertices),
            "buffers": [],
        }
        sphere["vao"], sphere["buffers"] = setup_vao(
            sphere_mesh.vertices,
            sphere_mesh.indices,
            model_matrices,
            colors,
        )

        # get index of new sphere instances in list
        i_sphere = -1
        if len(self.spheres) != 0:
            for i, check_sphere in enumerate(self.spheres):
                if check_sphere["vao"] == 0:
                    i_sphere = i
                    self.spheres[i_sphere] = sphere
            if i_sphere == -1:
                i_sphere = len(self.spheres)
                self.spheres.append(sphere)
        else:
            i_sphere = 0
            self.spheres.append(sphere)
        return i_sphere

    def remove_cylinder(self, i_cylinder: int) -> None:
        """Remove a cylinder from the list of cylinders.

        :param i_cylinder: Index of the cylinder to remove.
        :type i_cylinder: int
        :return:
        """
        if i_cylinder >= len(self.cylinders):
            return

        cylinder = self.cylinders[i_cylinder]
        if cylinder["vao"] != 0:
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            for buffer in cylinder["buffers"]:
                glDeleteBuffers(1, [buffer])
            glDeleteVertexArrays(1, [cylinder["vao"]])
        self.cylinders[i_cylinder] = {
            "vao": 0,
            "n_instances": 0,
            "n_vertices": 0,
            "buffers": [],
        }

    def remove_sphere(self, i_sphere: int) -> None:
        """Remove a sphere from the list of spheres.

        :param i_sphere: Index of the sphere to remove.
        :type i_sphere: int
        :return:
        """
        if i_sphere < len(self.spheres):
            sphere = self.spheres[i_sphere]
            if sphere["vao"] != 0:
                glBindBuffer(GL_ARRAY_BUFFER, 0)
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
                for buffer in sphere["buffers"]:
                    glDeleteBuffers(1, [buffer])
                glDeleteVertexArrays(1, [sphere["vao"]])
            self.spheres[i_sphere] = {
                "vao": 0,
                "n_instances": 0,
                "n_vertices": 0,
                "buffers": [],
            }

    def update_atoms_vao(
        self,
        vertices: np.ndarray,
        indices: np.ndarray,
        model_matrices: np.ndarray,
        colors: np.ndarray,
    ) -> None:
        """Update the vertex attribute object for the atoms.

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
        if self.atoms_vao["vao"] != 0:
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            for buffer in self.atoms_vao["buffers"]:
                glDeleteBuffers(1, buffer)
            glDeleteVertexArrays(1, self.atoms_vao["vao"])
        self.atoms_vao["vao"], self.atoms_vao["buffers"] = setup_vao(
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
        """Update the vertex attribute object for the bonds.

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
        if self.bonds_vao["vao"] != 0:
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            for buffer in self.bonds_vao["buffers"]:
                glDeleteBuffers(1, buffer)
            glDeleteVertexArrays(1, self.bonds_vao["vao"])
        self.bonds_vao["vao"], self.bonds_vao["buffers"] = setup_vao(
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
        bonds: bool,
    ) -> None:
        """Draws the scene.

        :param camera: Camera object.
        :type camera: Camera
        :param bonds: If True, bonds are drawn.
        :type bonds: bool
        :return:
        """
        light_direction_loc = glGetUniformLocation(self.shader, "light_direction")
        proj_loc = glGetUniformLocation(self.shader, "projection")
        camera_loc = glGetUniformLocation(self.shader, "camera_position")
        view_loc = glGetUniformLocation(self.shader, "view")

        light_direction = -camera.position - camera.up_vector * camera.distance_from_target * 0.5
        glUniform3fv(light_direction_loc, 1, light_direction)
        glUniform3fv(camera_loc, 1, camera.position)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, camera.projection_matrix)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, camera.view_matrix)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw atoms
        if self.atoms_vao["vao"] != 0:
            glBindVertexArray(self.atoms_vao["vao"])
            glDrawElementsInstanced(
                GL_TRIANGLES,
                self.atoms_vao["n_vertices"],
                GL_UNSIGNED_INT,
                None,
                self.atoms_vao["n_atoms"],
            )

        # Draw bonds
        if self.bonds_vao["vao"] != 0 and bonds:
            glBindVertexArray(self.bonds_vao["vao"])
            glDrawElementsInstanced(
                GL_TRIANGLES,
                self.bonds_vao["n_vertices"],
                GL_UNSIGNED_INT,
                None,
                self.bonds_vao["n_bonds"],
            )

        # Draw spheres
        for sphere in self.spheres:
            if sphere["vao"] != 0:
                glBindVertexArray(sphere["vao"])
                glDrawElementsInstanced(
                    GL_TRIANGLES,
                    sphere["n_vertices"],
                    GL_UNSIGNED_INT,
                    None,
                    sphere["n_instances"],
                )

        # Draw cylinders
        for cylinder in self.cylinders:
            if cylinder["vao"] != 0:
                glBindVertexArray(cylinder["vao"])
                glDrawElementsInstanced(
                    GL_TRIANGLES,
                    cylinder["n_vertices"],
                    GL_UNSIGNED_INT,
                    None,
                    cylinder["n_instances"],
                )
        glBindVertexArray(0)
