"""Module for displaying 3D surfaces from cube files."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow

    from molara.structure.molecule import Molecule

from molara.gui.surface_3d import Surface3DDialog
from molara.gui.ui_surface_3d_dialog import Ui_Surface3D_dialog

__copyright__ = "Copyright 2024, Molara"


class CubeFileDialog(Surface3DDialog):
    """Dialog for displaying MOs."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Initialize the MOs dialog.

        params:
        parent: MainWindow: The widget of the MainWindow.
        """
        super().__init__(
            parent,
        )
        self.molecule: None | Molecule = None
        self.ui = Ui_Surface3D_dialog()
        self.ui.setupUi(self)
        self.ui.visualize_surfaceButton.clicked.connect(self.visualize_surfaces)
        self.ui.isoSpinBox.valueChanged.connect(self.change_iso_value)

    def change_iso_value(self) -> None:
        """Change the iso value."""
        self.set_iso_value(self.ui.isoSpinBox.value())
        self.visualize_surfaces()

    def initialize_dialog(self) -> None:
        """Initialize the dialog."""
        self.set_molecule(self.parent().structure_widget.structures[0])
        assert self.molecule is not None
        self.set_voxel_grid(self.molecule.voxel_grid)
        self.set_iso_value(self.ui.isoSpinBox.value())
