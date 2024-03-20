"""Test the MeasurementDialog class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from molara.Structure.structure import Structure

if TYPE_CHECKING:
    from molara.Gui.main_window import MainWindow
    from pytestqt.qtbot import QtBot


class WorkaroundTestMeasurementDialog:
    """This class contains the tests for the MainWindow class.

    It does not inherit from unittest.TestCase, because that does not work with pytest-qt.
    """

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the WorkaroundTestMainWindow object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.measurement_dialog = main_window.measurement_dialog

    def test_init(self) -> None:
        """Write test code to verify the behavior of the __init__ method."""
        # test e.g. that tablePositions is a QTableWidget,
        # has the right number of rows and columns, etc.
        measurement_dialog = self.measurement_dialog
        measurement_dialog.show()
        assert measurement_dialog.isVisible()

    def _test_position_texts(self, selected_atoms: list[int]) -> None:
        """Test the texts in the position table."""
        measurement_dialog = self.measurement_dialog
        structure = self.main_window.structure_widget.structure
        ui = measurement_dialog.ui
        for i in range(4):
            atom_id = selected_atoms[i]
            if atom_id == -1:
                assert ui.tablePositions.item(i, 0).text() == ""
                assert ui.tablePositions.item(i, 1).text() == ""
                assert ui.tablePositions.item(i, 2).text() == ""
                assert ui.tablePositions.item(i, 3).text() == ""
                assert ui.tablePositions.item(i, 4).text() == ""
                continue
            atom = structure.atoms[atom_id]
            pos = atom.position
            for k in range(3):
                assert ui.tablePositions.item(i, k + 2).text() == f"{pos[k]:.3f}"
            assert ui.tablePositions.item(i, 0).text() == atom.symbol
            assert ui.tablePositions.item(i, 1).text() == atom.name

    def _test_distance_texts(self, selected_atoms: list[int]) -> None:
        """Test the texts in the distance table."""
        ui = self.measurement_dialog.ui
        structure = self.main_window.structure_widget.structure
        for i in range(4):
            for k in range(i + 1, 4):
                atom_id1, atom_id2 = selected_atoms[i], selected_atoms[k]
                if atom_id1 == -1 or atom_id2 == -1:
                    assert ui.tableDistances.item(i, k - 1).text() == ""
                    continue
                pos1 = structure.atoms[atom_id1].position
                pos2 = structure.atoms[atom_id2].position
                distance = np.linalg.norm(pos2 - pos1)
                assert ui.tableDistances.item(i, k - 1).text()[:-2] == f"{distance:.3f}"
        for i in range(1, 3):
            for k in range(i):
                item = ui.tableDistances.item(i, k)
                assert item is None or item.text() == ""

    def _test_angle_texts(self, selected_atoms: list[int]) -> None:
        """Test the texts in the angle table."""
        ui = self.measurement_dialog.ui
        structure = self.main_window.structure_widget.structure
        for i in range(2):
            atom_id1, atom_id2, atom_id3 = selected_atoms[i], selected_atoms[i + 1], selected_atoms[i + 2]
            if atom_id1 == -1 or atom_id2 == -1 or atom_id3 == -1:
                assert ui.tableAngles.item(i, 0).text() == ""
                continue
            pos1 = structure.atoms[atom_id1].position
            pos2 = structure.atoms[atom_id2].position
            pos3 = structure.atoms[atom_id3].position
            v1 = pos1 - pos2
            v2 = pos3 - pos2
            angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
            assert ui.tableAngles.item(i, 0).text()[:-2] == f"{np.degrees(angle):.3f}"

    def _test_dihedral_texts(self, selected_atoms: list[int]) -> None:
        """Test the texts in the dihedral table."""
        ui = self.measurement_dialog.ui
        structure = self.main_window.structure_widget.structure
        dihedral_angle_item = ui.tableAngles.item(2, 0)

        atom_id1, atom_id2, atom_id3, atom_id4 = selected_atoms
        if atom_id1 == -1 or atom_id2 == -1 or atom_id3 == -1 or atom_id4 == -1:
            assert dihedral_angle_item.text() == ""
            return

        pos1 = structure.atoms[atom_id1].position
        pos2 = structure.atoms[atom_id2].position
        pos3 = structure.atoms[atom_id3].position
        pos4 = structure.atoms[atom_id4].position
        ab = pos2 - pos1
        bc = pos3 - pos2
        cd = pos4 - pos3
        # explanations on the calculation see https://math.stackexchange.com/a/47084
        n1 = np.cross(ab, bc)
        n2 = np.cross(bc, cd)
        n1 /= np.linalg.norm(n1)
        n2 /= np.linalg.norm(n2)
        m1 = np.cross(n1, bc / np.linalg.norm(bc))
        x, y = np.dot(n1, n2), np.dot(m1, n2)
        angle = np.arctan2(y, x)
        assert dihedral_angle_item.text()[:-2] == f"{np.degrees(angle):.3f}"

    def test_display_distances_angles(self) -> None:
        """Test the display_distances & display_angles methods.

        A test where a molecule has been loaded must be executed before this test!
        (see test_load_molecules in test_main_window.py)
        """
        window = self.main_window
        measurement_dialog = self.measurement_dialog

        structure = window.structure_widget.structure
        assert isinstance(structure, Structure)
        assert len(structure.atoms) >= 4  # noqa: PLR2004

        def _tests(selected_atoms: list[int]) -> None:
            measurement_dialog.display_distances(structure, selected_atoms)
            self._test_distance_texts(selected_atoms)
            self._test_position_texts(selected_atoms)

            measurement_dialog.display_angles(structure, selected_atoms)
            self._test_angle_texts(selected_atoms)

            measurement_dialog.display_dihedral(structure, selected_atoms)
            self._test_dihedral_texts(selected_atoms)

        _tests([0, -1, -1, -1])
        _tests([1, -1, 3, -1])
        _tests([-1, 2, 3, 0])
        _tests([0, 1, -1, 2])
        _tests([0, 1, 2, 3])
        _tests([3, 1, 0, 2])
