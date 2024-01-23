"""Module for displaying the MOs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
)

from molara.Gui.ui_mos_dialog import Ui_MOs_dialog

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
        print(self.parent().parent().mols)
        if self.parent().parent().mols is None:
            return False
        print(self.parent().parent().mols.get_current_mol())
        if self.parent().parent().mols.get_current_mol().mos.coefficients.size == 0:
            return False
        self.mos = self.parent().parent().mols.get_current_mol().mos
        self.aos = self.parent().parent().mols.get_current_mol().aos
        self.atoms = self.parent().parent().mols.get_current_mol().atoms
        return True

    def test(self):
        print('lmao')
        self.mcubes()

    def mcubes(self):

        cube_size = np.array([1, 1, 3])
        resolution = np.array([10, 10, 10])
        cube = np.zeros(resolution)
        for i in range(resolution[0]):
            print(i)
            for j in range(resolution[1]):
                for k in range(resolution[2]):
                    cube[i, j, k] = self.mos.calculate_mo_cartesian(5,
                                                                    self.aos,
                                                                    np.array([i, j, k]) /
                                                                    resolution * cube_size - cube_size / 2)
        print(cube)


    def temp_MO(self) -> None:

        steps = 10000
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
            print(run, idx)
            vals.append(self.mos.calculate_mo_cartesian(orb, self.aos,r))
            pos.append(r)
            if vals[-1] > 0:
                colors.append(np.array([1, 0, 0], dtype=np.float32))
            else:
                colors.append(np.array([0, 0, 1], dtype=np.float32))
            radii.append([0.1 * abs(vals[-1])])
            for i in range(steps):
                r = np.array(pos[-1]) + (np.random.rand(3) * 2 - 1) * step_size
                val = self.mos.calculate_mo_cartesian(orb,
                                                          self.aos,
                                                          r)
                #print(i, val ,r)
                if val**2 > vals[-1]**2:
                    vals.append(val)
                    pos.append(r)
                else:
                    if np.random.rand() < val**2 / vals[-1]**2:
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
        self.parent().parent().ui.openGLWidget.renderer.draw_spheres(pos, radii, colors, 2)

