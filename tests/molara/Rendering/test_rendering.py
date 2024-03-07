"""This module contains the tests for the rendering module."""
from __future__ import annotations

import unittest

from molara.Rendering.rendering import Renderer
from OpenGL.GL import (
    GLuint,
)


class TestRenderer(unittest.TestCase):
    """This class contains the tests for the Renderer class."""

    def setUp(self) -> None:
        """Instantiates the Renderer object."""
        self.renderer = Renderer()

    def test_init(self) -> None:
        """Tests the __init__ method of the Renderer class."""
        assert isinstance(self.renderer, Renderer)
        assert isinstance(self.renderer.atoms_vao, dict)
        assert isinstance(self.renderer.bonds_vao, dict)
        assert isinstance(self.renderer.spheres, list[dict])
        assert isinstance(self.renderer.cylinders, list[dict])
        assert isinstance(self.renderer.shader, GLuint)

    # def test_draw_cylinders(self) -> None:
    #     positions = np.array([[0, 0, 0], [1, 1, 1]])
    #     directions = np.array([[1, 0, 0], [0, 1, 0]])
    #     radii = np.array([0.5, 0.3])
    #     lengths = np.array([1.0, 2.0])
    #     colors = np.array([[1, 0, 0], [0, 1, 0]])
    #     subdivisions = 10

    #     result = self.renderer.draw_cylinders(positions, directions, radii, lengths, colors, subdivisions)

    #     self.assertEqual(result, 2)  # Assert that the number of cylinders drawn is correct

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
