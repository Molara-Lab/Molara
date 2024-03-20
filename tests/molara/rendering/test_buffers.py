"""This module contains the unit tests for the buffers module of the Rendering package."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from molara.Gui.main_window import MainWindow
    from pytestqt.qtbot import QtBot

import numpy as np
from molara.Rendering.buffers import setup_vao
from molara.Rendering.sphere import Sphere, calculate_sphere_model_matrix


class WorkaroundTestBuffers:
    """This class contains the tests for the buffers module."""

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the WorkaroundTestMainWindow object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.openGLWidget = main_window.structure_widget

    def test_setup_vao(self) -> None:
        """Tests the setup_vao function of the buffers module."""
        # Define the input data for a sphere
        subdivisions = 10
        sphere_mesh = Sphere(subdivisions)
        position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        sphere_radius = 1.0
        sphere_colors = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        sphere_model_matrices = calculate_sphere_model_matrix(position, sphere_radius)

        self.openGLWidget.makeCurrent()
        (vao, buffers) = setup_vao(
            sphere_mesh.vertices,
            sphere_mesh.indices,
            sphere_model_matrices,
            sphere_colors,
        )

        assert isinstance(vao, (np.integer, int))
        assert isinstance(buffers, list)
        # len(buffers) must always be 4.
        assert len(buffers) == 4  # noqa: PLR2004
        for i in range(4):
            assert isinstance(buffers[i], (np.integer, int))
