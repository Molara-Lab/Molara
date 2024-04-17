
from __future__ import annotations

from typing import TYPE_CHECKING

from molara.Gui.ui_structure_customizer import Ui_structure_customizer

from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
)

__copyright__ = "Copyright 2024, Molara"

class StructureCustomizerDialog(QDialog):
    """Dialog for manipulating appearance of trajectories."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Initialize the trajectory dialog.

        :param parent: parent widget (main window)
        """
        super().__init__(
            parent,
        )  # main window widget is passed as a parent, so dialog is closed if main window is closed.
        self.stick_mode = False
        self.bonds = True

        self.ui = Ui_structure_customizer()
        self.ui.setupUi(self)
        self.ui.ballSizeSpinBox.setValue(1.0)
        self.ui.stickSizeSpinBox.setValue(1.0)
        self.ui.toggleBondsButton.setText("Hide Bonds")

        self.ui.applyButton.clicked.connect(self.apply_changes)
        self.ui.viewModeButton.clicked.connect(self.toggle_stick_mode)
        self.ui.toggleBondsButton.clicked.connect(self.toggle_bonds)

    def apply_changes(self) -> None:
        """Set the size of the cylinders."""
        if self.stick_mode:
            stick_radius = 0.15
            self.parent().structure_widget.structure.drawer.cylinder_radius = stick_radius
            self.parent().structure_widget.structure.drawer.sphere_default_radius = stick_radius

            self.parent().structure_widget.structure.drawer.sphere_scale = self.ui.stickSizeSpinBox.value() - 0.01
            self.parent().structure_widget.structure.drawer.set_atom_scales()
            self.parent().structure_widget.structure.drawer.set_atom_scale_matrices()
            self.parent().structure_widget.structure.drawer.set_atom_model_matrices()
        else:
            self.parent().structure_widget.structure.drawer.sphere_default_radius = 1.0 / 6
            self.parent().structure_widget.structure.drawer.cylinder_radius = 0.075

            self.parent().structure_widget.structure.drawer.sphere_scale = self.ui.ballSizeSpinBox.value()
            self.parent().structure_widget.structure.drawer.set_atom_scales()
            self.parent().structure_widget.structure.drawer.set_atom_scale_matrices()
            self.parent().structure_widget.structure.drawer.set_atom_model_matrices()

        if self.bonds:
            self.parent().structure_widget.structure.draw_bonds = True
        else:
            self.parent().structure_widget.structure.draw_bonds = False

        self.parent().structure_widget.structure.drawer.cylinder_scale = self.ui.stickSizeSpinBox.value()
        self.parent().structure_widget.structure.drawer.set_cylinder_dimensions()
        self.parent().structure_widget.structure.drawer.set_cylinder_scale_matrices()
        self.parent().structure_widget.structure.drawer.set_cylinder_model_matrices()

        self.parent().structure_widget.set_vertex_attribute_objects()
        self.parent().structure_widget.update()

    def toggle_stick_mode(self) -> None:
        """Toggle between stick and ball mode."""
        self.stick_mode = not self.stick_mode
        if self.stick_mode:
            if not self.bonds:
                self.toggle_bonds()
                self.bonds = True
            self.ui.viewModeButton.setText("Ball Mode")
            self.parent().ui.actionToggle_Bonds.setEnabled(False)
            self.ui.toggleBondsButton.setEnabled(False)
            self.ui.stickSizeSpinBox.setEnabled(True)
            self.ui.ballSizeSpinBox.setEnabled(False)
        else:
            self.ui.viewModeButton.setText("Stick Mode")
            self.ui.toggleBondsButton.setEnabled(True)
            self.ui.stickSizeSpinBox.setEnabled(True)
            self.ui.ballSizeSpinBox.setEnabled(True)

    def toggle_bonds(self) -> None:
        """Toggle bonds on and off."""
        self.bonds = not self.bonds
        if self.bonds:
            self.ui.toggleBondsButton.setText("Hide Bonds")
        else:
            self.ui.toggleBondsButton.setText("Show Bonds")
