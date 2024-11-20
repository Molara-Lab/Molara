"""Test the NormalizationDialog class."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from unittest import mock

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    from molara.gui.main_window import MainWindow


class WorkaroundTestNormalizationDialog:
    """Contains the tests for the MOsDialog class.

    It does not inherit from unittest.TestCase, because that does not work with pytest-qt.
    """

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the WorkaroundTestMeasurementDialog object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        testargs = ["molara", "examples/molden/o2.molden"]
        with mock.patch.object(sys, "argv", testargs):
            self.main_window.show_init_xyz()

        self.main_window.show_normalization_dialog()
        self.normalization_dialog = self.main_window.normalization_dialog

    def run_tests(self) -> None:
        """Run the tests."""
        # unrestricted case
        self._test_population()

        self._test_close()

    def _test_population(self) -> None:
        """Test the populationanalysis."""
        self.normalization_dialog.run_population_analysis()
        assert self.normalization_dialog.ui.exactCountLabel.text() == "16.0"
        assert self.normalization_dialog.ui.calculatedCountLabel.text() == "15.999999999983896"

    def _test_close(self) -> None:
        """Close the widget again."""
        self.normalization_dialog.close()
        assert self.normalization_dialog.ui.exactCountLabel.text() == ""
        assert self.normalization_dialog.ui.calculatedCountLabel.text() == ""
