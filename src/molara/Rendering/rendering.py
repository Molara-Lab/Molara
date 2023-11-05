"""Contains the rendering function for the opengl widget."""

# mypy: disable-error-code="name-defined"
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pyrr
from OpenGL.GL import *

from molara.Rendering.buffers import setup_vao
from molara.Rendering.sphere import Sphere

if TYPE_CHECKING:
    import numpy as np

    from molara.Molecule.molecule import Molecule
    from molara.Rendering.camera import Camera

atoms_vao: dict = {"vao": 0, "n_atoms": 0, "n_vertices": 0, "buffers": []}
bonds_vao: dict = {"vao": 0, "n_bonds": 0, "n_vertices": 0, "buffers": []}


def update_atoms_vao(
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
    if atoms_vao["vao"] == 0:
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        for buffer in atoms_vao["buffers"]:
            glDeleteBuffers(1, buffer)
        glDeleteVertexArrays(1, atoms_vao["vao"])
    atoms_vao["vao"], atoms_vao["buffers"] = setup_vao(
        vertices,
        indices,
        model_matrices,
        colors,
    )
    atoms_vao["n_atoms"] = len(model_matrices)
    atoms_vao["n_vertices"] = len(vertices)


def update_bonds_vao(
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
    if bonds_vao["vao"] == 0:
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        for buffer in bonds_vao["buffers"]:
            glDeleteBuffers(1, buffer)
        glDeleteVertexArrays(1, bonds_vao["vao"])
    bonds_vao["vao"], bonds_vao["buffers"] = setup_vao(
        vertices,
        indices,
        model_matrices,
        colors,
    )
    bonds_vao["n_bonds"] = len(model_matrices)
    bonds_vao["n_vertices"] = len(vertices)


def draw_scene(
    shader: GLuint,
    camera: Camera,
    molecule: Molecule | None = None,
) -> None:
    """Draws the contents of the given vaos from the given camera perspective.

    :param shader: The shader program of the opengl widget.
    :type shader: pyopengl program
    :param camera: The camera object to capture the scene.
    :type camera: Camera
    :param vaos: The vertex array object pointers for the opengl draw call.
    :type vaos: GL_INT
    :param molecule: The molecule that is currently loaded.
    :type molecule: Molecule
    """
    if molecule is None:
        return
    view_mat = pyrr.matrix44.create_look_at(
        pyrr.Vector3(camera.position),
        pyrr.Vector3(camera.target),
        pyrr.Vector3(camera.up_vector),
    )

    light_direction_loc = glGetUniformLocation(shader, "light_direction")
    proj_loc = glGetUniformLocation(shader, "projection")
    camera_loc = glGetUniformLocation(shader, "camera_position")
    view_loc = glGetUniformLocation(shader, "view")

    light_direction = -camera.position - camera.up_vector * camera.distance_from_target * 0.5
    glUniform3fv(light_direction_loc, 1, light_direction)
    glUniform3fv(camera_loc, 1, camera.position)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, camera.projection_matrix)
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_mat)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glBindVertexArray(atoms_vao["vao"])
    glDrawElementsInstanced(
        GL_TRIANGLES,
        atoms_vao["n_vertices"],
        GL_UNSIGNED_INT,
        None,
        atoms_vao["n_atoms"],
    )
    glBindVertexArray(bonds_vao["vao"])
    glDrawElementsInstanced(
        GL_TRIANGLES,
        bonds_vao["n_vertices"],
        GL_UNSIGNED_INT,
        None,
        bonds_vao["n_bonds"],
    )
    glBindVertexArray(0)
    # for vao, atomic_number in zip(vaos, molecule.unique_atomic_numbers):
    #     idx = molecule.drawer.unique_spheres_mapping[atomic_number]
    #     glBindVertexArray(vao)
    #     glDrawElementsInstanced(
    #         GL_TRIANGLES,
    #         len(molecule.drawer.unique_spheres[idx].vertices),
    #         GL_UNSIGNED_INT,
    #         None,
    #         len(molecule.drawer.unique_spheres[idx].model_matrices),
    #     )
    #     glBindVertexArray(0)
    # for vao, atomic_number in zip(
    #     vaos[len(molecule.unique_atomic_numbers) :],
    #     molecule.unique_atomic_numbers,
    # ):
    #     idx = molecule.drawer.unique_cylinders_mapping[atomic_number]
    #     if molecule.drawer.unique_cylinders[idx].model_matrices is not None:
    #         glBindVertexArray(vao)
    #         if molecule.draw_bonds:
    #             glDrawElementsInstanced(
    #                 GL_TRIANGLES,
    #                 len(molecule.drawer.unique_cylinders[idx].vertices),
    #                 GL_UNSIGNED_INT,
    #                 None,
    #                 len(molecule.drawer.unique_cylinders[idx].model_matrices),
    #             )
    #         glBindVertexArray(0)
