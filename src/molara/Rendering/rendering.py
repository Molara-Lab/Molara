# mypy: disable-error-code="name-defined"
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pyrr
from OpenGL.GL import *

if TYPE_CHECKING:
    from molara.Molecule.molecule import Molecule
    from molara.Rendering.camera import Camera


def draw_scene(
    shader: GLuint, camera: Camera, vaos: list[int], molecule: Molecule | None = None,
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

    light_direction = (
        -camera.position - camera.up_vector * camera.distance_from_target * 0.5
    )
    glUniform3fv(light_direction_loc, 1, light_direction)
    glUniform3fv(camera_loc, 1, camera.position)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, camera.projection_matrix)
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_mat)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    for vao, atomic_number in zip(vaos, molecule.unique_atomic_numbers):
        idx = molecule.drawer.unique_spheres_mapping[atomic_number]
        glBindVertexArray(vao)
        glDrawElementsInstanced(
            GL_TRIANGLES,
            len(molecule.drawer.unique_spheres[idx].vertices),
            GL_UNSIGNED_INT,
            None,
            len(molecule.drawer.unique_spheres[idx].model_matrices),
        )
        glBindVertexArray(0)
    for vao, atomic_number in zip(
        vaos[len(molecule.unique_atomic_numbers) :], molecule.unique_atomic_numbers,
    ):
        idx = molecule.drawer.unique_cylinders_mapping[atomic_number]
        if molecule.drawer.unique_cylinders[idx].model_matrices is not None:
            glBindVertexArray(vao)
            glDrawElementsInstanced(
                GL_TRIANGLES,
                len(molecule.drawer.unique_cylinders[idx].vertices),
                GL_UNSIGNED_INT,
                None,
                len(molecule.drawer.unique_cylinders[idx].model_matrices),
            )
            glBindVertexArray(0)
