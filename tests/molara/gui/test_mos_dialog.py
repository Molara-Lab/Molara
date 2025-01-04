"""Test the MOsDialog class."""

from __future__ import annotations

import contextlib
import sys
from typing import TYPE_CHECKING
from unittest import mock

import numpy as np

from molara.structure.molecularorbitals import MolecularOrbitals

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    from molara.gui.main_window import MainWindow


class WorkaroundTestMOsDialog:
    """Contains the tests for the MOsDialog class.

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
        self._test_box()
        self._test_visualization()
        self._test_wire_mesh()
        self._test_mo_initialization()
        self._test_change_iso_value()
        self._test_colors()

        self._test_close()

        # restricted case
        self._test_restricted_case()
        self._test_recalculate_orbital()

        # test isolines
        self._test_isoline_border_drawing()
        self._test_change_isoline_resolution()
        self._test_toggle_isolines()
        self._test_draw_isoline_border_axes()
        self._test_update_selected_atoms()
        self._test_isoline_transformation()
        self._test_reset_plane()

    def _test_mo_initialization(self) -> None:
        """Test the initialization of the Molecularorbital class."""
        mos_test = MolecularOrbitals(None, None, None, None, self.mo_dialog.aos)
        mos_test.construct_transformation_matrices()
        with contextlib.suppress(ValueError):
            mos_test.set_mo_coefficients(np.array([1, 2, 3]), spherical_order="not_working")

        with contextlib.suppress(ValueError):
            mos_test.spherical_to_cartesian_transformation(np.array([1, 2, 3]))

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
        self.mo_dialog.toggle_surfaces()
        assert not self.mo_dialog.parent().structure_widget.renderer.objects3d["Surface_1"].wire_frame
        self.mo_dialog.toggle_wire_mesh()
        assert self.mo_dialog.parent().structure_widget.renderer.objects3d["Surface_1"].wire_frame
        self.mo_dialog.toggle_wire_mesh()
        self.mo_dialog.toggle_surfaces()

    def _test_box(self) -> None:
        """Test the scale box size method and the corner calculation."""
        size = 2

        corners = self.mo_dialog.calculate_corners_of_box()

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
        self.mo_dialog.toggle_surfaces()
        number_of_vertices = 768
        assert (
            self.mo_dialog.parent().structure_widget.renderer.objects3d["Surface_1"].number_of_vertices
            == number_of_vertices
        )
        self.mo_dialog.remove_surfaces()
        assert "Surface_1" not in self.mo_dialog.parent().structure_widget.renderer.objects3d
        self.mo_dialog.toggle_surfaces()

    def _test_close(self) -> None:
        """Close the widget again."""
        self.mo_dialog.close()

    def _test_change_iso_value(self) -> None:
        """Test the change of the iso value."""
        iso1 = 0.123
        self.mo_dialog.ui.isoValueSpinBox.setValue(iso1)
        self.mo_dialog.change_iso_value()
        assert self.mo_dialog.iso_value == iso1
        iso1 /= 10
        self.mo_dialog.ui.isoValueSpinBox.setValue(iso1)
        self.mo_dialog.change_iso_value()
        assert self.mo_dialog.iso_value == iso1

    def _test_colors(self) -> None:
        """Test the color selection."""
        self.mo_dialog.change_color_surface_1()
        self.mo_dialog.change_color_surface_2()

    def _test_recalculate_orbital(self) -> None:
        """Test the recalculation of the orbital."""
        self.mo_dialog.ui.orbitalSelector.setCurrentCell(5, 0)
        self.mo_dialog.select_row()
        assert self.mo_dialog.voxel_grid_parameters_changed
        self.mo_dialog.recalculate_orbital()
        assert not self.mo_dialog.voxel_grid_parameters_changed

    def _test_isoline_border_drawing(self) -> None:
        """Test the drawing of the isoline border."""
        assert not self.mo_dialog.isoline_border_is_visible
        assert self.mo_dialog.ui.displayIsolineBorderButton.text() == "Display Border"
        self.mo_dialog.toggle_isoline_border()
        assert self.mo_dialog.isoline_border_is_visible
        assert self.mo_dialog.ui.displayIsolineBorderButton.text() == "Hide Border"
        assert "Isoline_Border_Cylinders" in self.mo_dialog.parent().structure_widget.renderer.objects3d
        assert "Isoline_Border_Spheres" in self.mo_dialog.parent().structure_widget.renderer.objects3d
        self.mo_dialog.toggle_isoline_border()
        assert not self.mo_dialog.isoline_border_is_visible
        assert self.mo_dialog.ui.displayIsolineBorderButton.text() == "Display Border"
        assert "Isoline_Border_Cylinders" not in self.mo_dialog.parent().structure_widget.renderer.objects3d
        assert "Isoline_Border_Spheres" not in self.mo_dialog.parent().structure_widget.renderer.objects3d

    def _test_change_isoline_resolution(self) -> None:
        """Test changing the isoline resolution."""
        self.mo_dialog.ui.isolineResolutionSpinBox.setValue(0.51)
        self.mo_dialog.change_isoline_resolution()
        assert self.mo_dialog.isoline_grid_parameters_changed

    def _test_toggle_isolines(self) -> None:
        """Enable and disable isolines."""
        assert not self.mo_dialog.isolines_are_visible
        assert self.mo_dialog.ui.displayIsolinesButton.text() == "Display Isolines"
        self.mo_dialog.toggle_isolines()
        assert self.mo_dialog.isolines_are_visible
        assert self.mo_dialog.ui.displayIsolinesButton.text() == "Hide Isolines"
        self.mo_dialog.toggle_isolines()
        assert not self.mo_dialog.isolines_are_visible
        assert self.mo_dialog.ui.displayIsolinesButton.text() == "Display Isolines"

    def _test_draw_isoline_border_axes(self) -> None:
        """Draw isoline border axes."""
        assert not self.mo_dialog.isoline_axes_visible
        assert self.mo_dialog.ui.displayAxesButton.text() == "Display Axes"
        self.mo_dialog.toggle_isoline_axes()
        assert not self.mo_dialog.isoline_axes_visible
        assert self.mo_dialog.ui.displayAxesButton.text() == "Display Axes"
        self.mo_dialog.toggle_isoline_border()
        self.mo_dialog.toggle_isoline_axes()
        assert self.mo_dialog.isoline_axes_visible
        assert self.mo_dialog.ui.displayAxesButton.text() == "Hide Axes"
        self.mo_dialog.toggle_isoline_axes()
        assert not self.mo_dialog.isoline_axes_visible
        assert self.mo_dialog.ui.displayAxesButton.text() == "Display Axes"
        assert "Isoline_Axes_Cylinders" not in self.mo_dialog.parent().structure_widget.renderer.objects3d
        assert "Isoline_Axes_Spheres" not in self.mo_dialog.parent().structure_widget.renderer.objects3d

    def _test_update_selected_atoms(self) -> None:
        """Test the update_selected_atoms method."""
        self.mo_dialog.update_selected_atoms()
        self.mo_dialog.ui.isoTab.setCurrentIndex(1)
        self.mo_dialog.update_selected_atoms()

    def _test_isoline_transformation(self) -> None:  # noqa: PLR0915
        """Test the isoline transformation."""
        scale = 1
        rot = 2
        trans = 3

        max_rot = 180
        max_trans = 100
        max_scale = 100
        min_scale = 0.1
        min_trans = -100

        red_rot = 11
        green_rot = -1.2
        blue_rot = 130

        # scaling
        self.mo_dialog.ui.isoTab.setCurrentIndex(1)
        assert self.mo_dialog.isoline_border_rot_trans_scale_group.checkedId() == scale
        self.mo_dialog.ui.redSpinBox.setValue(1.1)
        self.mo_dialog.ui.greenSpinBox.setValue(1.2)
        self.mo_dialog.change_isoline_border_transformation()
        assert self.mo_dialog.ui.redSpinBox.maximum() == max_scale
        assert self.mo_dialog.ui.redSpinBox.minimum() == min_scale
        assert self.mo_dialog.ui.greenSpinBox.maximum() == max_scale
        assert self.mo_dialog.ui.greenSpinBox.minimum() == min_scale
        assert not self.mo_dialog.ui.blueSpinBox.isEnabled()
        self.mo_dialog.transform_isoline_border_red()
        self.mo_dialog.transform_isoline_border_green()

        # rotating
        self.mo_dialog.ui.rotateCheckBox.setChecked(True)
        assert self.mo_dialog.isoline_border_rot_trans_scale_group.checkedId() == rot
        self.mo_dialog.change_isoline_border_transformation()
        assert self.mo_dialog.ui.redSpinBox.value() == 0.0
        assert self.mo_dialog.ui.greenSpinBox.value() == 0.0
        assert self.mo_dialog.ui.blueSpinBox.value() == 0.0
        self.mo_dialog.ui.redSpinBox.setValue(red_rot)
        self.mo_dialog.ui.greenSpinBox.setValue(green_rot)
        self.mo_dialog.ui.blueSpinBox.setValue(blue_rot)
        self.mo_dialog.change_isoline_border_transformation()
        assert self.mo_dialog.ui.redSpinBox.maximum() == max_rot
        assert self.mo_dialog.ui.redSpinBox.minimum() == -max_rot
        assert self.mo_dialog.ui.greenSpinBox.maximum() == max_rot
        assert self.mo_dialog.ui.greenSpinBox.minimum() == -max_rot
        assert self.mo_dialog.ui.blueSpinBox.maximum() == max_rot
        assert self.mo_dialog.ui.blueSpinBox.minimum() == -max_rot
        self.mo_dialog.transform_isoline_border_green()
        self.mo_dialog.transform_isoline_border_red()
        self.mo_dialog.transform_isoline_border_blue()

        # translating
        self.mo_dialog.ui.translateCheckBox.setChecked(True)
        assert self.mo_dialog.isoline_border_rot_trans_scale_group.checkedId() == trans
        self.mo_dialog.change_isoline_border_transformation()
        assert self.mo_dialog.ui.redSpinBox.value() == 0.0
        assert self.mo_dialog.ui.greenSpinBox.value() == 0.0
        assert self.mo_dialog.ui.blueSpinBox.value() == 0.0
        self.mo_dialog.ui.redSpinBox.setValue(0.5)
        self.mo_dialog.ui.greenSpinBox.setValue(-1.2)
        self.mo_dialog.ui.blueSpinBox.setValue(0.3)
        self.mo_dialog.change_isoline_border_transformation()
        assert self.mo_dialog.ui.redSpinBox.maximum() == max_trans
        assert self.mo_dialog.ui.redSpinBox.minimum() == min_trans
        assert self.mo_dialog.ui.greenSpinBox.maximum() == max_trans
        assert self.mo_dialog.ui.greenSpinBox.minimum() == min_trans
        assert self.mo_dialog.ui.blueSpinBox.maximum() == max_trans
        assert self.mo_dialog.ui.blueSpinBox.minimum() == min_trans
        self.mo_dialog.transform_isoline_border_green()
        self.mo_dialog.transform_isoline_border_red()
        self.mo_dialog.transform_isoline_border_blue()

        # check if old values were saved
        self.mo_dialog.ui.rotateCheckBox.setChecked(True)
        assert self.mo_dialog.isoline_border_rot_trans_scale_group.checkedId() == rot
        self.mo_dialog.change_isoline_border_transformation()
        assert self.mo_dialog.ui.redSpinBox.value() == red_rot
        assert self.mo_dialog.ui.greenSpinBox.value() == green_rot
        assert self.mo_dialog.ui.blueSpinBox.value() == blue_rot

    def _test_reset_plane(self) -> None:
        """Test the reset plane method."""
        self.mo_dialog.ui.xAxisCheckBox.setChecked(True)
        self.mo_dialog.reset_isoline_border()
        directions_x = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]])
        assert np.array_equal(self.mo_dialog.isoline_border_direction, directions_x)
        self.mo_dialog.ui.yAxisCheckBox.setChecked(True)
        self.mo_dialog.reset_isoline_border()
        directions_y = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]])
        assert np.array_equal(self.mo_dialog.isoline_border_direction, directions_y)
        self.mo_dialog.ui.zAxisCheckBox.setChecked(True)
        self.mo_dialog.reset_isoline_border()
        directions_z = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])
        assert np.array_equal(self.mo_dialog.isoline_border_direction, directions_z)
        self.mo_dialog.ui.selectAtomsCheckBox.setChecked(True)
        self.mo_dialog.isoline_selected_atoms = [0, 1, 2]
        self.mo_dialog.reset_isoline_border()
        assert np.array_equal(self.mo_dialog.isoline_border_direction, directions_x)
        self.mo_dialog.ui.xAxisCheckBox.setChecked(True)
        self.mo_dialog.reset_isoline_border()
