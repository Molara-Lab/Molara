"""Module for displaying the MOs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
)

from molara.Gui.ui_mos_dialog import Ui_MOs_dialog

if TYPE_CHECKING:
    from molara.Molecule.structure import Structure

__copyright__ = "Copyright 2024, Molara"


class MOsDialog(QDialog):
    """Dialog for displaying MOs."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Initializes the MOs dialog.

        params:
        parent: MainWindow: The widget of the MainWindow.
        """
        super().__init__(
            parent,
        )

        self.ui = Ui_MOs_dialog()
        self.ui.setupUi(self)
        print()

