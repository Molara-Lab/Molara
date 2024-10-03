"""Test the BuilderDialog class."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from unittest import mock

import numpy as np
from numpy.testing import assert_array_equal
from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QMouseEvent

from molara.gui.structure_widget import BUILDER, MEASUREMENT
from molara.structure.crystal import Crystal
from molara.structure.crystals import Crystals
from molara.util.testing import assert_vectors_equal

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    from molara.gui.main_window import MainWindow


class WorkaroundTestStructureWidget:
    """Contains the tests for the StructureWidget class.

    It does not inherit from unittest.TestCase, because that does not work with pytest-qt.
    """

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the WorkaroundTestBuilderDialog object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.structure_widget = main_window.structure_widget

    def run_tests(self) -> None:
        """Run the tests."""
        self.test_load_molecule_toggle_bonds()
        self.test_mouse_move()
        self.test_toggle_axes()
        self.test_toggle_unit_cell_boundaries()
        self.test_select_atoms()
        self.test_set_view_to_axes()

    def test_toggle_unit_cell_boundaries(self) -> None:
        """Test the toggle_unit_cell_boundaries method."""
        window = self.main_window
        structure_widget = window.structure_widget
        window.load_molecules("examples/POSCAR/Ba2YCu3O7_POSCAR")
        assert isinstance(window.mols, Crystals)
        assert isinstance(structure_widget.structures[0], Crystal)
        assert structure_widget.structures[0] is window.mols.get_current_mol()

        structure_widget.toggle_unit_cell_boundaries()
        text_unit_cell_boundaries = "Hide Unit Cell Boundaries"
        assert structure_widget.draw_unit_cell_boundaries

        assert (
            window.ui.actionToggle_UnitCellBoundaries.text()
            == text_unit_cell_boundaries
        )

        structure_widget.toggle_unit_cell_boundaries()
        assert not structure_widget.draw_unit_cell_boundaries
        text_unit_cell_boundaries = "Show Unit Cell Boundaries"
        assert (
            window.ui.actionToggle_UnitCellBoundaries.text()
            == text_unit_cell_boundaries
        )

    def test_load_molecule_toggle_bonds(self) -> None:
        """Test the load_molecule and toggle_bonds methods."""
        structure_widget = self.main_window.structure_widget
        testargs = ["molara", "examples/xyz/pentane.xyz"]
        with mock.patch.object(sys, "argv", testargs):
            self.main_window.show_init_xyz()
        assert structure_widget.draw_bonds
        assert structure_widget.bonds
        self.main_window.structure_customizer_dialog.toggle_bonds()
        assert not structure_widget.bonds
        assert not structure_widget.draw_bonds

    def test_mouse_move(self) -> None:
        """Test the mouse_move method."""
        structure_widget = self.main_window.structure_widget
        # Test mouse moves and clicks
        self.qtbot.mousePress(structure_widget, Qt.LeftButton, pos=QPoint(50, 50))

        # Simulate mouse move events to rotate the structure
        self.qtbot.mouseMove(structure_widget, QPoint(60, 60))
        self.qtbot.mouseMove(structure_widget, QPoint(70, 70))

        # Simulate a left mouse button release event to end rotation
        self.qtbot.mouseRelease(structure_widget, Qt.LeftButton, pos=QPoint(70, 70))

        self.qtbot.mousePress(structure_widget, Qt.RightButton, pos=QPoint(50, 50))

        # Simulate mouse move events to rotate the structure
        self.qtbot.mouseMove(structure_widget, QPoint(60, 60))
        self.qtbot.mouseMove(structure_widget, QPoint(70, 70))

        # Simulate a left mouse button release event to end rotation
        self.qtbot.mouseRelease(structure_widget, Qt.RightButton, pos=QPoint(70, 70))

    def test_toggle_axes(self) -> None:
        """Test toggle axes."""
        structure_widget = self.main_window.structure_widget
        structure_widget.toggle_axes()
        assert structure_widget.draw_axes
        structure_widget.toggle_axes()
        assert not structure_widget.draw_axes

    def test_select_atoms(self) -> None:
        """Test the select_atoms method."""
        structure_widget = self.main_window.structure_widget
        # Test measurement select sphere
        event = QMouseEvent(
            QEvent.MouseButtonPress,  # Event type
            QPoint(50, 50),  # Position
            QPoint(0, 0),  # Global (screen) position
            Qt.LeftButton,  # Button
            Qt.LeftButton,  # Buttons (pressed buttons)
            Qt.NoModifier,  # Modifiers (keyboard modifiers)
        )
        # Comment on the constructor of QMouseEvent:
        # The global position is necessary to avoid the use of a deprecated method.
        # The global position is not used in the test, so it is set to (0, 0).
        # Should this cause problems in the future, we need to
        # figure out how to set the global position correctly.
        structure_widget.update_selected_atoms(MEASUREMENT, event)

        measurement_selected_spheres = structure_widget.measurement_selected_spheres
        structure_widget.unselect_all_atoms()
        for sphere_id in measurement_selected_spheres:
            assert sphere_id == -1
        id1, id2, id3, id4 = 2, 1, 0, 3
        structure_widget.exec_select_sphere(id1, measurement_selected_spheres)
        assert measurement_selected_spheres[0] == id1
        assert_vectors_equal(
            structure_widget.structures[0].drawer.atom_colors[id1],
            structure_widget.new_sphere_colors[0],
        )
        structure_widget.exec_select_sphere(id2, measurement_selected_spheres)
        assert measurement_selected_spheres[1] == id2
        assert_vectors_equal(
            structure_widget.structures[0].drawer.atom_colors[id2],
            structure_widget.new_sphere_colors[1],
        )
        structure_widget.exec_select_sphere(id3, measurement_selected_spheres)
        assert measurement_selected_spheres[2] == id3
        assert_vectors_equal(
            structure_widget.structures[0].drawer.atom_colors[id3],
            structure_widget.new_sphere_colors[2],
        )
        structure_widget.exec_select_sphere(id4, measurement_selected_spheres)
        assert measurement_selected_spheres[3] == id4
        assert_vectors_equal(
            structure_widget.structures[0].drawer.atom_colors[id4],
            structure_widget.new_sphere_colors[3],
        )

        assert_array_equal(measurement_selected_spheres, [id1, id2, id3, id4])
        structure_widget.exec_unselect_sphere(-1, measurement_selected_spheres)
        assert_array_equal(measurement_selected_spheres, [id1, id2, id3, id4])
        structure_widget.exec_unselect_sphere(id2, measurement_selected_spheres)
        assert_array_equal(measurement_selected_spheres, [id1, -1, id3, id4])
        structure_widget.exec_unselect_sphere(id1, measurement_selected_spheres)
        assert_array_equal(measurement_selected_spheres, [-1, -1, id3, id4])
        structure_widget.exec_unselect_sphere(id3, measurement_selected_spheres)
        assert_array_equal(measurement_selected_spheres, [-1, -1, -1, id4])
        structure_widget.exec_unselect_sphere(id4, measurement_selected_spheres)
        assert_array_equal(measurement_selected_spheres, [-1, -1, -1, -1])

        # Test builder select sphere
        structure_widget.update_selected_atoms(BUILDER, event)

    def test_set_view_to_axes(self) -> None:
        """Test setting the rotation of the camera. See also test_set_rotation in test_camera.py."""
        structure_widget = self.main_window.structure_widget
        camera = structure_widget.camera
        quaternion_x = [0.0, 0.0, 0.0, 1.0]
        quaternion_y = [0.0, 0.0, np.sqrt(2) / 2, np.sqrt(2) / 2]
        quaternion_z = [0.0, np.sqrt(2) / 2, 0.0, np.sqrt(2) / 2]
        # quaternion_y = [0.0, 0.0, 0.7071067690849304, 0.7071067690849304]
        # quaternion_z = [0.0, 0.7071067690849304, 0.0, 0.7071067690849304]
        structure_widget.set_view_to_axis("x")
        assert_vectors_equal(camera.rotation.tolist(), quaternion_x)
        structure_widget.set_view_to_axis("y")
        assert_vectors_equal(camera.rotation.tolist(), quaternion_y)
        structure_widget.set_view_to_axis("z")
        assert_vectors_equal(camera.rotation.tolist(), quaternion_z)
