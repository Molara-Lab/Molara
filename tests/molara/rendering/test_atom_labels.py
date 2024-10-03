"""Contains the unit tests for the atom labels calculation of the rendering package."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

    from molara.gui.main_window import MainWindow

import sys
from unittest import mock

import numpy as np

from molara.rendering.atom_labels import calculate_atom_number_arrays, init_atom_number


class WorkaroundTestAtomLabels:
    """Contains the tests for the buffers module."""

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the WorkaroundTestMainWindow object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.openGLWidget = main_window.structure_widget

    def test_atom_numbers(self) -> None:
        """Tests the init_atom_number function of the atom_labels module."""
        testargs = ["molara", "examples/xyz/pentane.xyz"]
        with mock.patch.object(sys, "argv", testargs):
            self.main_window.show_init_xyz()

        digits, positions_3d = init_atom_number(
            self.main_window.structure_widget.structures[0]
        )

        assert isinstance(digits, np.ndarray)
        assert isinstance(positions_3d, np.ndarray)
        assert len(digits) == 17  # noqa: PLR2004
        assert len(positions_3d) == 17  # noqa: PLR2004

        calculate_atom_number_arrays(
            digits,
            positions_3d,
            self.main_window.structure_widget.structures[0],
            self.main_window.structure_widget.camera,
        )
        assert isinstance(digits, np.ndarray)
        assert isinstance(positions_3d, np.ndarray)
        assert len(digits) == 17  # noqa: PLR2004
        assert len(positions_3d) == 17  # noqa: PLR2004
        for i in range(17):
            assert digits[i] == i + 1
            assert isinstance(positions_3d[i], np.ndarray)
            assert len(positions_3d[i]) == 3  # noqa: PLR2004
