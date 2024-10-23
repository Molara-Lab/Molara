"""Test the BuilderDialog class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from numpy import deg2rad

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    from molara.gui.main_window import MainWindow


class WorkaroundTestBuilderDialog:
    """Contains the tests for the BuilderDialog class.

    It does not inherit from unittest.TestCase, because that does not work with pytest-qt.
    """

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the WorkaroundTestBuilderDialog object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.builder_dialog = main_window.builder_dialog

    def run_tests(self) -> None:
        """Run the tests."""
        self._test_init()
        self._test_add_atom()
        self._test_select_add()
        self._test_delete_atom()
        self._test_check_selected_atoms()

    def _test_init(self) -> None:
        """Test the initialization of the BuilderDialog class."""
        assert self.builder_dialog is not None
        builder_dialog = self.builder_dialog
        builder_dialog.show()
        assert builder_dialog.isVisible()

    def _test_add_atom(self) -> None:
        """Test the addition of the first atom."""
        builder_dialog = self.builder_dialog
        angle120 = deg2rad(120.0)
        builder_dialog.exec_add_atom(0, ("H", None), [])
        assert self.main_window.mols.get_current_mol().atomic_numbers == [1]

        builder_dialog.exec_add_atom(1, ("C", 1.2), [0])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6]

        builder_dialog.exec_add_atom(2, ("O", 1.2, 0), [1, 0])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6]
        assert builder_dialog.ui.ErrorMessageBrowser.toPlainText() == "Parameter values are not valid."
        builder_dialog.exec_add_atom(2, ("O", 1.2, angle120), [1, 0])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6, 8]

        builder_dialog.exec_add_atom(3, ("Mg", 1.2, 0, 0), [2, 1, 0])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6, 8]
        assert builder_dialog.ui.ErrorMessageBrowser.toPlainText() == "Parameter values are not valid."
        builder_dialog.exec_add_atom(3, ("Mg", 1.2, angle120, 0.0), [2, 1, 0])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6, 8, 12]

        builder_dialog.exec_add_atom(4, ("F", 1.2, angle120, 0.0), [3, 2, 1])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6, 8, 12, 9]

        builder_dialog.exec_add_atom(5, ("B", 1.2, angle120, 0.0), [4, 3, 2])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6, 8, 12, 9, 5]

        builder_dialog.exec_add_atom(6, ("H", 1.2, angle120, 0.0), [5, 4, 3])  # type: ignore[arg-type]
        assert builder_dialog.ui.ErrorMessageBrowser.toPlainText() == "The atom would collide with atom 1."
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6, 8, 12, 9, 5]
        builder_dialog.exec_add_atom(6, ("H", 1.2, angle120, 30.0), [5, 4, 3])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6, 8, 12, 9, 5, 1]

        structure = builder_dialog.structure_widget.structures[0]
        assert structure is not None
        assert structure.atoms[0].symbol == "H"
        assert structure.atoms[1].symbol == "C"
        assert structure.atoms[2].symbol == "O"
        assert structure.atoms[3].symbol == "Mg"

    def _test_select_add(self) -> None:
        """Test the selection of the add button."""
        builder_dialog = self.builder_dialog
        builder_dialog.select_add()
        assert builder_dialog.err is True
        assert builder_dialog.colliding_idx is None

    def _test_delete_atom(self) -> None:
        """Test the deletion of an atom."""
        builder_dialog = self.builder_dialog
        builder_dialog.delete_atom()
        assert builder_dialog.ui.ErrorMessageBrowser.toPlainText() == "No Atom was chosen to be deleted."

    def _test_check_selected_atoms(self) -> None:
        """Test the check of selected atoms."""
        builder_dialog = self.builder_dialog
        builder_dialog.err = False
        builder_dialog.ui.ErrorMessageBrowser.clear()

        assert builder_dialog._check_selected_atoms(17, 100, 611)  # noqa: SLF001
        assert not builder_dialog.err
        assert builder_dialog.ui.ErrorMessageBrowser.toPlainText() == ""

        error_message = "Not enough atoms selected."
        assert not builder_dialog._check_selected_atoms(-1, -1, 611)  # noqa: SLF001
        assert builder_dialog.err
        assert builder_dialog.ui.ErrorMessageBrowser.toPlainText() == error_message
        builder_dialog.err = False
        builder_dialog.ui.ErrorMessageBrowser.clear()
