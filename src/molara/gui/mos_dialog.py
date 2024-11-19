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

from PySide6.QtWidgets import QHeaderView, QMainWindow, QTableWidgetItem

from molara.eval.generate_voxel_grid import generate_voxel_grid
from molara.eval.populationanalysis import PopulationAnalysis
from molara.gui.surface_3d import Surface3DDialog
from molara.gui.ui_mos_dialog import Ui_MOs_dialog
from molara.util.constants import ANGSTROM_TO_BOHR

__copyright__ = "Copyright 2024, Molara"


class MOsDialog(Surface3DDialog):
    """Dialog for displaying MOs."""

    def __init__(self, parent: QMainWindow = None) -> None:
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
        self.ui.displayMos.clicked.connect(self.visualize_orbital)
        self.ui.orbitalSelector.cellClicked.connect(self.select_row)
        self.ui.toggleDisplayBoxButton.clicked.connect(self.toggle_box)
        self.ui.cubeBoxSizeSpinBox.valueChanged.connect(self.calculate_new_box)
        self.ui.checkBoxWireMesh.clicked.connect(self.toggle_wire_mesh)
        self.ui.alphaCheckBox.clicked.connect(self.select_spin_alpha)
        self.ui.betaCheckBox.clicked.connect(self.select_spin_beta)
        self.ui.normalizationButton.clicked.connect(self.run_population_analysis)
        self.ui.cutoffSpinBox.valueChanged.connect(self.set_recalculate_voxel_grid)
        self.ui.voxelSizeSpinBox.valueChanged.connect(self.set_recalculate_voxel_grid)
        self.ui.isoValueSpinBox.valueChanged.connect(self.change_iso_value)
        self.ui.colorPlusButton.clicked.connect(self.show_color_dialog_1)
        self.ui.colorMinusButton.clicked.connect(self.show_color_dialog_2)

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

    def change_color_surface_2(self) -> None:
        """Change the color of the second surface."""
        super().change_color_surface_2()
        self.update_color_buttons()
        if not self.voxel_grid_parameters_changed:
            self.display_surfaces()

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
        assert self.molecule is not None
        self.mos = self.molecule.mos
        self.aos = self.molecule.basis_set
        self.atoms = self.molecule.atoms

        # Set the labels and buttons
        self.ui.orbTypeLabel.setText(self.mos.basis_type)
        self.init_spin_labels()
        self.setup_orbital_selector()
        self.fill_orbital_selector()
        self.update_color_buttons()

        # Set the box size and draw the box
        self.calculate_minimum_box_size()

        self.show()

    def init_spin_labels(self) -> None:
        """Initialize the labels for alpha, beta spins or a restricted calculation."""
        assert self.mos is not None
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
        assert self.mos is not None
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

    def calculate_new_box(self) -> None:
        """Draw the box."""
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

        self.set_recalculate_voxel_grid()
        if self.display_box:
            self.draw_box()

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

    def calculate_voxelgrid(self) -> None:
        """Calculate the voxel grid."""
        assert self.aos is not None
        assert self.mos is not None

        self.voxel_grid.voxel_size = np.array(
            [
                [self.ui.voxelSizeSpinBox.value(), 0, 0],
                [0, self.ui.voxelSizeSpinBox.value(), 0],
                [0, 0, self.ui.voxelSizeSpinBox.value()],
            ],
            dtype=np.float64,
        )
        mo_coefficients = self.mos.coefficients[:, self.selected_orbital]

        self.voxel_grid.origin = self.origin
        direction = self.direction
        voxel_size = self.ui.voxelSizeSpinBox.value()
        self.voxel_grid.voxel_number = np.array(
            [
                int(self.size[0] / voxel_size) + 1,
                int(self.size[1] / voxel_size) + 1,
                int(self.size[2] / voxel_size) + 1,
            ],
            dtype=np.int64,
        )
        self.voxel_grid.voxel_size = direction * voxel_size

        # Calculate the cutoffs for the shells
        max_distance = np.linalg.norm(self.size * ANGSTROM_TO_BOHR)
        max_number = int(max_distance * 5)
        threshold = 10 ** self.ui.cutoffSpinBox.value()

        shells_cut_off = self.mos.calculate_cut_offs(
            self.aos,
            self.selected_orbital,
            threshold=threshold,
            max_distance=max_distance,
            max_points_number=max_number,
        )

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

    def change_iso_value(self) -> None:
        """Change the iso value."""
        self.set_iso_value(self.ui.isoValueSpinBox.value())
        if not self.voxel_grid_parameters_changed:
            self.visualize_surfaces()

    def visualize_orbital(self) -> None:
        """Visualize the orbital."""
        if self.voxel_grid_parameters_changed:
            self.calculate_voxelgrid()
        self.voxel_grid_parameters_changed = False
        self.set_iso_value(self.ui.isoValueSpinBox.value())
        self.visualize_surfaces()

    def run_population_analysis(self) -> None:
        """Run the population analysis to check if the calculated number of electrons matches the exact one."""
        # Use QThreadpool in the future :)
        population = PopulationAnalysis(self.parent().structure_widget.structures[0])
        self.ui.exactCountLabel.setText(str(round(population.number_of_electrons, 6)))
        self.ui.calculatedCountLabel.setText(str(round(population.calculated_number_of_electrons, 6)))
