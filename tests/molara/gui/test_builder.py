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
        self._test_select_add()
        self._test_delete_atom()
        self._test_current_mol()
        self._test_add_first_atom()

    def _test_init(self) -> None:
        """Test the initialization of the BuilderDialog class."""
        assert self.builder_dialog is not None
        builder_dialog = self.builder_dialog
        builder_dialog.show()
        assert builder_dialog.isVisible()

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

    def _test_current_mol(self) -> None:
        """Test the current molecule."""
        builder_dialog = self.builder_dialog
        builder_dialog.adapt_z_matrix
        assert self.main_window.mols.get_current_mol().atomic_numbers.tolist() == [
            6,
            1,
            1,
            6,
            1,
            1,
            6,
            1,
            1,
            1,
            6,
            1,
            1,
            6,
            1,
            1,
            1,
        ]

    def _test_add_first_atom(self) -> None:
        """Test the addition of the first atom."""
        builder_dialog = self.builder_dialog
        builder_dialog.add_first_atom(("H", None))
        assert builder_dialog.err is True
        assert builder_dialog.colliding_idx is None
        assert builder_dialog.z_matrix == []
        # print(self.main_window.mols.get_current_mol().atomic_numbers)
        # assert self.main_window.mols.get_current_mol().atomic_numbers == [1]
