"""Module for displaying the isolines of the MOs."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent

    from molara.structure.atom import Atom
    from molara.structure.basisset import BasisFunction
    from molara.structure.molecularorbitals import MolecularOrbitals

from PySide6.QtWidgets import QHeaderView, QMainWindow, QTableWidgetItem, QDialog

from molara.eval.populationanalysis import PopulationAnalysis
from molara.eval.generate_voxel_grid import generate_voxel_grid
from molara.eval.marching_squares import marching_squares
from molara.gui.surface_3d import Surface3DDialog
from molara.gui.ui_isoline_dialog import Ui_isoline_dialog
from molara.util.constants import ANGSTROM_TO_BOHR
import time

__copyright__ = "Copyright 2024, Molara"


class IsolineMOsDialog(Surface3DDialog):
    """Dialog for displaying isolines for the MOs."""

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
        self.grid = np.array([])

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
        self.ui = Ui_isoline_dialog()
        self.ui.setupUi(self)
        self.ui.displayMos.clicked.connect(self.visualize_orbital)
        self.ui.orbitalSelector.cellClicked.connect(self.select_row)
        self.ui.alphaCheckBox.clicked.connect(self.select_spin_alpha)
        self.ui.betaCheckBox.clicked.connect(self.select_spin_beta)
        self.ui.normalizationButton.clicked.connect(self.run_population_analysis)

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

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Close the dialog."""
        super().closeEvent(event)

    def calculate_voxelgrid(self) -> None:
        """Calculate the voxel grid."""
        assert self.aos is not None
        assert self.mos is not None
        number_of_isos = 15
        start_iso = 2.0
        isos = [start_iso / 2 ** i for i in range(1, number_of_isos + 1)]
        voxel_size = 0.02
        origin = np.array([0, -2, -2], dtype=np.float64)
        direction = np.array(
            [
                [0, 1, 0],
                [0, 0, 1],
                [1, 0, 0]
            ],
            dtype=np.float64,
        )
        size = np.array([4, 4], dtype=np.float64)
        voxel_number = np.array([
            int(size[0] / voxel_size) + 1,
            int(size[1] / voxel_size) + 1,
            1,
        ], dtype=np.int64)
        voxel_size = direction * voxel_size

        # Calculate the cutoffs for the shells
        max_distance = np.linalg.norm(size * ANGSTROM_TO_BOHR)
        max_number = int(max_distance * 5)
        threshold = 10 ** (-5)

        shells_cut_off = self.mos.calculate_cut_offs(
            self.aos,
            self.selected_orbital,
            threshold=threshold,
            max_distance=max_distance,
            max_points_number=max_number,
        )
        mo_coefficients = self.mos.coefficients[:, self.selected_orbital]

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


        for iso in isos:
            lines_1 = np.zeros(((voxel_number[0] - 1) * (voxel_number[1] - 1) * 4 + 1, 3), dtype=np.float32)
            lines_2 = np.zeros(((voxel_number[0] - 1) * (voxel_number[1] - 1) * 4 + 1, 3), dtype=np.float32)
            _ = marching_squares(grid,iso, origin, voxel_size, voxel_number, lines_1, lines_2)
            number_of_lines_entries_1 = int(lines_1[-1, -1])
            number_of_lines_entries_2 = int(lines_2[-1, -1])
            if number_of_lines_entries_1 != 0:
                lines_1 = lines_1[:number_of_lines_entries_1]
                lines_1 = lines_1.reshape((number_of_lines_entries_1 // 2, 2, 3))
                radii_1 = np.array([0.001] * number_of_lines_entries_1, dtype=np.float32)
                colors_1 = np.array([1, 0, 0] * number_of_lines_entries_1, dtype=np.float32)
                self.parent().structure_widget.renderer.draw_cylinders_from_to(lines_1, radii_1, colors_1, 10)
            if number_of_lines_entries_2 != 0:
                lines_2 = lines_2[:number_of_lines_entries_2]
                lines_2 = lines_2.reshape((number_of_lines_entries_2 // 2, 2, 3))
                radii_2 = np.array([0.001] * number_of_lines_entries_2, dtype=np.float32)
                colors_2 = np.array([0, 0, 1] * number_of_lines_entries_2, dtype=np.float32)
                self.parent().structure_widget.renderer.draw_cylinders_from_to(lines_2, radii_2, colors_2, 10)
        self.parent().structure_widget.update()

    def change_iso_value(self) -> None:
        """Change the iso value."""
        self.set_iso_value(self.ui.isoValueSpinBox.value())
        if not self.voxel_grid_parameters_changed:
            self.visualize_surfaces()

    def visualize_orbital(self) -> None:
        """Visualize the orbital."""
        if self.voxel_grid_parameters_changed:
            self.calculate_voxelgrid()

    def run_population_analysis(self) -> None:
        """Run the population analysis to check if the calculated number of electrons matches the exact one."""
        # Use QThreadpool in the future :)
        population = PopulationAnalysis(self.parent().structure_widget.structures[0])
        self.ui.exactCountLabel.setText(str(round(population.number_of_electrons, 6)))
        self.ui.calculatedCountLabel.setText(str(round(population.calculated_number_of_electrons, 6)))
