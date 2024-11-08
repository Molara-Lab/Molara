"""Module for displaying 3D surfaces from cube files."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtCore import Qt

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent

from PySide6.QtWidgets import QDialog, QHeaderView, QMainWindow, QTableWidgetItem
from molara.gui.ui_surface_3d_dialog import Ui_Surface3D_dialog


__copyright__ = "Copyright 2024, Molara"


class Surface3DDialog(QDialog):
    """Dialog for displaying MOs."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Initialize the MOs dialog.

        params:
        parent: MainWindow: The widget of the MainWindow.
        """
        super().__init__(
            parent,
        )
        self.ui = Ui_Surface3D_dialog()
        self.ui.setupUi(self)