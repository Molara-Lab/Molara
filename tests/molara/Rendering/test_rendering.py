"""This module contains the tests for the rendering module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from molara.Rendering.rendering import Renderer
from PySide6.QtOpenGLWidgets import QOpenGLWidget

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


def test_renderer(qtbot: QtBot) -> None:
    """Tests the Renderer class."""
    workaround_test_renderer = WorkaroundTestRenderer(qtbot)
    workaround_test_renderer.test_init()
    workaround_test_renderer.test_draw_cylinders()


class WorkaroundTestRenderer:
    """This class contains the tests for the Renderer class."""

    def __init__(self, qtbot: QtBot) -> None:
        """Instantiates the Renderer object."""
        self.qtbot = qtbot
        self.openGLWidget = QOpenGLWidget(None)
        self.renderer = Renderer()
        self.openGLWidget.show()

    def test_init(self) -> None:
        """Tests the __init__ method of the Renderer class."""
        assert isinstance(self.renderer, Renderer)
        assert isinstance(self.renderer.atoms_vao, dict)
        assert isinstance(self.renderer.bonds_vao, dict)
        assert isinstance(self.renderer.spheres, list)
        assert isinstance(self.renderer.cylinders, list)
        assert self.renderer.shader == 0

    def test_draw_cylinders(self) -> None:
        """Tests the draw_cylinders method of the Renderer class."""
        positions = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.float32)
        directions = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float32)
        radii = np.array([0.5, 0.3], dtype=np.float32)
        lengths = np.array([1.0, 2.0], dtype=np.float32)
        colors = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float32)
        subdivisions = 10

        self.openGLWidget.makeCurrent()
        count_cylinder_instances = 0
        result = self.renderer.draw_cylinders(positions, directions, radii, lengths, colors, subdivisions)
        assert result == count_cylinder_instances
        count_cylinder_instances += 1
        result = self.renderer.draw_cylinders(positions, directions, radii, lengths, colors, subdivisions)
        assert result == count_cylinder_instances
        count_cylinder_instances += 1
        result = self.renderer.draw_cylinders(positions, directions, radii, lengths, colors, subdivisions)
        assert result == count_cylinder_instances
        self.openGLWidget.doneCurrent()

    # def test_draw_spheres(self):
    #     positions = np.array([[0, 0, 0], [1, 1, 1]])
    #     radii = np.array([0.5, 0.3])
    #     colors = np.array([[1, 0, 0], [0, 1, 0]])
    #     subdivisions = 10

    #     result = self.renderer.draw_spheres(positions, radii, colors, subdivisions)

    #     self.assertEqual(result, 2)  # Assert that the number of spheres drawn is correct

    # def test_remove_cylinder(self):
    #     i_cylinder = 0

    #     self.renderer.remove_cylinder(i_cylinder)

    #     # Assert that the cylinder has been removed successfully
    #     # You can add additional assertions here if needed

    # def test_remove_sphere(self):
    #     i_sphere = 0

    #     self.renderer.remove_sphere(i_sphere)

    #     # Assert that the sphere has been removed successfully
    #     # You can add additional assertions here if needed

    # def test_update_atoms_vao(self):
    #     vertices = np.array([[0, 0, 0], [1, 1, 1]])
    #     indices = np.array([0, 1])
    #     model_matrices = np.array([np.eye(4), np.eye(4)])
    #     colors = np.array([[1, 0, 0], [0, 1, 0]])

    #     self.renderer.update_atoms_vao(vertices, indices, model_matrices, colors)

    #     # Assert that the atoms VAO has been updated successfully
    #     # You can add additional assertions here if needed

    # def test_update_bonds_vao(self):
    #     vertices = np.array([[0, 0, 0], [1, 1, 1]])
    #     indices = np.array([0, 1])
    #     model_matrices = np.array([np.eye(4), np.eye(4)])
    #     colors = np.array([[1, 0, 0], [0, 1, 0]])

    #     self.renderer.update_bonds_vao(vertices, indices, model_matrices, colors)

    #     # Assert that the bonds VAO has been updated successfully
    #     # You can add additional assertions here if needed

    # def test_draw_scene(self):
    #     # Create a mock camera object and set the bonds flag to True
    #     class MockCamera:
    #         pass

    #     camera = MockCamera()
    #     camera.bonds = True

    #     self.renderer.draw_scene(camera)

    #     # Assert that the scene has been drawn successfully
    #     # You can add additional assertions here if needed
