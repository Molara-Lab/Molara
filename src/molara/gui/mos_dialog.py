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
from molara.eval.marchingsquares import marching_squares
from molara.eval.populationanalysis import PopulationAnalysis
from molara.eval.voxel_grid import VoxelGrid2D
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

        # Isoline parameters
        self.isoline_drawn_lines = [-1, -1]
        self.isoline_voxel_grid = VoxelGrid2D()
        self.isoline_grid_parameters_changed = True
        self.isolines_1: np.ndarray = np.array([])
        self.isolines_2: np.ndarray = np.array([])
        self.isoline_origin: np.ndarray = np.array([])
        self.isoline_size: np.ndarray = np.array([])
        self.isoline_direction: np.ndarray = np.array([])
        self.isoline_border_cylinders = -1
        self.isoline_border_spheres = -1
        self.isoline_border_points: np.ndarray = np.array([])
        self.border_is_visible = False

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

        # isoline ui connections
        self.ui.displayIsolinesButton.clicked.connect(self.visualize_isolines)
        self.ui.numberLinesSpinBox.valueChanged.connect(self.change_number_of_lines)
        self.ui.isolineVoxelSizeSpinBox.valueChanged.connect(self.set_recalculate_isoline_grid)
        self.ui.displayIsolineBorderButton.clicked.connect(self.toggle_isoline_border)

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
        self.set_recalculate_isoline_grid()

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
        self.remove_isolines()
        self.remove_isoline_border()

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

    def calculate_cutoffs(self) -> np.ndarray:
        """Calculate the cutoffs for the shells."""
        assert self.aos is not None
        assert self.mos is not None
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

    def set_recalculate_isoline_grid(self) -> None:
        """Set a flag to recalculate the isoline grid."""
        self.isoline_grid_parameters_changed = True

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

    def set_isoline_border_points(self) -> None:
        """Set the points of the border that can be displayed as a guide to the eye."""
        assert self.isoline_origin is not None
        assert self.isoline_size is not None
        assert self.isoline_direction is not None
        self.isoline_border_points = np.array(
            [
                self.isoline_origin,
                self.isoline_origin + self.isoline_size[0] * self.isoline_direction[0],
                self.isoline_origin + self.isoline_size[1] * self.isoline_direction[1],
                self.isoline_origin + self.isoline_size[0] * self.isoline_direction[0] + self.isoline_size[1] * self.isoline_direction[1],
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
        self.border_is_visible = not self.border_is_visible
        if self.border_is_visible:
            self.display_isoline_border()
            self.ui.displayIsolineBorderButton.setText("Hide Border")
            return
        self.remove_isoline_border()
        self.ui.displayIsolineBorderButton.setText("Display Border")

    def calculate_isoline_voxelgrid(self) -> None:
        """Calculate the 2D voxel grid for the isolines."""
        assert self.aos is not None
        assert self.mos is not None

        direction = np.array([[0, 1, 0], [0, 0, 1], [0, 0, 0]], dtype=np.float64)
        origin = np.array([0, -2, -2], dtype=np.float64)
        size = np.array([4, 4], dtype=np.float64)

        self.isoline_origin = origin
        self.isoline_size = size
        self.isoline_direction = direction

        voxel_size = direction * self.ui.isolineVoxelSizeSpinBox.value()

        mo_coefficients = self.mos.coefficients[:, self.selected_orbital]

        voxel_number = np.array(
            [
                int(size[0] / self.ui.isolineVoxelSizeSpinBox.value()) + 1,
                int(size[1] / self.ui.isolineVoxelSizeSpinBox.value()) + 1,
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

    def visualize_isolines(self) -> None:
        """Calculate the voxel grid."""
        assert self.aos is not None
        assert self.mos is not None
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
        if grid_sum > 1.e-14:
            log_grid_max = np.log(np.max(np.abs(grid)))
            log_grid_min = np.log(max(np.min(np.abs(grid)), 5e-3))
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

    def draw_isolines(self) -> None:
        """Draw the isolines."""
        self.parent().structure_widget.makeCurrent()
        self.remove_isolines()
        radii_1 = np.array([0.003] * self.isolines_1.shape[0], dtype=np.float32)
        colors_1 = np.array(list(self.color_surface_1 / 255) * self.isolines_1.shape[0], dtype=np.float32)
        radii_2 = np.array([0.003] * self.isolines_2.shape[0], dtype=np.float32)
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

    def isolines_are_initialized(self) -> bool:
        """Check if the isolines are initialized."""
        return self.isolines_1.size != 0 or self.isolines_2.size != 0

    def display_isolines(self) -> None:
        """Display the isolines."""
        if self.isolines_are_initialized():
            self.draw_isolines()
        else:
            self.visualize_isolines()
