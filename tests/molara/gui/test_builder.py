"""Test the BuilderDialog class."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from molara.Gui.main_window import MainWindow
    from pytestqt.qtbot import QtBot

import time

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


    def _test_init(self) -> None:
        """Test the initialization of the BuilderDialog class."""
        assert self.builder_dialog is not None
        builder_dialog = self.builder_dialog
        builder_dialog.show()
        assert builder_dialog.isVisible()
