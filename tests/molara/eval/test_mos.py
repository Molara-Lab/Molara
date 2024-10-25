"""Test the molecular orbital code."""

from __future__ import annotations

import sys
from unittest import TestCase, mock

import numpy as np
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

from molara.gui.main_window import MainWindow
from molara.structure.molecule import Molecule

__copyright__ = "Copyright 2024, Molara"


class TestMolecularOrbitals(TestCase):
    """Test the molecular orbital code."""

    def setUp(self) -> None:
        """Initialize the program."""
        _format = QSurfaceFormat()
        _format.setVersion(3, 3)
        _format.setSamples(4)
        _format.setProfile(QSurfaceFormat.CoreProfile)  # type: ignore[attr-defined]
        QSurfaceFormat.setDefaultFormat(_format)
        self.app = QApplication([]) if QApplication.instance() is None else QApplication.instance()
        self.main_window = MainWindow()
        self.main_window.show()
        testargs = ["molara", "examples/molden/h2o.molden"]
        with mock.patch.object(sys, "argv", testargs):
            self.main_window.show_init_xyz()
        if isinstance(self.main_window.structure_widget.structures[0], Molecule):
            self.mos = self.main_window.structure_widget.structures[0].mos
            self.aos = self.main_window.structure_widget.structures[0].basis_set

    def test_mo_evaluation(self) -> None:
        """Test Camera setup."""
        val = self.mos.get_mo_value(1, self.aos, np.array([0.10154165, 0.465418564, -1.498185465]))
        # Generated after comparing the mos with the mos of multiwfn.
        reference = 0.009741653204777932
        assert val == reference
