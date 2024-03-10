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
        """Instantiates the WorkaroundTestMainWindow object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.measurement_dialog = main_window.measurement_dialog

    # def test_init(self) -> None:
    #     """Write test code to verify the behavior of the __init__ method."""
    #     # test e.g. that tablePositions is a QTableWidget,
    #     # has the right number of rows and columns, etc.

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
                assert ui.tablePositions.item(i, k + 2).text()[:5] == f"{pos[k]:.3f}"[:5]
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
                assert ui.tableDistances.item(i, k - 1).text()[:5] == f"{distance:.3f}"
        for i in range(1, 3):
            for k in range(i):
                item = ui.tableDistances.item(i, k)
                assert item is None or item.text() == ""

    def test_display_distances(self) -> None:
        """Test the display_distances method.

        A test where a molecule has been loaded must be executed before this test!
        (see test_load_molecules in test_main_window.py)
        """
        window = self.main_window
        measurement_dialog = self.measurement_dialog
        measurement_dialog.show()
        assert measurement_dialog.isVisible()

        structure = window.structure_widget.structure
        assert isinstance(structure, Structure)
        assert len(structure.atoms) >= 4  # noqa: PLR2004

        atoms_selected = [0, -1, -1, -1]
        measurement_dialog.display_distances(structure, atoms_selected)
        self._test_distance_texts(atoms_selected)
        self._test_position_texts(atoms_selected)

        atoms_selected = [1, -1, 3, -1]
        measurement_dialog.display_distances(structure, atoms_selected)
        self._test_distance_texts(atoms_selected)
        self._test_position_texts(atoms_selected)

        atoms_selected = [-1, 2, 3, 0]
        measurement_dialog.display_distances(structure, atoms_selected)
        self._test_distance_texts(atoms_selected)
        self._test_position_texts(atoms_selected)

        atoms_selected = [0, 1, -1, 2]
        measurement_dialog.display_distances(structure, atoms_selected)
        self._test_distance_texts(atoms_selected)
        self._test_position_texts(atoms_selected)

        atoms_selected = [0, 1, 2, 3]
        measurement_dialog.display_distances(structure, atoms_selected)
        self._test_distance_texts(atoms_selected)
        self._test_position_texts(atoms_selected)

        atoms_selected = [3, 1, 0, 2]
        measurement_dialog.display_distances(structure, atoms_selected)
        self._test_distance_texts(atoms_selected)
        self._test_position_texts(atoms_selected)
