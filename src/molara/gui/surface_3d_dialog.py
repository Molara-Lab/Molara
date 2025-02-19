"""Module for displaying 3D surfaces from cube files."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow

    from molara.structure.molecule import Molecule

from molara.gui.layouts.ui_surface_3d_dialog import Ui_Surface3D_dialog
from molara.gui.surface_3d import Surface3DDialog

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
        self.ui.visualize_surfaceButton.clicked.connect(self.toggle_surfaces)
        self.ui.isoSpinBox.valueChanged.connect(self.change_iso_value)
        self.ui.colorPlusButton.clicked.connect(self.show_color_dialog_1)
        self.ui.colorMinusButton.clicked.connect(self.show_color_dialog_2)
        self.ui.checkBoxWireMesh.clicked.connect(self.toggle_wire_mesh)

        self.surface_toggle_button = self.ui.visualize_surfaceButton

    def update_color_buttons(self) -> None:
        """Update the color buttons."""
        self.ui.colorPlusButton.setStyleSheet(
            f"background-color: rgb({self.color_surface_1[0]}, {self.color_surface_1[1]}, {self.color_surface_1[2]})",
        )
        self.ui.colorMinusButton.setStyleSheet(
            f"background-color: rgb({self.color_surface_2[0]}, {self.color_surface_2[1]}, {self.color_surface_2[2]})",
        )

    def change_color_surface_1(self) -> None:
        """Change the color of the first surface."""
        super().change_color_surface_1()
        self.update_color_buttons()
        if self.surfaces_are_visible:
            self.display_surfaces()

    def change_color_surface_2(self) -> None:
        """Change the color of the second surface."""
        super().change_color_surface_2()
        self.update_color_buttons()
        if self.surfaces_are_visible:
            self.display_surfaces()

    def change_iso_value(self) -> None:
        """Change the iso value."""
        self.set_iso_value(self.ui.isoSpinBox.value())
        if self.surfaces_are_visible:
            self.visualize_surfaces()

    def initialize_dialog(self) -> None:
        """Initialize the dialog."""
        if not self.parent().structure_widget.structures[0].voxel_grid.is_initialized:
            return
        self.set_molecule(self.parent().structure_widget.structures[0])
        assert self.molecule is not None
        self.set_voxel_grid(self.molecule.voxel_grid)
        self.set_iso_value(self.ui.isoSpinBox.value())
        self.update_color_buttons()
        self.show()
