"""Test the StructureCustomizerDialog class."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    from molara.gui.main_window import MainWindow


class WorkaroundTestCustomizerDialog:
    """Contains the tests for the CustomizerDialog class.

    It does not inherit from unittest.TestCase, because that does not work with pytest-qt.
    """

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the WorkaroundTestCustomizerDialog object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.main_window.show_structure_customizer_dialog()
        self.customizer_dialog = main_window.structure_customizer_dialog
        self.molecule = self.main_window.structure_widget.structures[0]

    def teardown(self) -> None:
        """Clean up after tests."""
        if self.customizer_dialog:
            self.customizer_dialog.close()

    def run_tests(self) -> None:
        """Run the tests."""
        self._test_stick_mode()

    def _test_stick_mode(self) -> None:
        """Test the toggle stick model method."""
        self.customizer_dialog.toggle_stick_mode()
        assert not self.customizer_dialog.stick_mode
        self.customizer_dialog.toggle_stick_mode()
        assert self.customizer_dialog.stick_mode
        self.molecule.drawer.set_spheres(self.molecule.atoms)
        for radius in self.molecule.drawer.sphere_radii:
            assert radius == self.molecule.drawer.sphere_radii[0]
