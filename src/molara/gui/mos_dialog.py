"""Module for displaying the MOs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import time

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHeaderView, QMainWindow, QTableWidget, QTableWidgetItem
from molara.gui.ui_mos_dialog import Ui_MOs_dialog
from molara.eval.marchingcubes import marching_cubes
from molara.eval.generate_voxel_grid import generate_voxel_grid

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
        self.ui = Ui_MOs_dialog()
        self.ui.setupUi(self)
        self.ui.displayMos.clicked.connect(self.test)
        self.ui.orbitalSelector.cellClicked.connect(self.select_row)
        self.check_if_mos()
        self.drawn_orbitals = [-1, -1]
        self.origin = np.array([-1, -1, -1.5])
        self.direction = np.array([[1, 0, 0],
                                 [0, 1, 0],
                                [0, 0, 1],], dtype=np.float64)
        self.size = np.array([2, 2, 3])
        self.draw_cube()
    def select_row(self):
        """When a cell is selected, select the whole row"""
        self.ui.orbitalSelector.selectRow(self.ui.orbitalSelector.currentRow())

    def setup_orbital_selector(self):
        """Set up the orbital selector."""
        def set_resize_modes(obj: QHeaderView, modes: list) -> None:
            for i, mode in enumerate(modes):
                obj.setSectionResizeMode(i, mode)
        fixed, resize, stretch = QHeaderView.Fixed, QHeaderView.ResizeToContents, QHeaderView.Stretch

        # font = QFont()  # or "Monospace", "Consolas", etc.
        # font.setStyleHint(QFont.TypeWriter)
        # self.ui.orbitalSelector.setFont(font)

        self.ui.orbitalSelector.setColumnCount(2)
        self.ui.orbitalSelector.setHorizontalHeaderLabels(["Energy", "Occupation"])
        header_positions = self.ui.orbitalSelector.horizontalHeader()
        set_resize_modes(header_positions, [stretch, stretch])

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


    def check_if_mos(self):
        """Check if MOs are available."""
        if not self.parent().structure_widget.structures:
            return False
        if self.parent().structure_widget.structures[0].mos.coefficients.size == 0:
            return False
        self.mos = self.parent().structure_widget.structures[0].mos
        self.aos = self.parent().structure_widget.structures[0].aos
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
            corners[i, :] = origin + direction[0] * (i % 2) * size[0] + direction[1] * (
                (i // 2) % 2
            ) * size[1] + direction[2] * (i // 4) * size[2]
        return corners

    def draw_cube(self):
        corners = self.calculate_corners_of_cube()
        positions = np.array([[corners[0], corners[1]],
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
                    [corners[3], corners[7]]], dtype=np.float32)
        radius = 0.01
        colors = np.array([0, 0, 0] * 12, dtype=np.float32)
        radii = np.array([radius] * 12, dtype=np.float32)
        self.parent().structure_widget.renderer.draw_cylinders_from_to(
            positions,
            radii,
            colors,
            10,
        )
        self.parent().structure_widget.renderer.draw_spheres(
            np.array(corners, dtype=np.float32),
            radii,
            colors,
            10,
        )
        self.parent().structure_widget.update()

    def mcubes(self):
        iso = 0.09
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
        voxel_number = np.array([30, 30, 40], dtype=np.int32)
        voxel_size = np.array(
            [
                [size[0] / (voxel_number[0] - 1), 0, 0],
                [0, size[1] / (voxel_number[1] - 1), 0],
                [0, 0, size[2] / (voxel_number[2] - 1)],
            ]
        )
        voxel_size_ = np.array(
            [
                size[0] / (voxel_number[0] - 1),
                size[1] / (voxel_number[1] - 1),
                size[2] / (voxel_number[2] - 1),
            ],
            dtype=np.float64,
        )
        mo_coefficients = self.mos.coefficients[orbital]
        self.parent().structure_widget.update()

        t1 = time.time()
        temp = generate_voxel_grid(
            np.array(origin, dtype=np.float64),
            direction,
            voxel_size_,
            voxel_number,
            self.aos,
            mo_coefficients,
        )
        t2 = time.time()
        vertices1, vertices2 = marching_cubes(
            temp, iso, origin, voxel_size, voxel_number
        )
        t3 = time.time()
        print("new_voxel: ", t2 - t1)
        print("marching: ", t3 - t2)

        for orb in self.drawn_orbitals:
            if orb != -1:
                self.parent().structure_widget.renderer.remove_polygon(orb)

        orb1 = self.parent().structure_widget.renderer.draw_polygon(
            vertices1, np.array([[1, 0, 0]], dtype=np.float32)
        )
        orb2 = self.parent().structure_widget.renderer.draw_polygon(
            vertices2, np.array([[0, 0, 1]], dtype=np.float32)
        )
        self.drawn_orbitals = [orb1, orb2]

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
