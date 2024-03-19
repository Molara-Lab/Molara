"""Module for displaying the MOs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import time
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
)

from molara.Gui.ui_mos_dialog import Ui_MOs_dialog
from molara.Eval.marchingcubes import marching_cubes
from molara.Eval.mos import calculate_mo_cartesian
from molara.Eval.generate_voxel_grid import generate_voxel_grid

if TYPE_CHECKING:
    from molara.Molecule.structure import Structure

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
        self.ui.pushButton.clicked.connect(self.test)
        self.check_if_mos()

    def check_if_mos(self):
        """Check if MOs are available."""
        if self.parent().structure_widget.structure is None:
            return False
        if self.parent().structure_widget.structure.mos.coefficients.size == 0:
            return False
        self.mos = self.parent().structure_widget.structure.mos
        self.aos = self.parent().structure_widget.structure.aos
        self.atoms = self.parent().structure_widget.structure.atoms
        return True

    def test(self):
        self.check_if_mos()
        self.mcubes()

    def mcubes(self):
        iso = 0.08
        orbital = 16

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
        origin = np.array([-1, -1, -1.5])
        direction = np.array([[1, 0, 0],
                                 [0, 1, 0],
                                [0, 0, 1],], dtype=np.float64)
        size = np.array([5, 2, 5])
        voxel_number = np.array([30, 12, 30], dtype=np.int32)
        # origin = np.array([-1.2, -1.2, -2.4])
        # direction = np.array(
        #     [
        #         [1, 0, 0],
        #         [0, 1, 0],
        #         [0, 0, 1],
        #     ],
        #     dtype=np.float64,
        # )
        # size = np.array([2.4, 2.4, 4.8])
        # voxel_number = np.array([20,20,40], dtype=np.int32)

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

        print(voxel_size_)

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
        self.parent().structure_widget.renderer.draw_polygon(
            vertices1, np.array([[1, 0, 0]], dtype=np.float32)
        )
        self.parent().structure_widget.renderer.draw_polygon(
            vertices2, np.array([[0, 0, 1]], dtype=np.float32)
        )

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
