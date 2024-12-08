"""Module for displaying the MOs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent

    from molara.structure.atom import Atom
    from molara.structure.basisset import BasisFunction
    from molara.structure.molecularorbitals import MolecularOrbitals


from pyrr.matrix33 import create_from_axis_rotation
from PySide6.QtWidgets import QButtonGroup, QHeaderView, QMainWindow, QTableWidgetItem

from molara.eval.generate_voxel_grid import generate_voxel_grid
from molara.eval.marchingsquares import marching_squares
from molara.eval.voxel_grid import VoxelGrid2D
from molara.gui.surface_3d import Surface3DDialog
from molara.gui.ui_mos_dialog import Ui_MOs_dialog
from molara.util.constants import ANGSTROM_TO_BOHR

__copyright__ = "Copyright 2024, Molara"


class MOsDialog(Surface3DDialog):
    """Dialog for displaying MOs."""

    def __init__(self, parent: QMainWindow = None) -> None:  # noqa: PLR0915
        """Initialize the MOs dialog.

        params:
        parent: MainWindow: The widget of the MainWindow.
        """
        super().__init__(
            parent,
        )
        self.mos: None | MolecularOrbitals = None
        self.aos: None | list[BasisFunction] = None
        self.atoms: None | list[Atom] = None

        # Voxel grid parameters
        self.size = np.zeros(3, dtype=np.float64)
        self.direction = np.zeros((3, 3), dtype=np.float64)
        self.origin = np.zeros(3, dtype=np.float64)
        self.voxel_grid_parameters_changed = True

        # Display box for voxel grid parameters
        self.box_center = np.zeros(3, dtype=np.float64)
        self.minimum_box_size = np.zeros(3, dtype=np.float64)
        self.display_box = False
        self.box_spheres = -1
        self.box_cylinders = -1
        self.initial_box_size = 2
        self.box_positions: np.ndarray = np.array([])
        self.box_radii: np.ndarray = np.array([])
        self.box_colors: np.ndarray = np.array([])
        self.box_corners: np.ndarray = np.array([])

        # Orbital selection parameters
        self.old_orbital = 0
        self.selected_orbital = 0
        self.number_of_alpha_orbitals = 0
        self.number_of_beta_orbitals = 0
        self.number_of_orbitals = 0
        # 0 for restricted, 1 for alpha, -1 for beta
        self.display_spin = 0

        # Ui connections
        self.ui = Ui_MOs_dialog()
        self.ui.setupUi(self)
        self.ui.displayMos.clicked.connect(self.toggle_surfaces)
        self.ui.orbitalSelector.cellClicked.connect(self.select_row)
        self.ui.toggleDisplayBoxButton.clicked.connect(self.toggle_box)
        self.ui.cubeBoxSizeSpinBox.valueChanged.connect(self.calculate_and_show_new_box)
        self.ui.checkBoxWireMesh.clicked.connect(self.toggle_wire_mesh)
        self.ui.alphaCheckBox.clicked.connect(self.select_spin_alpha)
        self.ui.betaCheckBox.clicked.connect(self.select_spin_beta)
        self.ui.cutoffSpinBox.valueChanged.connect(self.on_change_surface_voxel_parameters)
        self.ui.resolutionSpinBox.valueChanged.connect(self.on_change_surface_voxel_parameters)
        self.ui.isoValueSpinBox.valueChanged.connect(self.change_iso_value)
        self.ui.colorPlusButton.clicked.connect(self.show_color_dialog_1)
        self.ui.colorMinusButton.clicked.connect(self.show_color_dialog_2)
        self.ui.recalculateOrbitalButton.clicked.connect(self.recalculate_orbital)
        self.ui.isoTab.currentChanged.connect(self.update_selected_atoms)

        self.surface_toggle_button = self.ui.displayMos
        self.surface_text = "Orbital"

        # isoline checkboxgroups
        self.isoline_border_normal_group = QButtonGroup()
        self.ui.xAxisCheckBox.setChecked(True)
        self.isoline_border_normal_group.addButton(self.ui.xAxisCheckBox, id=1)
        self.isoline_border_normal_group.addButton(self.ui.yAxisCheckBox, id=2)
        self.isoline_border_normal_group.addButton(self.ui.zAxisCheckBox, id=3)
        self.isoline_border_normal_group.addButton(self.ui.selectAtomsCheckBox, id=4)
        self.isoline_border_rot_trans_scale_group = QButtonGroup()
        self.ui.scaleCheckBox.setChecked(True)
        self.isoline_border_rot_trans_scale_group.addButton(self.ui.scaleCheckBox, id=1)
        self.isoline_border_rot_trans_scale_group.addButton(self.ui.rotateCheckBox, id=2)
        self.isoline_border_rot_trans_scale_group.addButton(self.ui.translateCheckBox, id=3)

        # isoline ui connections
        self.isoline_border_normal_group.buttonClicked.connect(self.change_isoline_border_normal_selection)
        self.isoline_border_rot_trans_scale_group.buttonClicked.connect(self.change_isoline_border_transformation)
        self.ui.displayIsolinesButton.clicked.connect(self.toggle_isolines)
        self.ui.numberLinesSpinBox.valueChanged.connect(self.change_number_of_lines)
        self.ui.isolineResolutionSpinBox.valueChanged.connect(self.change_isoline_resolution)
        self.ui.displayIsolineBorderButton.clicked.connect(self.toggle_isoline_border)
        self.ui.resetButton.clicked.connect(self.reset_isoline_border)
        self.ui.displayAxesButton.clicked.connect(self.toggle_isoline_axes)
        self.ui.redSpinBox.valueChanged.connect(self.transform_isoline_border_red)
        self.ui.greenSpinBox.valueChanged.connect(self.transform_isoline_border_green)
        self.ui.blueSpinBox.valueChanged.connect(self.transform_isoline_border_blue)

        # Isoline parameters
        self.isolines_are_visible = False
        self.isoline_radius = 0.006
        self.isoline_drawn_lines = [-1, -1]
        self.isoline_voxel_grid = VoxelGrid2D()
        self.isoline_grid_parameters_changed = True
        self.isolines_1: np.ndarray = np.array([])
        self.isolines_2: np.ndarray = np.array([])
        self.isoline_border_origin: np.ndarray = np.array([])
        self.isoline_border_size: np.ndarray = np.array([4, 4])
        self.isoline_border_scale = [1, 1]
        self.isoline_border_direction = np.zeros((3, 3), dtype=np.float64)
        self.isoline_border_center = np.zeros(3, dtype=np.float64)
        self.isoline_border_cylinders = -1
        self.isoline_border_spheres = -1
        self.isoline_axes_cylinders = -1
        self.isoline_axes_spheres = -1
        self.isoline_axes_visible = False
        self.isoline_rotation_values = [0, 0, 0]
        self.isoline_translation_values = [0, 0, 0]
        self.isoline_border_points: np.ndarray = np.array([])
        self.isoline_border_normal: np.ndarray = np.array([])
        self.isoline_selected_atoms: list = [-1] * 3
        self.isoline_drawn_spheres: list = [-1] * 3
        self.isoline_border_is_visible = False

        # isoline setup border
        self.isoline_initialize_border()

    def update_color_buttons(self) -> None:
        """Update the color buttons."""
        self.ui.colorPlusButton.setStyleSheet(
            f"background-color: rgb({self.color_surface_1[0]}, {self.color_surface_1[1]}, {self.color_surface_1[2]})",
        )
        self.ui.colorMinusButton.setStyleSheet(
            f"background-color: rgb({self.color_surface_2[0]}, {self.color_surface_2[1]}, {self.color_surface_2[2]})",
        )

    def change_color_surface_1(self) -> None:
        """Change the color of the first surface."""
        super().change_color_surface_1()
        self.update_color_buttons()
        if not self.voxel_grid_parameters_changed:
            self.display_surfaces()
        if not self.isoline_grid_parameters_changed:
            self.display_isolines()

    def change_color_surface_2(self) -> None:
        """Change the color of the second surface."""
        super().change_color_surface_2()
        self.update_color_buttons()
        if not self.voxel_grid_parameters_changed:
            self.display_surfaces()
        if not self.isoline_grid_parameters_changed:
            self.display_isolines()

    def set_recalculate_voxel_grid(self) -> None:
        """Set the flag to recalculate the voxel grid, when drawing an orbital for the next time."""
        self.voxel_grid_parameters_changed = True

    def initialize_dialog(self) -> None:
        """Call all the functions to initialize all the labels and buttons and so on."""
        # Check if a structure with MOs is loaded
        if not self.parent().structure_widget.structures:
            return
        if self.parent().structure_widget.structures[0].mos.coefficients.size == 0:
            return
        # Set all molecule related variables
        self.set_molecule(self.parent().structure_widget.structures[0])
        if self.molecule is None:
            msg = "No molecule loaded"
            raise ValueError(msg)

        self.mos = self.molecule.mos
        self.aos = self.molecule.basis_set
        self.atoms = self.molecule.atoms

        # Set the labels and buttons
        self.ui.orbTypeLabel.setText(self.mos.basis_type)
        self.init_spin_labels()
        self.setup_orbital_selector()
        self.fill_orbital_selector()
        self.update_color_buttons()
        self.ui.recalculateOrbitalButton.setDisabled(True)

        # Set the box size and draw the box
        self.calculate_minimum_box_size()

        # isolines initialization
        isoline_tab = 1
        self.change_isoline_border_transformation()
        if self.ui.isoTab.currentIndex() == isoline_tab:
            self.draw_isoline_selected_atoms()

        self.show()

    def init_spin_labels(self) -> None:
        """Initialize the labels for alpha, beta spins or a restricted calculation."""
        if self.mos is None:
            msg = "No molecular orbitals loaded"
            raise ValueError(msg)
        if -1 in self.mos.spins and 1 in self.mos.spins:
            self.ui.restrictedLabel.hide()
            self.ui.alphaCheckBox.show()
            self.ui.betaCheckBox.show()
            self.ui.alphaCheckBox.setChecked(True)
            self.ui.betaCheckBox.setChecked(False)
            self.display_spin = 1
        else:
            self.ui.restrictedLabel.setText("Restricted")
            self.ui.restrictedLabel.show()
            self.ui.alphaCheckBox.hide()
            self.ui.betaCheckBox.hide()
            self.display_spin = 0

    def select_spin_alpha(self) -> None:
        """Select the spin with the checkboxes and update the displayed mos accordingly."""
        if self.ui.alphaCheckBox.isChecked():
            self.ui.betaCheckBox.setChecked(False)
        self.ui.alphaCheckBox.setChecked(True)
        self.display_spin = 1
        self.fill_orbital_selector()
        self.select_row()
        self.set_recalculate_voxel_grid()

    def select_spin_beta(self) -> None:
        """Select the spin with the checkboxes and update the displayed mos accordingly."""
        if self.ui.betaCheckBox.isChecked():
            self.ui.alphaCheckBox.setChecked(False)
        self.ui.betaCheckBox.setChecked(True)
        self.display_spin = -1
        self.fill_orbital_selector()
        self.select_row()
        self.set_recalculate_voxel_grid()

    def select_row(self) -> None:
        """When a cell is selected, select the whole row."""
        self.ui.orbitalSelector.selectRow(self.ui.orbitalSelector.currentRow())
        if self.display_spin == 0:
            self.selected_orbital = self.ui.orbitalSelector.currentRow()
        if self.display_spin == 1:
            self.selected_orbital = self.ui.orbitalSelector.currentRow()
            self.old_orbital = self.selected_orbital
        if self.display_spin == -1:
            self.old_orbital = self.ui.orbitalSelector.currentRow()
            self.selected_orbital = self.old_orbital + self.number_of_alpha_orbitals

        self.set_recalculate_voxel_grid()
        self.update_surfaces()

        self.set_recalculate_isoline_grid()
        self.update_isolines(self.isolines_are_visible)

    def setup_orbital_selector(self) -> None:
        """Set up the orbital selector."""

        def set_resize_modes(obj: QHeaderView, modes: list) -> None:
            for i, mode in enumerate(modes):
                obj.setSectionResizeMode(i, mode)

        _, __, stretch = (
            QHeaderView.Fixed,
            QHeaderView.ResizeToContents,
            QHeaderView.Stretch,
        )

        self.ui.orbitalSelector.setColumnCount(2)
        self.ui.orbitalSelector.setHorizontalHeaderLabels(["Energy", "Occupation"])
        header_positions = self.ui.orbitalSelector.horizontalHeader()
        set_resize_modes(header_positions, [stretch, stretch])

    def fill_orbital_selector(self) -> None:
        """Fill the orbital selector."""
        if self.mos is None:
            msg = "No molecular orbitals loaded"
            raise ValueError(msg)
        number_of_orbitals = 0
        max_number_of_orbitals = 0
        start = 0
        self.ui.orbitalSelector.clearContents()

        if self.display_spin == 0:
            self.number_of_orbitals = len(self.mos.energies)
            number_of_orbitals = self.number_of_orbitals
            max_number_of_orbitals = self.number_of_orbitals
            start = 0
        elif self.display_spin == 1:
            max_number_of_orbitals = sum([1 for spin in self.mos.spins if spin == 1])
            number_of_orbitals = max_number_of_orbitals
            self.number_of_alpha_orbitals = number_of_orbitals
            self.number_of_orbitals = len(self.mos.energies)
            self.number_of_beta_orbitals = self.number_of_orbitals - number_of_orbitals
            start = 0
        elif self.display_spin == -1:
            number_of_alpha_orbitals = sum([1 for spin in self.mos.spins if spin == 1])
            number_of_orbitals = sum([1 for spin in self.mos.spins if spin == -1])
            self.number_of_orbitals = number_of_orbitals + number_of_alpha_orbitals
            max_number_of_orbitals = self.number_of_orbitals
            self.number_of_alpha_orbitals = number_of_alpha_orbitals
            self.number_of_beta_orbitals = self.number_of_orbitals - number_of_orbitals
            start = number_of_alpha_orbitals

        self.ui.orbitalSelector.setRowCount(number_of_orbitals)

        # Fill the selector with energies rounded up to 3 digits and all the numbers aligned to the right
        for i in range(start, max_number_of_orbitals):
            energy_item = QTableWidgetItem()
            energy_item.setTextAlignment(Qt.AlignRight)
            energy_item.setText(f"{self.mos.energies[i]:.3f}")
            self.ui.orbitalSelector.setItem(i - start, 0, energy_item)

            occupation_item = QTableWidgetItem()
            occupation_item.setTextAlignment(Qt.AlignRight)
            occupation_item.setText(f"{self.mos.occupations[i]:.3f}")
            self.ui.orbitalSelector.setItem(i - start, 1, occupation_item)

        self.ui.orbitalSelector.selectRow(self.old_orbital)

    def calculate_minimum_box_size(self) -> None:
        """Calculate the minimum box size to fit the molecular orbitals."""
        max_x = min_x = max_y = min_y = max_z = min_z = 0
        for atom in self.parent().structure_widget.structures[0].atoms:
            max_x = max(atom.position[0], max_x)
            min_x = min(atom.position[0], min_x)
            max_y = max(atom.position[1], max_y)
            min_y = min(atom.position[1], min_y)
            max_z = max(atom.position[2], max_z)
            min_z = min(atom.position[2], min_z)
        self.box_center = np.array(
            [(max_x + min_x) / 2, (max_y + min_y) / 2, (max_z + min_z) / 2],
        )
        self.minimum_box_size = np.array([max_x - min_x, max_y - min_y, max_z - min_z])
        self.direction = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64)
        self.scale_box()
        self.calculate_new_box()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Close the dialog."""
        super().closeEvent(event)
        self.remove_box()
        self.remove_isolines()
        self.remove_isoline_border()
        self.remove_isoline_axes()

        # select the x axis as default for the normal vector for the isoline borders
        self.ui.xAxisCheckBox.setChecked(True)
        self.remove_isoline_selected_atoms()

    def calculate_corners_of_box(self) -> np.ndarray:
        """Calculate the corners of the cube."""
        origin = self.origin
        direction = self.direction
        size = self.size
        corners = np.zeros((8, 3), dtype=np.float64)
        for i in range(8):
            corners[i, :] = (
                origin
                + direction[0] * (i % 2) * size[0]
                + direction[1] * ((i // 2) % 2) * size[1]
                + direction[2] * (i // 4) * size[2]
            )
        return corners

    def toggle_box(self) -> None:
        """Toggle the cube."""
        self.parent().structure_widget.makeCurrent()
        self.display_box = not self.display_box
        if not self.display_box:
            self.remove_box()
            self.ui.toggleDisplayBoxButton.setText("Display Box")
            return
        self.ui.toggleDisplayBoxButton.setText("Hide Box")
        self.draw_box()

    def remove_box(self) -> None:
        """Remove the box."""
        self.parent().structure_widget.makeCurrent()
        if self.box_spheres != -1:
            self.parent().structure_widget.renderer.remove_sphere(self.box_spheres)
            self.box_spheres = -1
        if self.box_cylinders != -1:
            self.parent().structure_widget.renderer.remove_cylinder(self.box_cylinders)
            self.box_cylinders = -1
        self.parent().structure_widget.update()

    def scale_box(self) -> None:
        """Scale the box to fit the molecular orbitals."""
        self.size = self.minimum_box_size + self.ui.cubeBoxSizeSpinBox.value() + self.initial_box_size
        self.origin = self.box_center - self.size / 2

    def calculate_and_show_new_box(self) -> None:
        """Calculate and show a new box."""
        self.calculate_new_box()
        self.on_change_surface_voxel_parameters()
        if self.display_box:
            self.draw_box()

    def calculate_new_box(self) -> None:
        """Calculate a new box."""
        self.parent().structure_widget.makeCurrent()
        self.remove_box()
        self.scale_box()
        self.box_corners = self.calculate_corners_of_box()
        self.box_positions = np.array(
            [
                [self.box_corners[0], self.box_corners[1]],
                [self.box_corners[0], self.box_corners[2]],
                [self.box_corners[3], self.box_corners[1]],
                [self.box_corners[3], self.box_corners[2]],
                [self.box_corners[4], self.box_corners[5]],
                [self.box_corners[4], self.box_corners[6]],
                [self.box_corners[7], self.box_corners[5]],
                [self.box_corners[7], self.box_corners[6]],
                [self.box_corners[0], self.box_corners[4]],
                [self.box_corners[1], self.box_corners[5]],
                [self.box_corners[2], self.box_corners[6]],
                [self.box_corners[3], self.box_corners[7]],
            ],
            dtype=np.float32,
        )
        radius = 0.01
        self.box_colors = np.array([0, 0, 0] * 12, dtype=np.float32)
        self.box_radii = np.array([radius] * 12, dtype=np.float32)

    def draw_box(self) -> None:
        """Draw the box to see where the mos will be calculated."""
        self.box_cylinders = self.parent().structure_widget.renderer.draw_cylinders_from_to(
            self.box_positions,
            self.box_radii,
            self.box_colors,
            10,
        )
        self.box_spheres = self.parent().structure_widget.renderer.draw_spheres(
            np.array(self.box_corners, dtype=np.float32),
            self.box_radii,
            self.box_colors,
            10,
        )
        self.parent().structure_widget.update()

    def voxel_size_value(self, voxel_size_min: float = 0.05, voxel_size_max: float = 0.35) -> float:
        """Get the voxel size value from the resolution.

        Using a minimal value of 0.05 and a maximal value of 0.35 for the voxel size, a resolution between 1 and 0 is
        mapped to this range.
        :param voxel_size_min: minimal value for the voxel size
        :param voxel_size_max: maximal value for the voxel size
        :return: scaled value for the voxel size
        """
        a = voxel_size_min - voxel_size_max
        b = voxel_size_max

        return a * self.ui.resolutionSpinBox.value() + b

    def calculate_voxelgrid(self) -> None:
        """Calculate the voxel grid."""
        if self.aos is None:
            msg = "No basis functions loaded"
            raise ValueError(msg)
        if self.mos is None:
            msg = "No molecular orbitals loaded"
            raise ValueError(msg)

        self.voxel_grid.voxel_size = np.eye(3, dtype=np.float64) * self.voxel_size_value()
        mo_coefficients = self.mos.coefficients[:, self.selected_orbital]

        self.voxel_grid.origin = self.origin
        direction = self.direction
        voxel_size = self.voxel_size_value()
        self.voxel_grid.voxel_number = np.array(
            [
                int(self.size[0] / voxel_size) + 1,
                int(self.size[1] / voxel_size) + 1,
                int(self.size[2] / voxel_size) + 1,
            ],
            dtype=np.int64,
        )
        self.voxel_grid.voxel_size = direction * voxel_size

        shells_cut_off = self.calculate_cutoffs()

        self.voxel_grid.grid = np.array(
            generate_voxel_grid(
                self.voxel_grid.origin,
                self.voxel_grid.voxel_size,
                self.voxel_grid.voxel_number,
                self.aos,
                mo_coefficients,
                shells_cut_off,
            ),
        )
        self.voxel_grid_parameters_changed = False
        self.voxel_grid_changed = True

    def calculate_cutoffs(self) -> np.ndarray:
        """Calculate the cutoffs for the shells."""
        if self.aos is None:
            msg = "No basis functions loaded"
            raise ValueError(msg)
        if self.mos is None:
            msg = "No molecular orbitals loaded"
            raise ValueError(msg)
        # Calculate the cutoffs for the shells
        max_distance = np.linalg.norm(self.size * ANGSTROM_TO_BOHR)
        max_number = int(max_distance * 5)
        threshold = 10 ** self.ui.cutoffSpinBox.value()

        return self.mos.calculate_cut_offs(
            self.aos,
            self.selected_orbital,
            threshold=threshold,
            max_distance=max_distance,
            max_points_number=max_number,
        )

    def change_iso_value(self) -> None:
        """Change the iso value."""
        self.set_iso_value(self.ui.isoValueSpinBox.value())
        if not self.voxel_grid_parameters_changed:
            self.visualize_surfaces()

    def set_surfaces_hidden(self) -> None:
        """Set the surfaces hidden."""
        super().set_surfaces_hidden()
        self.ui.recalculateOrbitalButton.setDisabled(True)

    def update_voxel_grid(self) -> None:
        """Update the voxel grid."""
        if self.voxel_grid_parameters_changed:
            self.calculate_voxelgrid()

        self.set_iso_value(self.ui.isoValueSpinBox.value())

    def set_recalculate_isoline_grid(self) -> None:
        """Set a flag to recalculate the isoline grid."""
        self.isoline_grid_parameters_changed = True

    def on_change_surface_voxel_parameters(self) -> None:
        """Change the voxel size of the surface."""
        self.set_recalculate_voxel_grid()
        self.ui.recalculateOrbitalButton.setEnabled(True)

    def recalculate_orbital(self) -> None:
        """Recalculate the orbital."""
        self.set_surfaces_visible()
        self.ui.recalculateOrbitalButton.setDisabled(True)

    def change_number_of_lines(self) -> None:
        """Change the number of lines, does not recalculate the grid if needed."""
        if not self.isoline_grid_parameters_changed:
            self.visualize_isolines()

    def remove_isolines(self) -> None:
        """Remove the isolines."""
        self.parent().structure_widget.makeCurrent()
        for line in self.isoline_drawn_lines:
            if line != -1:
                self.parent().structure_widget.renderer.remove_cylinder(line)
        self.isoline_drawn_lines = [-1, -1]
        self.parent().structure_widget.update()
        self.set_isolines_hidden()

    def set_isoline_border_points(self) -> None:
        """Set the points of the border that can be displayed as a guide to the eye."""
        if self.isoline_border_origin is None:
            msg = "No origin for the isoline border set"
            raise ValueError(msg)
        if self.isoline_border_size is None:
            msg = "No size for the isoline border set"
            raise ValueError(msg)
        if self.isoline_border_direction is None:
            msg = "No direction for the isoline border set"
            raise ValueError(msg)

        size_direction_1 = self.isoline_border_size[0] * self.isoline_border_direction[0] * self.isoline_border_scale[0]
        size_direction_2 = self.isoline_border_size[1] * self.isoline_border_direction[1] * self.isoline_border_scale[1]
        self.isoline_border_points = np.array(
            [
                self.isoline_border_origin,
                self.isoline_border_origin + size_direction_1,
                self.isoline_border_origin + size_direction_2,
                self.isoline_border_origin + size_direction_1 + size_direction_2,
            ],
            dtype=np.float32,
        )

    def display_isoline_border(self) -> None:
        """Display the border of the isoline grid."""
        self.set_isoline_border_points()
        cylinder_end_points = np.array(
            [
                [self.isoline_border_points[0], self.isoline_border_points[1]],
                [self.isoline_border_points[0], self.isoline_border_points[2]],
                [self.isoline_border_points[1], self.isoline_border_points[3]],
                [self.isoline_border_points[2], self.isoline_border_points[3]],
            ],
            dtype=np.float32,
        )
        self.isoline_border_cylinders = self.parent().structure_widget.renderer.draw_cylinders_from_to(
            cylinder_end_points,
            np.array([0.01] * 4, dtype=np.float32),
            np.array([0, 0, 0] * 4, dtype=np.float32),
            10,
        )
        self.isoline_border_spheres = self.parent().structure_widget.renderer.draw_spheres(
            self.isoline_border_points,
            np.array([0.01] * 4, dtype=np.float32),
            np.array([0, 0, 0] * 4, dtype=np.float32),
            10,
        )
        self.parent().structure_widget.update()

    def remove_isoline_border(self) -> None:
        """Remove the border of the isoline grid."""
        if self.isoline_border_cylinders != -1:
            self.parent().structure_widget.renderer.remove_cylinder(self.isoline_border_cylinders)
            self.isoline_border_cylinders = -1
        if self.isoline_border_spheres != -1:
            self.parent().structure_widget.renderer.remove_sphere(self.isoline_border_spheres)
            self.isoline_border_spheres = -1
        self.parent().structure_widget.update()

    def toggle_isoline_border(self) -> None:
        """Toggle the isoline grid border."""
        self.isoline_border_is_visible = not self.isoline_border_is_visible
        if self.isoline_border_is_visible:
            self.display_isoline_border()
            self.ui.displayIsolineBorderButton.setText("Hide Border")
            return
        self.remove_isoline_border()
        self.ui.displayIsolineBorderButton.setText("Display Border")
        self.remove_isoline_axes()
        self.ui.displayAxesButton.setText("Display Axes")

    def change_isoline_resolution(self) -> None:
        """Change the voxel size of the isoline grid."""
        self.isoline_grid_parameters_changed = True
        self.update_isolines(self.isolines_are_visible)

    def isoline_voxel_size_value(self, voxel_size_min: float = 0.03, voxel_size_max: float = 0.43) -> float:
        """Get the voxel size value from the resolution.

        Using a minimal value of 0.03 and a maximal value of 0.43 for the voxel size, a resolution between 1 and 0 is
        mapped to this range.
        :return: scaled value for the voxel size
        """
        a = voxel_size_min - voxel_size_max
        b = voxel_size_max

        return a * self.ui.isolineResolutionSpinBox.value() + b

    def calculate_isoline_voxelgrid(self) -> None:
        """Calculate the 2D voxel grid for the isolines."""
        if self.aos is None:
            msg = "No basis functions loaded"
            raise ValueError(msg)
        if self.mos is None:
            msg = "No molecular orbitals loaded"
            raise ValueError(msg)

        origin = self.isoline_border_origin
        size = self.isoline_border_size * self.isoline_border_scale

        voxel_size = self.isoline_border_direction * self.isoline_voxel_size_value()

        mo_coefficients = self.mos.coefficients[:, self.selected_orbital]

        voxel_number = np.array(
            [
                int(size[0] / self.isoline_voxel_size_value()) + 1,
                int(size[1] / self.isoline_voxel_size_value()) + 1,
                1,
            ],
            dtype=np.int64,
        )

        # Calculate the cutoffs for the shells
        shells_cut_off = self.calculate_cutoffs()

        grid = np.array(
            generate_voxel_grid(
                origin,
                voxel_size,
                voxel_number,
                self.aos,
                mo_coefficients,
                shells_cut_off,
            ),
        )[:, :, 0]
        self.isoline_voxel_grid.set_grid(grid, origin, voxel_size[:2])

    def set_isolines_hidden(self) -> None:
        """Set the isolines to hidden."""
        self.isolines_are_visible = False
        self.ui.displayIsolinesButton.setText("Display Isolines")

    def set_isolines_visible(self) -> None:
        """Set the isolines to visible."""
        self.isolines_are_visible = True
        self.ui.displayIsolinesButton.setText("Hide Isolines")

    def toggle_isolines(self) -> None:
        """Toggle the display of the isolines."""
        self.isolines_are_visible = not self.isolines_are_visible
        if self.isolines_are_visible:
            self.ui.displayIsolinesButton.setText("Hide Isolines")
            self.visualize_isolines()
            return
        self.ui.displayIsolinesButton.setText("Display Isolines")
        self.remove_isolines()

    def visualize_isolines(self) -> None:
        """Calculate the voxel grid."""
        if self.aos is None:
            msg = "No basis functions loaded"
            raise ValueError(msg)
        if self.mos is None:
            msg = "No molecular orbitals loaded"
            raise ValueError(msg)

        self.remove_isolines()

        number_of_iso_values = self.ui.numberLinesSpinBox.value()

        if self.isoline_grid_parameters_changed:
            self.calculate_isoline_voxelgrid()
            self.isoline_grid_parameters_changed = False

        grid = self.isoline_voxel_grid.grid
        origin = self.isoline_voxel_grid.origin
        voxel_size = self.isoline_voxel_grid.voxel_size
        voxel_number = self.isoline_voxel_grid.voxel_number

        grid_sum = np.sum(np.abs(grid))
        if grid_sum > np.finfo(float).eps:
            log_grid_max = 0.1  # np.log(np.max(np.abs(grid)))
            log_grid_min = np.log(3e-3)  # np.log(max(np.min(np.abs(grid)), 5e-3))
            iso_values = np.exp(np.linspace(log_grid_min, log_grid_max, number_of_iso_values))

            total_lines_1 = np.empty((0, 2, 3))
            total_lines_2 = np.empty((0, 2, 3))
            for iso in iso_values:
                lines_1 = np.zeros(((voxel_number[0] - 1) * (voxel_number[1] - 1) * 4 + 1, 3), dtype=np.float32)
                lines_2 = np.zeros(((voxel_number[0] - 1) * (voxel_number[1] - 1) * 4 + 1, 3), dtype=np.float32)
                _ = marching_squares(grid, iso, origin, voxel_size, voxel_number, lines_1, lines_2)
                number_of_lines_entries_1 = int(lines_1[-1, -1])
                number_of_lines_entries_2 = int(lines_2[-1, -1])

                if number_of_lines_entries_1 != 0:
                    lines_1 = lines_1[:number_of_lines_entries_1]
                    total_lines_1 = np.concatenate(
                        [total_lines_1, lines_1.reshape((number_of_lines_entries_1 // 2, 2, 3))],
                        axis=0,
                    )
                if number_of_lines_entries_2 != 0:
                    lines_2 = lines_2[:number_of_lines_entries_2]
                    total_lines_2 = np.concatenate(
                        [total_lines_2, lines_2.reshape((number_of_lines_entries_2 // 2, 2, 3))],
                        axis=0,
                    )
            self.isolines_1 = total_lines_1
            self.isolines_2 = total_lines_2
            self.draw_isolines()
            self.isolines_are_visible = True

    def draw_isolines(self) -> None:
        """Draw the isolines."""
        self.parent().structure_widget.makeCurrent()
        self.remove_isolines()
        radii_1 = np.array([self.isoline_radius] * self.isolines_1.shape[0], dtype=np.float32)
        colors_1 = np.array(list(self.color_surface_1 / 255) * self.isolines_1.shape[0], dtype=np.float32)
        radii_2 = np.array([self.isoline_radius] * self.isolines_2.shape[0], dtype=np.float32)
        colors_2 = np.array(list(self.color_surface_2 / 255) * self.isolines_2.shape[0], dtype=np.float32)
        self.isoline_drawn_lines[0] = self.parent().structure_widget.renderer.draw_cylinders_from_to(
            self.isolines_1,
            radii_1,
            colors_1,
            10,
        )
        self.isoline_drawn_lines[1] = self.parent().structure_widget.renderer.draw_cylinders_from_to(
            self.isolines_2,
            radii_2,
            colors_2,
            10,
        )
        self.parent().structure_widget.update()
        self.set_isolines_visible()

    def isolines_are_initialized(self) -> bool:
        """Check if the isolines are initialized."""
        return (self.isolines_1.size != 0 or self.isolines_2.size != 0) and not self.isoline_grid_parameters_changed

    def display_isolines(self) -> None:
        """Display the isolines."""
        if self.isolines_are_initialized():
            self.draw_isolines()
        else:
            self.visualize_isolines()

    def isoline_initialize_border(self) -> None:
        """Initialize the isoline border."""
        self.set_isoline_border_parameters_from_normal(np.array([1, 0, 0], dtype=np.float64))
        self.update_isoline_border_origin()

    def reset_isoline_border_transformation_values(self) -> None:
        """Reset the isoline border transformation values."""
        self.isoline_rotation_values = [0, 0, 0]
        self.isoline_translation_values = [0, 0, 0]
        self.isoline_border_scale = [1, 1]
        self.change_isoline_border_transformation()

    def change_isoline_border_transformation(self) -> None:
        """Call when the user changes the transformation mode of the isoline border."""
        rotate = 2
        translate = 3
        scale = 1

        self.ui.redSpinBox.setEnabled(True)
        self.ui.greenSpinBox.setEnabled(True)
        self.ui.blueSpinBox.setEnabled(True)
        spin_boxes = [self.ui.redSpinBox, self.ui.greenSpinBox, self.ui.blueSpinBox]
        if self.isoline_border_rot_trans_scale_group.checkedId() == rotate:
            for i, spin_box in enumerate(spin_boxes):
                # Set minimum and maximum values
                spin_box.setMinimum(-180)
                spin_box.setMaximum(180)
                # Set the values of the spin boxes to the current values
                spin_box.setValue(self.isoline_rotation_values[i])
                # Set the increment of the spin boxes to 1
                spin_box.setSingleStep(5)

        elif self.isoline_border_rot_trans_scale_group.checkedId() == translate:
            for i, spin_box in enumerate(spin_boxes):
                # Set minimum and maximum values to largest possible to avoid conflicts when changing the mode
                spin_box.setMinimum(-180)
                spin_box.setMaximum(180)
                # Set the values of the spin boxes to the current values
                spin_box.setValue(self.isoline_translation_values[i])
                # Set the increment of the spin boxes to 0.1
                spin_box.setSingleStep(0.1)
                # Set minimum and maximum values
                spin_box.setMinimum(-100)
                spin_box.setMaximum(100)

        elif self.isoline_border_rot_trans_scale_group.checkedId() == scale:
            # Disable the blue spin box
            self.ui.blueSpinBox.setEnabled(False)
            self.ui.blueSpinBox.setValue(0)
            for i, spin_box in enumerate(spin_boxes[:2]):
                # Set minimum and maximum values to largest possible to avoid conflicts when changing the mode
                spin_box.setMinimum(-180)
                spin_box.setMaximum(180)
                # Set the values of the spin boxes to the current values
                spin_box.setValue(self.isoline_border_scale[i])
                # Set the increment of the spin boxes to 0.1
                spin_box.setSingleStep(0.1)
                # Set minimum and maximum values
                spin_box.setMinimum(0.1)
                spin_box.setMaximum(100)

    def reset_isoline_border(self) -> None:
        """Reset the isoline border."""
        were_visible = self.isolines_are_visible
        self.remove_isolines()
        self.set_recalculate_isoline_grid()
        self.isoline_border_center = np.array([0, 0, 0], dtype=np.float64)
        self.reset_isoline_border_transformation_values()

        x_axis = 1
        y_axis = 2
        z_axis = 3
        custom_atom_selection = 4

        if self.isoline_border_normal_group.checkedId() == x_axis:
            self.set_isoline_border_parameters_from_normal(np.array([1, 0, 0], dtype=np.float64))
        elif self.isoline_border_normal_group.checkedId() == y_axis:
            self.set_isoline_border_parameters_from_normal(np.array([0, 1, 0], dtype=np.float64))
        elif self.isoline_border_normal_group.checkedId() == z_axis:
            self.set_isoline_border_parameters_from_normal(np.array([0, 0, 1], dtype=np.float64))
        elif self.isoline_border_normal_group.checkedId() == custom_atom_selection:
            self.change_isoline_border_normal_selection()
            if -1 not in self.isoline_selected_atoms:
                self.set_isoline_border_parameters_from_atoms_plane()
        else:
            return
        self.update_isolines(were_visible)

    def set_isoline_border_parameters_from_atoms_plane(self) -> None:
        """Calculate the normal of the isoline border plane from the selected atoms and set the parameters."""
        atom1 = self.parent().structure_widget.structures[0].atoms[self.isoline_selected_atoms[0]]
        atom2 = self.parent().structure_widget.structures[0].atoms[self.isoline_selected_atoms[1]]
        atom3 = self.parent().structure_widget.structures[0].atoms[self.isoline_selected_atoms[2]]
        self.isoline_border_center = (atom1.position + atom2.position + atom3.position) / 3
        normal = np.cross(atom2.position - atom1.position, atom3.position - atom1.position)

        # check if selected atoms lie in the same line
        if np.linalg.norm(normal) == 0:
            normal = np.cross(atom2.position - atom1.position, np.array([0, 0, 1], dtype=np.float64))
        if np.linalg.norm(normal) == 0:
            normal = np.cross(atom2.position - atom1.position, np.array([0, 1, 0], dtype=np.float64))

        normal /= np.linalg.norm(normal)
        self.set_isoline_border_parameters_from_normal(normal)

    def change_isoline_border_normal_selection(self) -> None:
        """Check if the custom atom selection option is checked and set the border parameters accordingly."""
        custom_atoms_selection = 4
        if self.isoline_border_normal_group.checkedId() == custom_atoms_selection:
            if -1 in self.isoline_selected_atoms:
                self.set_isoline_reset_button_text("Select 3 Atoms")
            else:
                self.set_isoline_reset_button_text("Reset Plane")
        else:
            self.set_isoline_reset_button_text("Reset Plane")

    def set_isoline_reset_button_text(self, text: str) -> None:
        """Set the text of the reset button."""
        self.ui.resetButton.setText(text)

    def transform_isoline_border_red(self) -> None:
        """Transform the isoline border with the red axis. This wraps different cases."""
        rotate = 2
        translate = 3
        scale = 1
        if self.isoline_border_rot_trans_scale_group.checkedId() == rotate:
            axis = self.isoline_border_direction[0]
            value = self.isoline_rotation_values[0] - self.ui.redSpinBox.value()
            if value == 0:
                return
            self.set_recalculate_isoline_grid()
            self.rotate_isoline_border(axis, value)
            self.isoline_rotation_values[0] = self.ui.redSpinBox.value()

        if self.isoline_border_rot_trans_scale_group.checkedId() == scale:
            if self.isoline_border_scale[0] == self.ui.redSpinBox.value():
                return
            self.set_recalculate_isoline_grid()
            self.isoline_border_scale[0] = self.ui.redSpinBox.value()
            self.update_isolines(self.isolines_are_visible)

        if self.isoline_border_rot_trans_scale_group.checkedId() == translate:
            axis = self.isoline_border_direction[0]
            value = self.isoline_translation_values[0] - self.ui.redSpinBox.value()
            if value == 0:
                return
            self.set_recalculate_isoline_grid()
            self.isoline_border_center -= axis * value
            self.update_isolines(self.isolines_are_visible)
            self.isoline_translation_values[0] = self.ui.redSpinBox.value()

    def transform_isoline_border_green(self) -> None:
        """Transform the isoline border with the green axis. This wraps different cases."""
        rotate = 2
        translate = 3
        scale = 1
        if self.isoline_border_rot_trans_scale_group.checkedId() == rotate:
            axis = self.isoline_border_direction[1]
            value = self.isoline_rotation_values[1] - self.ui.greenSpinBox.value()
            if value == 0:
                return
            self.set_recalculate_isoline_grid()
            self.rotate_isoline_border(axis, value)
            self.isoline_rotation_values[1] = self.ui.greenSpinBox.value()

        if self.isoline_border_rot_trans_scale_group.checkedId() == scale:
            if self.isoline_border_scale[1] == self.ui.greenSpinBox.value():
                return
            self.set_recalculate_isoline_grid()
            self.isoline_border_scale[1] = self.ui.greenSpinBox.value()
            self.update_isolines(self.isolines_are_visible)

        if self.isoline_border_rot_trans_scale_group.checkedId() == translate:
            axis = self.isoline_border_direction[1]
            value = self.isoline_translation_values[1] - self.ui.greenSpinBox.value()
            if value == 0:
                return
            self.set_recalculate_isoline_grid()
            self.isoline_border_center -= axis * value
            self.update_isolines(self.isolines_are_visible)
            self.isoline_translation_values[1] = self.ui.greenSpinBox.value()

    def transform_isoline_border_blue(self) -> None:
        """Transform the isoline border with the blue axis. This wraps different cases."""
        # No scale, because it is disabled for the blue axis
        rotate = 2
        translate = 3
        if self.isoline_border_rot_trans_scale_group.checkedId() == rotate:
            axis = self.isoline_border_direction[2]
            value = self.isoline_rotation_values[2] - self.ui.blueSpinBox.value()
            if value == 0:
                return
            self.set_recalculate_isoline_grid()
            self.rotate_isoline_border(axis, value)
            self.isoline_rotation_values[2] = self.ui.blueSpinBox.value()

        if self.isoline_border_rot_trans_scale_group.checkedId() == translate:
            axis = self.isoline_border_direction[2]
            value = self.isoline_translation_values[2] - self.ui.blueSpinBox.value()
            if value == 0:
                return
            self.set_recalculate_isoline_grid()
            self.isoline_border_center -= axis * value
            self.update_isolines(self.isolines_are_visible)
            self.isoline_translation_values[2] = self.ui.blueSpinBox.value()

    def update_isoline_border_origin(self) -> None:
        """Update the isoline border origin."""
        self.isoline_border_origin = (
            self.isoline_border_center
            - self.isoline_border_direction[0] * self.isoline_border_size[0] * self.isoline_border_scale[0] / 2
            - self.isoline_border_direction[1] * self.isoline_border_size[1] * self.isoline_border_scale[1] / 2
        )

    def update_isolines(self, isolines_were_visible: bool) -> None:
        """Scale the isoline border."""
        self.update_isoline_border_origin()

        if self.isoline_border_is_visible:
            self.remove_isoline_border()
            self.display_isoline_border()
        else:
            self.set_isoline_border_points()

        if isolines_were_visible:
            self.display_isolines()
            self.set_isolines_visible()

        if self.isoline_axes_visible:
            self.remove_isoline_axes()
            self.draw_isoline_axes()

    def rotate_isoline_border(self, axis: np.ndarray, value: float) -> None:
        """Transform the isoline border according to the selected checkboxes."""
        were_visible = self.isolines_are_visible
        self.remove_isolines()

        value *= np.pi / 180
        rotation_matrix = create_from_axis_rotation(axis, value)
        self.isoline_border_direction = np.dot(self.isoline_border_direction, rotation_matrix)
        self.update_isolines(were_visible)

    def remove_isoline_selected_atoms(self) -> None:
        """Remove the visualization of the selected atoms."""
        for sphere_index in self.isoline_drawn_spheres:
            if sphere_index != -1:
                self.parent().structure_widget.renderer.remove_sphere(sphere_index)
        self.isoline_drawn_spheres = [-1] * 3
        self.parent().structure_widget.update()

    def draw_isoline_selected_atoms(self) -> None:
        """Draw the selected atoms."""
        for i, atom_index in enumerate(self.isoline_selected_atoms):
            if atom_index != -1:
                self.isoline_drawn_spheres[i] = self.parent().structure_widget.draw_selected_atom(atom_index, i)
        self.parent().structure_widget.update()

    def update_selected_atoms(self) -> None:
        """Switch to the orbital tab."""
        orbital_tab = 0
        isoline_tab = 1
        if self.ui.isoTab.currentIndex() == orbital_tab:
            self.remove_isoline_selected_atoms()

        if self.ui.isoTab.currentIndex() == isoline_tab:
            self.draw_isoline_selected_atoms()

    def set_isoline_border_parameters_from_normal(
        self,
        normal: np.ndarray,
    ) -> None:
        """Set the isoline border parameters from the normal.

        :param normal: The normal of the isoline border. Must be normalized!
        :param center: The center of the isoline border.
        """
        y_axis = np.array([0, 1, 0], dtype=np.float64)
        z_axis = np.array([0, 0, 1], dtype=np.float64)

        if np.abs(np.linalg.norm(normal) - 1) > np.finfo(float).eps:
            msg = "The normal must be normalized!"
            raise ValueError(msg)

        temp_axis = y_axis if np.dot(normal, y_axis) != 1 else z_axis

        self.isoline_border_direction[0] = np.cross(normal, temp_axis)
        self.isoline_border_direction[0] /= np.linalg.norm(self.isoline_border_direction[0])
        self.isoline_border_direction[1] = np.cross(normal, -self.isoline_border_direction[0])
        self.isoline_border_direction[1] /= np.linalg.norm(self.isoline_border_direction[1])
        self.isoline_border_direction[2] = normal

    def toggle_isoline_axes(self) -> None:
        """Toggle the isoline axes."""
        self.isoline_axes_visible = not self.isoline_axes_visible
        if not self.isoline_border_is_visible:
            self.isoline_axes_visible = False
        if self.isoline_axes_visible:
            self.draw_isoline_axes()
            self.ui.displayAxesButton.setText("Hide Axes")
            return
        self.remove_isoline_axes()
        self.ui.displayAxesButton.setText("Display Axes")

    def remove_isoline_axes(self) -> None:
        """Remove the isoline axes used for rotation and translation."""
        if self.isoline_axes_cylinders != -1:
            self.parent().structure_widget.renderer.remove_cylinder(self.isoline_axes_cylinders)
            self.isoline_axes_cylinders = -1
        if self.isoline_axes_spheres != -1:
            self.parent().structure_widget.renderer.remove_sphere(self.isoline_axes_spheres)
            self.isoline_axes_spheres = -1
        self.parent().structure_widget.update()

    def draw_isoline_axes(self) -> None:
        """Draw the isoline axes used for rotation and translation."""
        self.remove_isoline_axes()
        axes_scale = 1 / 2
        cylinder_end_points = np.array(
            [
                [self.isoline_border_center, self.isoline_border_center + direction]
                for direction in (self.isoline_border_direction * axes_scale)
            ],
            dtype=np.float32,
        )
        sphere_positions = self.isoline_border_center + np.vstack(
            (np.zeros(3), self.isoline_border_direction * axes_scale),
        )
        radii = np.full(4, 0.025, dtype=np.float32)
        colors = np.eye(3, dtype=np.float32)
        cylinder_colors = colors[:3]
        sphere_colors = np.vstack(([np.zeros(3)], colors))
        self.parent().structure_widget.makeCurrent()
        self.isoline_axes_cylinders = self.parent().structure_widget.renderer.draw_cylinders_from_to(
            cylinder_end_points,
            radii[:3],
            cylinder_colors,
            10,
        )
        self.isoline_axes_spheres = self.parent().structure_widget.renderer.draw_spheres(
            np.array(sphere_positions, dtype=np.float32),
            radii,
            sphere_colors,
            10,
        )

        self.parent().structure_widget.update()
