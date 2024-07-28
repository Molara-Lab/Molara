"""Test the BuilderDialog class."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from molara.Gui.main_window import MainWindow
    from pytestqt.qtbot import QtBot


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

    def _test_init(self) -> None:
        """Test the initialization of the BuilderDialog class."""
        assert self.builder_dialog is not None
        builder_dialog = self.builder_dialog
        builder_dialog.show()
        assert builder_dialog.isVisible()

    def _test_add_atom(self) -> None:
        """Test the addition of the first atom."""
        builder_dialog = self.builder_dialog
        builder_dialog.add_atom(0, ("H", None), [])
        assert self.main_window.mols.get_current_mol().atomic_numbers == [1]

        builder_dialog.add_atom(1, ("C", 1.2), [0])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6]

        builder_dialog.add_atom(2, ("O", 1.2, 0), [1, 0])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6]
        assert builder_dialog.ui.ErrorMessageBrowser.toPlainText() == "Parameter values are not valid."
        builder_dialog.add_atom(2, ("O", 1.2, 120.0), [1, 0])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6, 8]

        builder_dialog.add_atom(3, ("Mg", 1.2, 0, 0), [2, 1, 0])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6, 8]
        assert builder_dialog.ui.ErrorMessageBrowser.toPlainText() == "Parameter values are not valid."
        builder_dialog.add_atom(2, ("Mg", 1.2, 120.0, 30.0), [2, 1, 0])  # type: ignore[arg-type]
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [1, 6, 8, 12]

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
