"""Module for displaying the MOs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHeaderView, QMainWindow, QTableWidgetItem
from PySide6.QtGui import QCloseEvent
from molara.gui.ui_mos_dialog import Ui_MOs_dialog
from molara.eval.marchingcubes import marching_cubes
from molara.eval.octree import octree
from molara.eval.generate_voxel_grid import generate_voxel_grid
from molara.eval.mos import calculate_mo_cartesian


if TYPE_CHECKING:
    from molara.structure.molecule import Molecule

__copyright__ = "Copyright 2024, Molara"


class MOsDialog(QDialog):
    """Dialog for displaying MOs."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Initializes the MOs dialog.

        params:
        parent: MainWindow: The widget of the MainWindow.
        """
        super().__init__(
            parent,
        )
        self.mos = None
        self.aos = None
        self.atoms = None
        self.size = np.zeros(3, dtype=np.float64)
        self.direction = np.zeros((3, 3), dtype=np.float64)
        self.origin = np.zeros(3, dtype=np.float64)
        self.box_center = np.zeros(3, dtype=np.float64)
        self.minimum_box_size = np.zeros(3, dtype=np.float64)
        self.check_if_mos()
        self.drawn_orbitals = [-1, -1]
        self.display_box = False
        self.box_spheres = -1
        self.box_cylinders = -1

        self.ui = Ui_MOs_dialog()
        self.ui.setupUi(self)
        self.ui.displayMos.clicked.connect(self.test)
        self.ui.orbitalSelector.cellClicked.connect(self.select_row)
        self.ui.toggleDisplayBoxButton.clicked.connect(self.toggle_box)
        self.ui.cubeBoxSizeSpinBox.valueChanged.connect(self.draw_box)
        # self.ui.voxelSizeSpinBox.valueChanged.connect(self.test)
        # self.ui.isoValueSpinBox.valueChanged.connect(self.test)
        self.ui.checkBoxWireMesh.clicked.connect(self.display_wire_mesh)

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

    def select_row(self):
        """When a cell is selected, select the whole row"""
        self.ui.orbitalSelector.selectRow(self.ui.orbitalSelector.currentRow())

    def setup_orbital_selector(self):
        """Set up the orbital selector."""

        def set_resize_modes(obj: QHeaderView, modes: list) -> None:
            for i, mode in enumerate(modes):
                obj.setSectionResizeMode(i, mode)

        fixed, resize, stretch = (
            QHeaderView.Fixed,
            QHeaderView.ResizeToContents,
            QHeaderView.Stretch,
        )

        # font = QFont()  # or "Monospace", "Consolas", etc.
        # font.setStyleHint(QFont.TypeWriter)
        # self.ui.orbitalSelector.setFont(font)

        self.ui.orbitalSelector.setColumnCount(2)
        self.ui.orbitalSelector.setHorizontalHeaderLabels(["Energy", "Occupation"])
        header_positions = self.ui.orbitalSelector.horizontalHeader()
        set_resize_modes(header_positions, [stretch, stretch])

    def display_wire_mesh(self):

        self.parent().structure_widget.renderer.wire_mesh_orbitals = not (
            self.parent().structure_widget.renderer.wire_mesh_orbitals
        )
        self.parent().structure_widget.update()

    def fill_orbital_selector(self):
        """Fill the orbital selector."""
        self.ui.orbitalSelector.setRowCount(len(self.mos.energies))

        # Fill the selector with energies rounded up to 3 digits and all the numbers aligned to the right
        for i, energy in enumerate(self.mos.energies):
            energy_item = QTableWidgetItem()
            energy_item.setTextAlignment(Qt.AlignRight)
            energy_item.setText(f"{energy:.3f}")
            self.ui.orbitalSelector.setItem(i, 0, energy_item)

            occupation_item = QTableWidgetItem()
            occupation_item.setTextAlignment(Qt.AlignRight)
            occupation_item.setText(f"{self.mos.occupations[i]:.3f}")
            self.ui.orbitalSelector.setItem(i, 1, occupation_item)

        self.ui.orbitalSelector.selectRow(0)

    def calculate_minimum_box_size(self):
        """Calculate the minimum box size to fit the molecular orbitals."""
        max_x = min_x = max_y = min_y = max_z = min_z = 0
        for atom in self.parent().structure_widget.structures[0].atoms:
            if atom.position[0] > max_x:
                max_x = atom.position[0]
            if atom.position[0] < min_x:
                min_x = atom.position[0]
            if atom.position[1] > max_y:
                max_y = atom.position[1]
            if atom.position[1] < min_y:
                min_y = atom.position[1]
            if atom.position[2] > max_z:
                max_z = atom.position[2]
            if atom.position[2] < min_z:
                min_z = atom.position[2]
        self.box_center = np.array(
            [(max_x + min_x) / 2, (max_y + min_y) / 2, (max_z + min_z) / 2]
        )
        self.minimum_box_size = np.array([max_x - min_x, max_y - min_y, max_z - min_z])
        self.direction = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64)
        self.scale_box()

    def scale_box(self):
        """Scale the box to fit the molecular orbitals."""
        self.size = (
            self.minimum_box_size
            + self.ui.cubeBoxSizeSpinBox.value()
            + self.initial_box_scale
        )
        self.origin = self.box_center - self.size / 2

    def closeEvent(self, event: QCloseEvent) -> None:
        """Close the dialog."""
        self.remove_orbitals()
        self.remove_box()
        self.parent().structure_widget.update()
        event.accept()

    def check_if_mos(self):
        """Check if MOs are available."""
        if not self.parent().structure_widget.structures:
            return False
        if self.parent().structure_widget.structures[0].mos.coefficients.size == 0:
            return False
        self.mos = self.parent().structure_widget.structures[0].mos
        self.aos = self.parent().structure_widget.structures[0].basis_set
        self.atoms = self.parent().structure_widget.structures[0].atoms
        return True

    def test(self):
        self.mcubes()

    def calculate_corners_of_cube(self):
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

    def toggle_box(self):
        """Toggle the cube."""
        self.display_box = not self.display_box
        if not self.display_box:
            self.remove_box()
            return
        self.draw_box()

    def remove_box(self):
        """Remove the box."""
        if self.box_spheres != -1:
            self.parent().structure_widget.renderer.remove_sphere(self.box_spheres)
            self.box_spheres = -1
        if self.box_cylinders != -1:
            self.parent().structure_widget.renderer.remove_cylinder(self.box_cylinders)
            self.box_cylinders = -1
        self.parent().structure_widget.update()

    def draw_box(self):
        """Draw the box."""
        if not self.display_box:
            return
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
        self.box_cylinders = (
            self.parent().structure_widget.renderer.draw_cylinders_from_to(
                positions,
                radii,
                colors,
                10,
            )
        )
        self.box_spheres = self.parent().structure_widget.renderer.draw_spheres(
            np.array(corners, dtype=np.float32),
            radii,
            colors,
            10,
        )
        self.parent().structure_widget.update()

    def mcubes(self):
        self.voxel_size = np.array(
            [
                [self.ui.voxelSizeSpinBox.value(), 0, 0],
                [0, self.ui.voxelSizeSpinBox.value(), 0],
                [0, 0, self.ui.voxelSizeSpinBox.value()],
            ],
            dtype=np.float64,
        )
        iso = self.ui.isoValueSpinBox.value()
        orbital = self.ui.orbitalSelector.currentRow()

        max_length = 0
        for ao in self.aos:
            if len(ao.exponents) > max_length:
                max_length = len(ao.exponents)
        orbital_exponents = np.zeros((len(self.aos), max_length), dtype=np.float64)
        orbital_coefficients = np.zeros((len(self.aos), max_length), dtype=np.float64)
        orbital_norms = np.zeros((len(self.aos), max_length), dtype=np.float64)
        orbital_positions = np.zeros((len(self.aos), 3), dtype=np.float64)
        orbital_ijks = np.zeros((len(self.aos), 3), dtype=np.int64)
        for ao_index, ao in enumerate(self.aos):
            for i in range(len(ao.exponents)):
                orbital_exponents[ao_index, i] = ao.exponents[i]
                orbital_coefficients[ao_index, i] = ao.coefficients[i]
                orbital_norms[ao_index, i] = ao.norms[i]
            orbital_positions[ao_index, :] = ao.position
            orbital_ijks[ao_index, :] = ao.ijk
        origin = self.origin
        direction = self.direction
        size = self.size
        voxel_number = np.array(
            [
                int(size[0] / self.voxel_size[0, 0]) + 1,
                int(size[1] / self.voxel_size[1, 1]) + 1,
                int(size[2] / self.voxel_size[2, 2]) + 1,
            ],
            dtype=np.int32,
        )
        mo_coefficients = self.mos.coefficients[:, orbital]
        self.parent().structure_widget.update()

        t1 = time.time()
        temp = generate_voxel_grid(
            np.array(origin, dtype=np.float64),
            direction,
            np.array(
                [self.voxel_size[0, 0], self.voxel_size[1, 1], self.voxel_size[2, 2]],
                dtype=np.float64,
            ),
            voxel_number,
            self.aos,
            mo_coefficients,
        )
        t2 = time.time()
        vertices1, vertices2 = marching_cubes(
            temp, iso, origin, self.voxel_size, voxel_number
        )
        t3 = time.time()
        print("new_voxel: ", t2 - t1)
        print("marching: ", t3 - t2)

        self.remove_orbitals()

        orb1 = self.parent().structure_widget.renderer.draw_polygon(
            vertices1, np.array([[1, 0, 0]], dtype=np.float32)
        )
        orb2 = self.parent().structure_widget.renderer.draw_polygon(
            vertices2, np.array([[0, 0, 1]], dtype=np.float32)
        )
        self.drawn_orbitals = [orb1, orb2]

    def test_function(self):
        """Test function."""

        self.mcubes()
        iso = self.ui.isoValueSpinBox.value()
        orbital = self.ui.orbitalSelector.currentRow()
        mo_coefficients = self.mos.coefficients[orbital]
        voxel_size = np.array([0.4, 0.4, 0.4], dtype=np.float64)
        octree(
            self.origin,
            voxel_size,
            self.direction,
            self.size,
            iso,
            self.aos,
            mo_coefficients,
            self.parent().structure_widget,
        )
        self.parent().structure_widget.update()

    def new_cube(
        self,
        depth,
        c1,
        iso,
        size,
        orbital_positions,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values,
    ):
        """draws 8 new cubes inside old cube defined by c1 and c2"""

        direction = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float64)
        size = size / 2
        corners = np.zeros((8, 3), dtype=np.float64)
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    new_origin = (
                        c1
                        + direction[0] * i * size[0]
                        + direction[1] * j * size[1]
                        + direction[2] * k * size[2]
                    )
                    check_inside = False
                    check_indide_num = 0
                    for l in range(8):
                        corners[l, :] = (
                            new_origin
                            + direction[0] * (l % 2) * size[0]
                            + direction[1] * ((l // 2) % 2) * size[1]
                            + direction[2] * (l // 4) * size[2]
                        )
                        if not check_inside:
                            mo_val = calculate_mo_cartesian(
                                corners[l, :] * 1.889726124565062,
                                orbital_positions * 1.889726124565062,
                                orbital_coefficients,
                                orbital_exponents,
                                orbital_norms,
                                orbital_ijks,
                                mo_coefficients,
                                aos_values,
                            )
                        if mo_val > iso:
                            check_indide_num += 1
                        if check_indide_num < 8 and check_indide_num > 0:
                            check_inside = True
                    if check_inside:
                        if depth > 0:
                            self.new_cube(
                                depth - 1,
                                corners[0],
                                iso,
                                size,
                                orbital_positions,
                                orbital_coefficients,
                                orbital_exponents,
                                orbital_norms,
                                orbital_ijks,
                                mo_coefficients,
                                aos_values,
                            )
                        else:
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
                            radius = 0.005
                            colors = np.array([0, 0, 0] * 12, dtype=np.float32)
                            radii = np.array([radius] * 12, dtype=np.float32)
                            if check_inside:
                                self.box_cylinders = self.parent().structure_widget.renderer.draw_cylinders_from_to(
                                    positions,
                                    radii,
                                    colors,
                                    10,
                                )
                                self.box_spheres = self.parent().structure_widget.renderer.draw_spheres(
                                    np.array([new_origin], dtype=np.float32),
                                    radii,
                                    colors,
                                    10,
                                )
        self.parent().structure_widget.update()

    def remove_orbitals(self):
        """Remove the drawn orbitals."""
        for orb in self.drawn_orbitals:
            if orb != -1:
                self.parent().structure_widget.renderer.remove_polygon(orb)
                self.drawn_orbitals = [-1, -1]

    def temp_MO(self) -> None:
        steps = 100
        runs = 20
        orb = 5
        step_size = 0.1
        pos = []
        vals = []
        colors = []
        radii = []

        # Metropolis run
        for run in range(runs):
            idx = np.random.randint(0, high=len(self.atoms))
            r = np.array(self.atoms[idx].position, dtype=np.float32)
            r = np.array([0, 0, 0], dtype=np.float32)
            vals.append(self.mos.get_mo_value(orb, self.aos, r))
            pos.append(r)
            if vals[-1] > 0:
                colors.append(np.array([1, 0, 0], dtype=np.float32))
            else:
                colors.append(np.array([0, 0, 1], dtype=np.float32))
            radii.append([0.1 * abs(vals[-1])])
            for i in range(steps):
                r = np.array(pos[-1]) + (np.random.rand(3) * 2 - 1) * step_size
                val = self.mos.get_mo_value(orb, self.aos, r)
                if val**2 > vals[-1] ** 2:
                    vals.append(val)
                    pos.append(r)
                else:
                    if np.random.rand() < val**2 / vals[-1] ** 2:
                        vals.append(val)
                        pos.append(r)
                    else:
                        vals.append(vals[-1])
                        pos.append(pos[-1])
                if vals[-1] > 0:
                    colors.append(np.array([1, 0, 0], dtype=np.float32))
                else:
                    colors.append(np.array([0, 0, 1], dtype=np.float32))
                radii.append([0.035 * abs(vals[-1])])

        colors = np.array(colors, dtype=np.float32)
        radii = np.array(radii, dtype=np.float32)
        pos = np.array(pos, dtype=np.float32)
        # Draw the points
        self.parent().parent().ui.openGLWidget.renderer.draw_spheres(
            pos, radii, colors, 2
        )
