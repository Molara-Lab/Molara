"""This module contains the tests for the rendering module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from molara.Rendering.rendering import Renderer

if TYPE_CHECKING:
    from molara.Gui.main_window import MainWindow
    from pytestqt.qtbot import QtBot


class WorkaroundTestRenderer:
    """This class contains the tests for the Renderer class."""

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiates the Renderer object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.openGLWidget = self.main_window.structure_widget
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
        # for the first added cylinder, cylinder_total_counter must be set to the vao id of the first cylinder.
        # this is because previous tests might have added cylinders already.
        # after this, every added cylinder should increase the cylinder_total_counter by 1.
        cylinder_total_counter = self.renderer.cylinders[mostrecent_cylinder_id]["vao"]
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

        def _remove_tests(cylinder_id: int) -> None:
            """Tests the removal of a cylinder."""
            self.renderer.remove_cylinder(cylinder_id)
            if cylinder_id >= len(self.renderer.cylinders):
                return
            assert self.renderer.cylinders[cylinder_id]["vao"] == 0
            assert self.renderer.cylinders[cylinder_id]["n_instances"] == 0
            assert self.renderer.cylinders[cylinder_id]["n_vertices"] == 0
            assert self.renderer.cylinders[cylinder_id]["buffers"] == []

        _remove_tests(0)
        _remove_tests(1)
        _remove_tests(2)
        # also test removing a cylinder that does not exist. Nothing should happen.
        _remove_tests(543210)

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

        mostrecent_sphere_id = -1
        sphere_total_counter = 0

        def _test_ids_and_counters(result: int) -> None:
            """Tests most recent sphere ids, sphere vao entries and...?"""
            assert result == mostrecent_sphere_id
            assert self.renderer.spheres[mostrecent_sphere_id]["vao"] == sphere_total_counter
            start_id = 1 + (sphere_total_counter - 1) * 4
            end_id = 1 + sphere_total_counter * 4
            buffers_comparison = list(range(start_id, end_id))
            assert self.renderer.spheres[mostrecent_sphere_id]["buffers"] == buffers_comparison

        result = self.renderer.draw_spheres(positions, radii, colors, subdivisions)
        mostrecent_sphere_id += 1
        # for the first added sphere, sphere_total_counter must be set to the vao id of the first sphere.
        # this is because previous tests might have added spheres already.
        # after this, every added sphere should increase the sphere_total_counter by 1.
        sphere_total_counter = self.renderer.spheres[mostrecent_sphere_id]["vao"]
        _test_ids_and_counters(result)

        result = self.renderer.draw_spheres(positions, radii, colors, subdivisions)
        mostrecent_sphere_id += 1
        sphere_total_counter += 1
        _test_ids_and_counters(result)

        result = self.renderer.draw_spheres(positions, radii, colors, subdivisions)
        mostrecent_sphere_id += 1
        sphere_total_counter += 1
        _test_ids_and_counters(result)

    def test_remove_sphere(self) -> None:
        """Tests the remove_sphere method of the Renderer class."""
        self.openGLWidget.makeCurrent()

        def _remove_tests(sphere_id: int) -> None:
            """Tests the removal of a sphere."""
            self.renderer.remove_sphere(sphere_id)
            if sphere_id >= len(self.renderer.spheres):
                return
            assert self.renderer.spheres[sphere_id]["vao"] == 0
            assert self.renderer.spheres[sphere_id]["n_instances"] == 0
            assert self.renderer.spheres[sphere_id]["n_vertices"] == 0
            assert self.renderer.spheres[sphere_id]["buffers"] == []

        _remove_tests(0)
        _remove_tests(1)
        _remove_tests(2)
        # also test removing a sphere that does not exist. Nothing should happen.
        _remove_tests(543210)

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
