"""Contains the unit tests for the spheres module of the rendering package."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    from molara.gui.main_window import MainWindow

import numpy as np

from molara.rendering.spheres import Spheres


class WorkaroundTestSpheres:
    """Contains the tests for the buffers module."""

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the WorkaroundTestMainWindow object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.openGLWidget = main_window.structure_widget

    def run_tests(self) -> None:
        """Run the tests."""
        self._test_init()

    def _test_init(self) -> None:
        """Test the initialization of the Spheres class."""
        positions = np.array([[0.0, 0.0, 0.0],
                              [1.0, -2.345, 0.12]], dtype=np.float32)
        colors = np.array([[0.0, 1.0, 0.0],
                            [1.0, 0.0, 0.0]], dtype=np.float32)
        scales = np.array([1.0, 2.0], dtype=np.float32)
        subdivisions = 20
        spheres = Spheres(subdivisions, positions, scales, colors)
        assert spheres.subdivisions == subdivisions
