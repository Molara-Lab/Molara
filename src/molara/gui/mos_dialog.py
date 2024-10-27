"""Module for displaying the MOs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent

    from molara.structure.molecularorbitals import MolecularOrbitals

from PySide6.QtWidgets import QDialog, QHeaderView, QMainWindow, QTableWidgetItem

from molara.data.constants import ANGSTROM_TO_BOHR
from molara.eval.generate_voxel_grid import generate_voxel_grid
from molara.eval.marchingcubes import marching_cubes
from molara.eval.populationanalysis import PopulationAnalysis
from molara.gui.ui_mos_dialog import Ui_MOs_dialog

__copyright__ = "Copyright 2024, Molara"


class MOsDialog(QDialog):
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
        self.aos = None
        self.atoms = None
        self.size = np.zeros(3, dtype=np.float64)
        self.direction = np.zeros((3, 3), dtype=np.float64)
        self.origin = np.zeros(3, dtype=np.float64)
        self.box_center = np.zeros(3, dtype=np.float64)
        self.minimum_box_size = np.zeros(3, dtype=np.float64)
        self.drawn_orbitals = [-1, -1]
        self.display_box = False
        self.box_spheres = -1
        self.box_cylinders = -1
        self.old_orbital = 0
        self.selected_orbital = 0
        self.number_of_alpha_orbitals = 0
        self.number_of_beta_orbitals = 0
        self.number_of_orbitals = 0
        # 0 for restricted, 1 for alpha, -1 for beta
        self.display_spin = 0

        self.ui = Ui_MOs_dialog()
        self.ui.setupUi(self)
        self.ui.displayMos.clicked.connect(self.visualize_orbital)
        self.ui.orbitalSelector.cellClicked.connect(self.select_row)
        self.ui.toggleDisplayBoxButton.clicked.connect(self.toggle_box)
        self.ui.cubeBoxSizeSpinBox.valueChanged.connect(self.draw_box)
        self.ui.checkBoxWireMesh.clicked.connect(self.toggle_wire_mesh)
        self.ui.alphaCheckBox.clicked.connect(self.select_spin_alpha)
        self.ui.betaCheckBox.clicked.connect(self.select_spin_beta)
        self.ui.normalizationButton.clicked.connect(self.run_population_analysis)

        self.initial_box_scale = 2
        scale = self.ui.cubeBoxSizeSpinBox.value() + self.initial_box_scale
        self.box_scale = np.array([scale, scale, scale], dtype=np.float64)
        self.voxel_size = np.array(
            [
                [self.ui.voxelSizeSpinBox.value(), 0, 0],
                [0, self.ui.voxelSizeSpinBox.value(), 0],
                [0, 0, self.ui.voxelSizeSpinBox.value()],
            ],
            dtype=np.float64,
        )

    def init_dialog(self) -> None:
        """Call all the functions to initialize all the labels and buttons and so on."""
        assert self.mos is not None
        self.ui.orbTypeLabel.setText(self.mos.basis_type)
        self.setup_orbital_selector()
        self.calculate_minimum_box_size()
        self.init_spin_labels()
        self.fill_orbital_selector()

    def init_spin_labels(self) -> None:
        """Initialize the labels for alpha, beta spins or a restricted calculation."""
        assert self.mos is not None
        if -1 in self.mos.spins and 1 in self.mos.spins:
            self.ui.restrictedLabel.hide()
            self.ui.alphaCheckBox.setChecked(True)
            self.ui.betaCheckBox.setChecked(False)
            self.display_spin = 1
        else:
            self.ui.restrictedLabel.setText("Restricted")
            self.ui.alphaCheckBox.hide()
            self.ui.betaCheckBox.hide()
            self.display_spin = 0

    def select_spin_alpha(self) -> None:
        """Select the spin with the checkboxes and update the displayed mos accordingly."""
        if self.ui.alphaCheckBox.isChecked():
            self.ui.betaCheckBox.setChecked(False)
        if not self.ui.alphaCheckBox.isChecked():
            self.ui.alphaCheckBox.setChecked(True)
        self.display_spin = 1
        self.fill_orbital_selector()
        self.select_row()

    def select_spin_beta(self) -> None:
        """Select the spin with the checkboxes and update the displayed mos accordingly."""
        if self.ui.betaCheckBox.isChecked():
            self.ui.alphaCheckBox.setChecked(False)
        if not self.ui.betaCheckBox.isChecked():
            self.ui.betaCheckBox.setChecked(True)
        self.display_spin = -1
        self.fill_orbital_selector()
        self.select_row()

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

    def toggle_wire_mesh(self) -> None:
        """Display the orbitals in the wire mesh mode."""
        self.parent().structure_widget.makeCurrent()
        self.parent().structure_widget.renderer.wire_mesh_orbitals = not (
            self.parent().structure_widget.renderer.wire_mesh_orbitals
        )
        self.parent().structure_widget.update()

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

    def scale_box(self) -> None:
        """Scale the box to fit the molecular orbitals."""
        self.size = self.minimum_box_size + self.ui.cubeBoxSizeSpinBox.value() + self.initial_box_scale
        self.origin = self.box_center - self.size / 2

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Close the dialog."""
        self.remove_orbitals()
        self.remove_box()
        self.parent().structure_widget.update()
        event.accept()

    def check_if_mos(self) -> bool:
        """Check if MOs are available and if so initializes the mos, aos, and atoms."""
        if not self.parent().structure_widget.structures:
            return False
        if self.parent().structure_widget.structures[0].mos.coefficients.size == 0:
            return False
        self.mos = self.parent().structure_widget.structures[0].mos
        self.aos = self.parent().structure_widget.structures[0].basis_set
        self.atoms = self.parent().structure_widget.structures[0].atoms
        return True

    def calculate_corners_of_cube(self) -> np.ndarray:
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

    def draw_box(self) -> None:
        """Draw the box."""
        self.parent().structure_widget.makeCurrent()
        self.remove_box()
        self.scale_box()
        corners = self.calculate_corners_of_cube()
        positions = np.array(
            [
                [corners[0], corners[1]],
                [corners[0], corners[2]],
                [corners[3], corners[1]],
                [corners[3], corners[2]],
                [corners[4], corners[5]],
                [corners[4], corners[6]],
                [corners[7], corners[5]],
                [corners[7], corners[6]],
                [corners[0], corners[4]],
                [corners[1], corners[5]],
                [corners[2], corners[6]],
                [corners[3], corners[7]],
            ],
            dtype=np.float32,
        )
        radius = 0.01
        colors = np.array([0, 0, 0] * 12, dtype=np.float32)
        radii = np.array([radius] * 12, dtype=np.float32)
        if not self.display_box:
            return
        self.box_cylinders = self.parent().structure_widget.renderer.draw_cylinders_from_to(
            positions,
            radii,
            colors,
            10,
        )
        self.box_spheres = self.parent().structure_widget.renderer.draw_spheres(
            np.array(corners, dtype=np.float32),
            radii,
            colors,
            10,
        )
        self.parent().structure_widget.update()

    def visualize_orbital(self) -> None:
        """Visualize the orbital."""
        self.parent().structure_widget.makeCurrent()

        assert self.aos is not None
        assert self.mos is not None
        self.voxel_size = np.array(
            [
                [self.ui.voxelSizeSpinBox.value(), 0, 0],
                [0, self.ui.voxelSizeSpinBox.value(), 0],
                [0, 0, self.ui.voxelSizeSpinBox.value()],
            ],
            dtype=np.float64,
        )

        iso = self.ui.isoValueSpinBox.value()
        mo_coefficients = self.mos.coefficients[:, self.selected_orbital]

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

        origin = self.origin
        direction = self.direction
        size = self.size
        voxel_number = np.array(
            [
                int(size[0] / self.voxel_size[0, 0]) + 1,
                int(size[1] / self.voxel_size[1, 1]) + 1,
                int(size[2] / self.voxel_size[2, 2]) + 1,
            ],
            dtype=np.int64,
        )
        voxel_grid = np.array(
            generate_voxel_grid(
                np.array(origin, dtype=np.float64),
                direction,
                np.array(
                    [self.voxel_size[0, 0], self.voxel_size[1, 1], self.voxel_size[2, 2]],
                    dtype=np.float64,
                ),
                voxel_number,
                self.aos,
                mo_coefficients,
                shells_cut_off,
            ),
        )

        # 24 because each voxel can have up to 12 vertices and 12 normals
        # times 6 because each vertex has 3 coordinates and each normal has 3 coordinates
        # The +1 is to save the number of vertices in the marching cubes routine.
        max_vertices = 24 * (voxel_number[0] - 1) * (voxel_number[1] - 1) * (voxel_number[2] - 1) * 6 + 1
        vertices1 = np.zeros(max_vertices, dtype=np.float32)
        vertices2 = np.zeros(max_vertices, dtype=np.float32)

        _ = marching_cubes(
            voxel_grid,
            iso,
            origin,
            np.array([self.voxel_size[0, 0], self.voxel_size[1, 1], self.voxel_size[2, 2]], dtype=np.float64),
            voxel_number,
            vertices1,
            vertices2,
        )

        # Get the number of vertices from the last entry, to shrink the memory usage
        number_of_vertices_entries_1 = int(vertices1[-1])
        number_of_vertices_entries_2 = int(vertices2[-1])
        vertices1 = vertices1[:number_of_vertices_entries_1]
        vertices2 = vertices2[:number_of_vertices_entries_2]

        self.remove_orbitals()
        orb1 = self.parent().structure_widget.renderer.draw_polygon(
            vertices1,
            np.array([[1, 0, 0]], dtype=np.float32),
        )
        orb2 = self.parent().structure_widget.renderer.draw_polygon(
            vertices2,
            np.array([[0, 0, 1]], dtype=np.float32),
        )
        self.drawn_orbitals = [orb1, orb2]
        self.parent().structure_widget.update()

    def remove_orbitals(self) -> None:
        """Remove the drawn orbitals."""
        self.parent().structure_widget.makeCurrent()
        for orb in self.drawn_orbitals:
            if orb != -1:
                self.parent().structure_widget.renderer.remove_polygon(orb)
        self.drawn_orbitals = [-1, -1]

    def run_population_analysis(self) -> None:
        """Run the population analysis to check if the calculated number of electrons matches the exact one."""
        # Use QThreadpool in the future :)
        population = PopulationAnalysis(self.parent().structure_widget.structures[0])
        self.ui.exactCountLabel.setText(str(round(population.number_of_electrons, 8)))
        self.ui.calculatedCountLabel.setText(str(round(population.calculated_number_of_electrons, 8)))
