"""Test the MOsDialog class."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from unittest import mock

import numpy as np

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    from molara.gui.main_window import MainWindow


class WorkaroundTestMOsDialog:
    """Contains the tests for the MeasurementDialog class.

    It does not inherit from unittest.TestCase, because that does not work with pytest-qt.
    """

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the WorkaroundTestMeasurementDialog object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        testargs = ["molara", "examples/molden/o2.molden"]
        with mock.patch.object(sys, "argv", testargs):
            self.main_window.show_init_xyz()
        # only for the given o2 molecule!
        self.box_size = np.array([2.0, 2.0, 3.15844643])
        self.box_origin = np.array([-1.0, -1.0, -1.57922321])
        self.corners = np.array(
            [
                [-1.0, -1.0, -1.57922321],
                [1.0, -1.0, -1.57922321],
                [-1.0, 1.0, -1.57922321],
                [1.0, 1.0, -1.57922321],
                [-1.0, -1.0, 1.57922321],
                [1.0, -1.0, 1.57922321],
                [-1.0, 1.0, 1.57922321],
                [1.0, 1.0, 1.57922321],
            ],
        )

        self.main_window.show_mo_dialog()
        self.mo_dialog = self.main_window.mo_dialog

    def run_tests(self) -> None:
        """Run the tests."""
        # unrestricted case
        self._test_spin_selection()
        self._test_select_a_different_orbital()
        self._test_wire_mesh()
        self._test_box()
        self._test_visualization()
        self._test_population()

        self._test_close()

        # restricted case
        self._test_restricted_case()

    def _test_restricted_case(self) -> None:
        """Test the restricted case."""
        testargs = ["molara", "examples/molden/h2o.molden"]
        with mock.patch.object(sys, "argv", testargs):
            self.main_window.show_init_xyz()
        self.main_window.show_mo_dialog()
        self.mo_dialog = self.main_window.mo_dialog
        number_of_orbitals_for_h2o = 43
        assert self.mo_dialog.number_of_orbitals == number_of_orbitals_for_h2o

    def _test_spin_selection(self) -> None:
        """Test the spin selection checkboxes."""
        self.mo_dialog.select_spin_alpha()
        assert self.mo_dialog.display_spin == 1
        self.mo_dialog.select_spin_beta()
        assert self.mo_dialog.display_spin == -1
        assert (
            self.mo_dialog.number_of_alpha_orbitals + self.mo_dialog.number_of_beta_orbitals
            == self.mo_dialog.number_of_orbitals
        )

    def _test_select_a_different_orbital(self) -> None:
        """Test the selection of a different orbital."""
        self.mo_dialog.ui.orbitalSelector.setCurrentCell(3, 0)
        self.mo_dialog.select_row()
        selected_orbital = 65
        old_orbital = 3
        assert self.mo_dialog.selected_orbital == selected_orbital
        assert self.mo_dialog.old_orbital == old_orbital

    def _test_wire_mesh(self) -> None:
        """Test the wire mesh toggle button."""
        assert not self.mo_dialog.parent().structure_widget.renderer.wire_mesh_orbitals
        self.mo_dialog.toggle_wire_mesh()
        assert self.mo_dialog.parent().structure_widget.renderer.wire_mesh_orbitals
        self.mo_dialog.toggle_wire_mesh()

    def _test_box(self) -> None:
        """Test the scale box size method and the corner calculation."""
        size = 2

        corners = self.mo_dialog.calculate_corners_of_cube()

        assert not self.mo_dialog.display_box
        self.mo_dialog.toggle_box()
        assert self.mo_dialog.display_box
        self.mo_dialog.toggle_box()

        assert self.mo_dialog.size.all() == self.box_size.all()
        assert self.mo_dialog.origin.all() == self.box_origin.all()
        assert corners.all() == self.corners.all()
        self.mo_dialog.ui.cubeBoxSizeSpinBox.setValue(size)
        self.mo_dialog.scale_box()
        new_size = np.array([size, size, size]) + self.box_size
        new_origin = self.box_size - np.array([size, size, size]) / 2
        assert self.mo_dialog.size.all() == new_size.all()
        assert self.mo_dialog.origin.all() == new_origin.all()

    def _test_visualization(self) -> None:
        """Test the visualization of the orbitals not their correctness."""
        self.mo_dialog.visualize_orbital()
        number_of_vertices = 768
        assert self.mo_dialog.parent().structure_widget.renderer.polygons[0]["n_vertices"] == number_of_vertices
        self.mo_dialog.remove_orbitals()
        assert self.mo_dialog.parent().structure_widget.renderer.polygons[0]["vao"] == 0

    def _test_population(self) -> None:
        """Test the populationanalysis."""
        self.mo_dialog.run_population_analysis()
        assert self.mo_dialog.ui.exactCountLabel.text() == "16.0"
        assert self.mo_dialog.ui.calculatedCountLabel.text() == "16.00000003"

    def _test_close(self) -> None:
        """Close the widget again."""
        self.mo_dialog.close()
