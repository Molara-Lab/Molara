"""This module contains the tests for the rendering module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from molara.Rendering.rendering import Renderer

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow
    from pytestqt.qtbot import QtBot


# @pytest.mark.skipif(sys.platform == "win32", reason="Test is not compatible with Windows")
def _renderer(qtbot: QtBot, main_window: QMainWindow) -> None:
    """Tests the Renderer class.

    :param qtbot: provides methods to simulate user interaction
    """
    workaround_test_renderer = WorkaroundTestRenderer(qtbot, main_window)
    # workaround_test_renderer.openGLWidget.makeCurrent()

    # The order of the tests is important, as the tests are not independent.
    # Changing the order of the tests may lead to failing tests.
    workaround_test_renderer.test_init()
    workaround_test_renderer.test_set_shader()
    workaround_test_renderer.test_draw_cylinders()
    workaround_test_renderer.test_remove_cylinder()
    workaround_test_renderer.test_draw_cylinders_from_to()
    workaround_test_renderer.test_draw_spheres()

    workaround_test_renderer.openGLWidget.doneCurrent()


class WorkaroundTestRenderer:
    """This class contains the tests for the Renderer class."""

    def __init__(self, qtbot: QtBot, main_window: QMainWindow) -> None:
        """Instantiates the Renderer object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.openGLWidget = self.main_window.structure_widget  # QOpenGLWidget(None)
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

    def test_set_shader(self) -> None:
        """Tests the set_shader method of the Renderer class."""
        shader_int = 192837465
        self.renderer.set_shader(shader_int)
        assert self.renderer.shader == shader_int

    def test_draw_cylinders(self) -> None:
        """Tests the draw_cylinders method of the Renderer class."""
        self.openGLWidget.makeCurrent()
        positions = np.array([[0, 0, 0], [1, 1, 1], [4, 5, 6]], dtype=np.float32)
        directions = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
        radii = np.array([0.5, 0.3, 0.2], dtype=np.float32)
        lengths = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
        subdivisions = 10

        mostrecent_cylinder_id = -1
        cylinder_total_counter = 0

        def _test_ids_and_counters(result: int) -> None:
            """Tests most recent cylinder ids, cylinder vao entries and...?"""
            assert result == mostrecent_cylinder_id
            assert self.renderer.cylinders[mostrecent_cylinder_id]["vao"] == cylinder_total_counter
            start_id = 1 + (cylinder_total_counter - 1) * 4
            end_id = 1 + cylinder_total_counter * 4
            buffers_comparison = list(range(start_id, end_id))
            assert self.renderer.cylinders[mostrecent_cylinder_id]["buffers"] == buffers_comparison

        result = self.renderer.draw_cylinders(positions, directions, radii, lengths, colors, subdivisions)
        cylinder_total_counter += 1
        mostrecent_cylinder_id += 1
        _test_ids_and_counters(result)

        result = self.renderer.draw_cylinders(positions, directions, radii, lengths, colors, subdivisions)
        cylinder_total_counter += 1
        mostrecent_cylinder_id += 1
        _test_ids_and_counters(result)

        result = self.renderer.draw_cylinders(positions, directions, radii, lengths, colors, subdivisions)
        cylinder_total_counter += 1
        mostrecent_cylinder_id += 1
        _test_ids_and_counters(result)

        self.renderer.remove_cylinder(0)
        result = self.renderer.draw_cylinders(positions, directions, radii, lengths, colors, subdivisions)
        mostrecent_cylinder_id = 0
        cylinder_total_counter += 1

    def test_remove_cylinder(self) -> None:
        """Tests the remove_cylinder method of the Renderer class."""
        self.openGLWidget.makeCurrent()
        self.renderer.remove_cylinder(0)
        self.renderer.remove_cylinder(1)
        self.renderer.remove_cylinder(2)
        # also test removing a cylinder that does not exist. Nothing should happen.
        self.renderer.remove_cylinder(543210)

    def test_draw_cylinders_from_to(self) -> None:
        """Tests the draw_cylinders_from_to method of the Renderer class."""
        self.openGLWidget.makeCurrent()
        positions_from_to = np.array(
            [
                [[1.2, 3.4, 5.6], [9.8, 7.6, 5.4]],
                [[-3.3, -2.2, 1.1], [9.9, 8.8, -7.7]],
                [[0, 0, 0], [1, 1, 1]],
            ],
            dtype=np.float32,
        )
        positions = positions_from_to.mean(axis=1, dtype=np.float32)
        directions = positions_from_to[:, 1, :] - positions_from_to[:, 0, :]
        radii = np.array([0.5, 0.3, 0.2], dtype=np.float32)
        colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
        subdivisions = 10

        id_cylinder_from_to = self.renderer.draw_cylinders_from_to(positions_from_to, radii, colors, subdivisions)
        id_cylinder_normal = self.renderer.draw_cylinders(
            positions,
            directions,
            radii,
            np.linalg.norm(directions, axis=1),
            colors,
            subdivisions,
        )
        assert id_cylinder_from_to == 0
        assert id_cylinder_normal == 1

    def test_draw_spheres(self) -> None:
        """Tests the draw_spheres method of the Renderer class."""
        self.openGLWidget.makeCurrent()
        positions = np.array([[0, 0, 0], [1, 1, 1]], dtype=np.float32)
        radii = np.array([0.5, 0.3], dtype=np.float32)
        colors = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float32)
        subdivisions = 10

        count_sphere_instances = 0
        result = self.renderer.draw_spheres(positions, radii, colors, subdivisions)
        assert result == count_sphere_instances
        count_sphere_instances += 1
        result = self.renderer.draw_spheres(positions, radii, colors, subdivisions)
        assert result == count_sphere_instances
        count_sphere_instances += 1
        result = self.renderer.draw_spheres(positions, radii, colors, subdivisions)
        assert result == count_sphere_instances

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