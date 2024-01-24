"""Module for displaying the MOs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
)

from molara.Gui.ui_mos_dialog import Ui_MOs_dialog
from molara.Eval.marchingcubes import marching_cubes

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

    def check_if_mos(self):
        """Check if MOs are available."""
        if self.parent().parent().mols is None:
            return False
        if self.parent().parent().mols.get_current_mol().mos.coefficients.size == 0:
            return False
        self.mos = self.parent().parent().mols.get_current_mol().mos
        self.aos = self.parent().parent().mols.get_current_mol().aos
        self.atoms = self.parent().parent().mols.get_current_mol().atoms
        return True

    def test(self):
        self.mcubes()

    def mcubes(self):
        iso = 0.2
        origin = np.array([-0.5, -0.5, -1.5])
        size = -2 * origin.copy()
        voxel_number = np.array([20, 20, 50])
        voxel_size = np.array(
            [
                [size[0] / (voxel_number[0] - 1), 0, 0],
                [0, size[1] / (voxel_number[1] - 1), 0],
                [0, 0, size[2] / (voxel_number[2] - 1)],
            ]
        )
        self.parent().parent().ui.openGLWidget.update()
        cube = np.zeros(voxel_number)
        for i in range(voxel_number[0]):
            for j in range(voxel_number[1]):
                for k in range(voxel_number[2]):
                    position = origin + np.array([i, j, k]) * size / (
                        voxel_number - np.array([1, 1, 1])
                    )
                    cube[i, j, k] = self.mos.calculate_mo_cartesian(
                        5, self.aos, position
                    )
        vertices1, vertices2 = marching_cubes(
            cube, iso, origin, voxel_size, voxel_number
        )
        self.parent().parent().ui.openGLWidget.renderer.draw_polygon(
            vertices1, np.array([[1, 0, 0]], dtype=np.float32)
        )
        self.parent().parent().ui.openGLWidget.renderer.draw_polygon(
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
            vals.append(self.mos.calculate_mo_cartesian(orb, self.aos, r))
            pos.append(r)
            if vals[-1] > 0:
                colors.append(np.array([1, 0, 0], dtype=np.float32))
            else:
                colors.append(np.array([0, 0, 1], dtype=np.float32))
            radii.append([0.1 * abs(vals[-1])])
            for i in range(steps):
                r = np.array(pos[-1]) + (np.random.rand(3) * 2 - 1) * step_size
                val = self.mos.calculate_mo_cartesian(orb, self.aos, r)
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
