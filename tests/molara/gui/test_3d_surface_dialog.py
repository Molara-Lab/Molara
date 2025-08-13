"""Test the CubeFileDialog class."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from unittest import mock

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    from molara.gui.main_window import MainWindow


class WorkaroundTestCubeFileDialog:
    """Contains the tests for the CubeFileDialog class.

    It does not inherit from unittest.TestCase, because that does not work with pytest-qt.
    """

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the WorkaroundTestMeasurementDialog object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        testargs = ["molara", "examples/cube/tetrabenzoporphyrin.cube"]
        with mock.patch.object(sys, "argv", testargs):
            self.main_window.show_init_xyz()

    def run_tests(self) -> None:
        """Run the tests."""
        self._test_init()
        self._test_toggle_surfaces()
        self._test_change_iso_value()
        self._test_toggle_wire_mesh()
        self._test_color()

    def _test_init(self) -> None:
        """Test the initialization of the dialog."""
        self.main_window.surface_3d_dialog.initialize_dialog()
        assert self.main_window.surface_3d_dialog.isVisible() is True

    def _test_toggle_surfaces(self) -> None:
        """Test the toggle_surfaces method."""
        self.main_window.surface_3d_dialog.toggle_surfaces()
        assert self.main_window.surface_3d_dialog.surfaces_are_visible

    def _test_change_iso_value(self) -> None:
        """Test the change_iso_value method."""
        iso = 0.123
        self.main_window.surface_3d_dialog.ui.isoSpinBox.setValue(iso)
        self.main_window.surface_3d_dialog.change_iso_value()
        assert self.main_window.surface_3d_dialog.iso_value == iso

    def _test_toggle_wire_mesh(self) -> None:
        """Test the toggle_wire_mesh method."""
        assert not self.main_window.surface_3d_dialog.draw_wire_frame
        self.main_window.surface_3d_dialog.toggle_wire_mesh()
        assert self.main_window.surface_3d_dialog.draw_wire_frame
        self.main_window.surface_3d_dialog.toggle_wire_mesh()
        assert not self.main_window.surface_3d_dialog.draw_wire_frame

    def _test_color(self) -> None:
        """Test all color methods."""
        self.main_window.surface_3d_dialog.change_color_surface_1()
        self.main_window.surface_3d_dialog.change_color_surface_2()
        self.main_window.surface_3d_dialog.update_color_buttons()
