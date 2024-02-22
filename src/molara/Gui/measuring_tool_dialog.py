"""Module for the measuring tool dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
)

from molara.Gui.ui_measuring_tool import Ui_measuring_tool

if TYPE_CHECKING:
    from molara.Structure.structure import Structure

__copyright__ = "Copyright 2024, Molara"


class MeasurementDialog(QDialog):
    """Dialog for displaying measurements."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Initializes the measurement dialog.

        :param parent: the MainWindow widget
        """
        super().__init__(
            parent,
        )

        self.ui = Ui_measuring_tool()
        self.ui.setupUi(self)

    def ini_labels(self) -> None:
        """Initializes the labels."""
        self.ui.info_text.setText("Use SHIFT + Left Mouse Button to select atoms.")
        self.ui.atom1.setText("")
        self.ui.atom2.setText("")
        self.ui.atom3.setText("")
        self.ui.atom4.setText("")
        self.ui.x1.setText("")
        self.ui.y1.setText("")
        self.ui.z1.setText("")
        self.ui.x2.setText("")
        self.ui.y2.setText("")
        self.ui.z2.setText("")
        self.ui.x3.setText("")
        self.ui.y3.setText("")
        self.ui.z3.setText("")
        self.ui.x4.setText("")
        self.ui.y4.setText("")
        self.ui.z4.setText("")
        self.ui.d12.setText("")
        self.ui.d23.setText("")
        self.ui.d34.setText("")
        self.ui.a123.setText("")
        self.ui.a234.setText("")
        self.ui.d1234.setText("")

    def display_metrics(self, structure: Structure, selected_atoms: list) -> None:
        """Display the metrics in the table.

        :param structure: The structure to measure.
        :param selected_atoms: The selected atoms.
        :return:
        """
        self.display_distances(structure, selected_atoms)
        self.display_angles(structure, selected_atoms)
        self.display_dihedral(structure, selected_atoms)

    def display_distances(self, structure: Structure, selected_atoms: list) -> None:
        """Display the distances in the table.

        :param structure: The structure to measure.
        :param selected_atoms: The selected atoms.
        :return:
        """
        atom_labels = [self.ui.atom1, self.ui.atom2, self.ui.atom3, self.ui.atom4]
        atom_coordinates = [
            [self.ui.x1, self.ui.y1, self.ui.z1],
            [self.ui.x2, self.ui.y2, self.ui.z2],
            [self.ui.x3, self.ui.y3, self.ui.z3],
            [self.ui.x4, self.ui.y4, self.ui.z4],
        ]
        distances = [self.ui.d12, self.ui.d23, self.ui.d34]
        for i in range(len(selected_atoms)):
            if selected_atoms[i] == -1:
                atom_labels[i].setText("")
                for j in range(3):
                    atom_coordinates[i][j].setText("")
            else:
                atom_labels[i].setText(structure.atoms[selected_atoms[i]].symbol)
                for j in range(3):
                    atom_coordinates[i][j].setText(
                        f"{structure.atoms[selected_atoms[i]].position[j].round(3):.3f}",
                    )
        for i in range(3):
            if selected_atoms[i] != -1 and selected_atoms[i + 1] != -1:
                d = np.linalg.norm(
                    structure.atoms[selected_atoms[i]].position - structure.atoms[selected_atoms[i + 1]].position,
                )
                distances[i].setText(f"{d.round(3):.3f}")
            else:
                distances[i].setText("")

    def display_angles(self, structure: Structure, selected_atoms: list) -> None:
        """Display the angles in the table.

        :param structure: The structure to measure.
        :param selected_atoms: The selected atoms.
        :return:
        """
        angles = [self.ui.a123, self.ui.a234]
        for i in range(2):
            if selected_atoms[i] != -1 and selected_atoms[i + 1] != -1 and selected_atoms[i + 2] != -1:
                v1 = structure.atoms[selected_atoms[i]].position - structure.atoms[selected_atoms[i + 1]].position
                v2 = structure.atoms[selected_atoms[i + 2]].position - structure.atoms[selected_atoms[i + 1]].position
                a = np.arccos(
                    np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)),
                )
                angles[i].setText(f"{np.degrees(a).round(1):.3f}")
            else:
                angles[i].setText("")

    def display_dihedral(self, structure: Structure, selected_atoms: list) -> None:
        """Display the dihedral in the table.

        :param structure: The structure to measure.
        :param selected_atoms: The selected atoms.
        :return:
        """
        dihedral = self.ui.d1234
        if selected_atoms[0] != -1 and selected_atoms[1] != -1 and selected_atoms[2] != -1 and selected_atoms[3] != -1:
            ab = structure.atoms[selected_atoms[1]].position - structure.atoms[selected_atoms[0]].position
            bc = structure.atoms[selected_atoms[2]].position - structure.atoms[selected_atoms[1]].position
            cd = structure.atoms[selected_atoms[3]].position - structure.atoms[selected_atoms[2]].position
            nabc = np.cross(ab, bc)
            nbcd = np.cross(bc, cd)
            t = np.cross(nabc, bc)
            a = np.arctan2(np.dot(t, nbcd), np.dot(nabc, nbcd))
            a_deg = np.degrees(a)
            if a_deg > 0:
                a_deg = a_deg - 360
            a_deg = -a_deg
            dihedral.setText(f"{a_deg.round(1):.3f}")
        else:
            dihedral.setText("")
