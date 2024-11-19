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
    GL_FILL,
    GL_FRONT_AND_BACK,
    GL_LINE,
    GL_MULTISAMPLE,
    GL_POINTS,
    GL_TRIANGLES,
    GL_UNSIGNED_INT,
    GL_VERTEX_PROGRAM_POINT_SIZE,
    GLuint,
    glBindBuffer,
    glBindVertexArray,
    glClear,
    glDeleteBuffers,
    glDeleteVertexArrays,
    glDisable,
    glDrawArrays,
    glDrawArraysInstanced,
    glDrawElementsInstanced,
    glEnable,
    glGetUniformLocation,
    glPolygonMode,
    glUniform1f,
    glUniform3fv,
    glUniformMatrix4fv,
    glUseProgram,
)

from molara.rendering.buffers import setup_vao, setup_vao_numbers
from molara.rendering.cylinder import Cylinder, calculate_cylinder_model_matrix
from molara.rendering.sphere import Sphere, calculate_sphere_model_matrix

if TYPE_CHECKING:
    from numpy import floating

    from molara.rendering.camera import Camera

__copyright__ = "Copyright 2024, Molara"


class Renderer:
    """Contains the rendering function for the opengl widget."""

    def __init__(self) -> None:
        """Create a Renderer object."""
        self.atoms_vao: dict = {"vao": 0, "n_atoms": 0, "n_vertices": 0, "buffers": []}
        self.bonds_vao: dict = {"vao": 0, "n_bonds": 0, "n_vertices": 0, "buffers": []}
        self.spheres: list[dict] = []
        self.aspect_ratio: float = 1.0
        self.cylinders: list[dict] = []
        self.number_vao: list[dict] = []
        self.shaders: list[GLuint] = [0]
        self.polygons: list[dict] = []
        self.anti_aliasing = True
        self.wire_mesh_surfaces = False

    def enable_antialiasing(self) -> None:
        """Enable antialiasing."""
        self.anti_aliasing = True

    def disable_antialiasing(self) -> None:
        """Disable antialiasing."""
        self.anti_aliasing = False

    def set_shaders(self, shaders: list[GLuint]) -> None:
        """Set the shader program for the opengl widget.

        :param shaders: The shader programs of the opengl widget.
        """
        self.shaders = shaders

    @staticmethod
    def draw_object(
        n_instances: int,
        mesh: Cylinder | Sphere | None,
        vertices: np.ndarray | None,
        model_matrices: np.ndarray,
        colors: np.ndarray,
    ) -> dict:
        """Draws the object."""
        if isinstance(mesh, (Cylinder | Sphere)):
            vertices = np.array(mesh.vertices)
            indices = mesh.indices
            n_vertices = len(vertices)
        elif isinstance(vertices, np.ndarray):
            indices = None
            n_vertices = len(vertices) // 6
        else:
            msg = "Either mesh or vertices must be given."
            raise TypeError(msg)

        obj = {
            "vao": 0,
            "n_instances": n_instances,
            "n_vertices": n_vertices,
            "buffers": [],
        }
        obj["vao"], obj["buffers"] = setup_vao(
            vertices,
            indices,
            model_matrices,
            colors,
        )
        return obj

    def add_object_to_list(self, obj_list: list[dict], obj: dict) -> int:
        """Add an object to the list of objects."""
        # get index of new cylinder instances in list
        i_obj = -1

        if len(obj_list) == 0:
            i_obj = 0
            obj_list.append(obj)
            return i_obj

        for i, check_obj in enumerate(obj_list):
            if check_obj["vao"] == 0:
                i_obj = i
                obj_list[i_obj] = obj
                break

        if i_obj == -1:
            i_obj = len(obj_list)
            obj_list.append(obj)

        return i_obj

    def draw_polygon(
        self,
        vertices: np.ndarray,
        colors: np.ndarray,
    ) -> int:
        """Draw one polygon.

        :param vertices: Vertices in the following order x,y,z,nx,ny,nz,..., where xyz are the cartesian coordinates.
        :param colors: Colors of the vertices.
        :return: Returns the index of the polygon in the list of polygons.
        """
        n_instances = 1
        model_matrices = np.array([np.identity(4, dtype=np.float32)]).reshape((1, 4, 4))
        polygon = Renderer.draw_object(n_instances, None, vertices, model_matrices, colors)
        return self.add_object_to_list(self.polygons, polygon)

    def remove_polygon(self, i_polygon: int) -> None:
        """Remove a polygon from the list of polygon.

        :param i_polygon: Index of the polygon to remove.
        :return:
        """
        if i_polygon >= len(self.polygons):
            return

        polygon = self.polygons[i_polygon]
        self.remove_object(polygon)

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

        cylinder = Renderer.draw_object(n_instances, cylinder_mesh, None, model_matrices, colors)

        return self.add_object_to_list(self.cylinders, cylinder)

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
        model_matrices = np.array([])
        for i in range(n_instances):
            model_matrix = calculate_sphere_model_matrix(positions[i], radii[i])
            model_matrices = model_matrix if i == 0 else np.concatenate((model_matrices, model_matrix))

        sphere = Renderer.draw_object(n_instances, sphere_mesh, None, model_matrices, colors)

        return self.add_object_to_list(self.spheres, sphere)

    def remove_object(self, obj: dict) -> None:
        """Remove an object from the list of objects.

        :param obj: Object to remove.
        :type obj: dict
        :return:
        """
        if obj["vao"] != 0:
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            for buffer in obj["buffers"]:
                glDeleteBuffers(1, [buffer])
            glDeleteVertexArrays(1, [obj["vao"]])
        obj["vao"] = 0
        obj["n_instances"] = 0
        obj["n_vertices"] = 0
        obj["buffers"] = []

    def remove_cylinder(self, i_cylinder: int) -> None:
        """Remove a cylinder from the list of cylinders.

        :param i_cylinder: Index of the cylinder to remove.
        :type i_cylinder: int
        :return:
        """
        if i_cylinder >= len(self.cylinders):
            return

        cylinder = self.cylinders[i_cylinder]
        self.remove_object(cylinder)

    def remove_sphere(self, i_sphere: int) -> None:
        """Remove a sphere from the list of spheres.

        :param i_sphere: Index of the sphere to remove.
        :type i_sphere: int
        :return:
        """
        if i_sphere >= len(self.spheres):
            return

        sphere = self.spheres[i_sphere]
        self.remove_object(sphere)

    @staticmethod
    def update_vao(
        vao_dict: dict,
        vertices: np.ndarray,
        indices: np.ndarray,
        model_matrices: np.ndarray,
        colors: np.ndarray,
    ) -> None:
        """Update the vertex attribute object.

        :param vao_dict: Vertex attribute object.
        :type vao_dict: dict
        :param vertices: Vertices in the following order x,y,z,nx,ny,nz,..., where xyz are the cartesian coordinates.
        :type vertices: numpy.array of numpy.float32
        :param indices: Gives the connectivity of the vertices.
        :type indices: numpy.array of numpy.uint32
        :param model_matrices: Each matrix gives the transformation from object space to world.
        :type model_matrices: numpy.array of numpy.float32
        :param colors: Colors of the object.
        :type colors: numpy.array of numpy.float32
        :return:
        """
        if vao_dict["vao"] != 0:
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
            for buffer in vao_dict["buffers"]:
                glDeleteBuffers(1, int(buffer))
            glDeleteVertexArrays(1, int(vao_dict["vao"]))
        vao_dict["vao"], vao_dict["buffers"] = setup_vao(
            vertices,
            indices,
            model_matrices,
            colors,
        )

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
        Renderer.update_vao(self.atoms_vao, vertices, indices, model_matrices, colors)
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
        Renderer.update_vao(self.bonds_vao, vertices, indices, model_matrices, colors)
        self.bonds_vao["n_bonds"] = len(model_matrices)
        self.bonds_vao["n_vertices"] = len(vertices)

    def draw_numbers(
        self,
        digits: np.ndarray,
        positions_3d: np.ndarray,
    ) -> None:
        """Update the vertex attribute object for the numbers.

        :param digits: Digits of the numbers.
        :param positions_3d: 3D positions of the numbers.
        :return:
        """
        if len(self.number_vao) != 0:
            for number in self.number_vao:
                if number["vao"] != 0:
                    glBindBuffer(GL_ARRAY_BUFFER, 0)
                    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
                    for buffer in number["buffers"]:
                        glDeleteBuffers(1, buffer)
                    glDeleteVertexArrays(1, number["vao"])
        self.number_vao = []

        vao, buffers = setup_vao_numbers(digits, positions_3d)
        self.number_vao.append({"vao": vao, "n_instances": len(digits), "buffers": buffers})

    def draw_scene(  # noqa: C901
        self,
        camera: Camera,
        bonds: bool,
    ) -> None:
        """Draws the scene.

        When bonds are drawn, the bonds are drawn. Otherwise, only the atoms are drawn. When wire mesh surfaces are
        enabled, the surfaces are drawn as wire mesh.

        :param camera: Camera object.
        :param bonds: If True, bonds are drawn.
        :return:
        """
        if not self.anti_aliasing:
            glDisable(GL_MULTISAMPLE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glUseProgram(self.shaders[0])
        light_direction_loc = glGetUniformLocation(self.shaders[0], "light_direction")
        proj_loc = glGetUniformLocation(self.shaders[0], "projection")
        camera_loc = glGetUniformLocation(self.shaders[0], "camera_position")
        view_loc = glGetUniformLocation(self.shaders[0], "view")

        light_direction = -camera.position - camera.up_vector * camera.distance_from_target * 0.5
        glUniform3fv(light_direction_loc, 1, light_direction)
        glUniform3fv(camera_loc, 1, camera.position)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, camera.projection_matrix)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, camera.view_matrix)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        def _draw(obj: dict, n_instances_key: str = "n_instances") -> None:
            if obj["vao"] == 0:
                return
            glBindVertexArray(obj["vao"])
            glDrawElementsInstanced(
                GL_TRIANGLES,
                obj["n_vertices"],
                GL_UNSIGNED_INT,
                None,
                obj[n_instances_key],
            )

        # Draw atoms
        _draw(self.atoms_vao, "n_atoms")

        # Draw bonds
        if bonds:
            _draw(self.bonds_vao, "n_bonds")

        # Draw spheres
        for sphere in self.spheres:
            _draw(sphere, "n_instances")

        # Draw cylinders
        for cylinder in self.cylinders:
            _draw(cylinder, "n_instances")

        # Draw polygons
        if self.wire_mesh_surfaces:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        for polygon in self.polygons:
            if polygon["vao"] != 0:
                glBindVertexArray(polygon["vao"])
                glDrawArraysInstanced(
                    GL_TRIANGLES,
                    0,
                    polygon["n_vertices"],
                    polygon["n_instances"],
                )
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glBindVertexArray(0)
        if not self.anti_aliasing:
            glEnable(GL_MULTISAMPLE)

    def display_numbers(self, camera: Camera, scale_factor: float) -> None:
        """Draws the lines."""
        number_scale = 0.25
        scale = number_scale * scale_factor

        glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
        glUseProgram(self.shaders[1])

        glBindVertexArray(self.number_vao[0]["vao"])
        # Uniform for aspect ratio
        aspect_ratio_location = glGetUniformLocation(self.shaders[1], "aspect_ratio")
        scale_loc = glGetUniformLocation(self.shaders[1], "scale")
        glUniform1f(scale_loc, scale)
        glUniform1f(aspect_ratio_location, self.aspect_ratio)

        proj_loc = glGetUniformLocation(self.shaders[1], "projection")
        view_loc = glGetUniformLocation(self.shaders[1], "view")

        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, camera.projection_matrix)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, camera.view_matrix)

        # Uniform for color
        color_location = glGetUniformLocation(self.shaders[1], "color_in")
        glUniform3fv(color_location, 1, np.array([0.0, 0.0, 0.0], dtype=np.float32))

        # Draw instanced
        glDrawArrays(GL_POINTS, 0, self.number_vao[0]["n_instances"])

        glBindVertexArray(0)
