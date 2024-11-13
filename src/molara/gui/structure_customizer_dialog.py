"""Dialog for manipulating appearance of structures."""

from __future__ import annotations

import json
import shutil
from os import listdir
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
)

from molara.gui.ui_structure_customizer import Ui_structure_customizer
from molara.rendering.atom_labels import init_atom_number

if TYPE_CHECKING:
    from molara.structure.crystal import Crystal
    from molara.structure.molecule import Molecule
    from molara.structure.structure import Structure

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
        self.ui = Ui_structure_customizer()
        self.ui.setupUi(self)

        self.src_path = Path(__file__).parent.parent
        self.home_path = Path("~/.molara").expanduser()
        self.save_names: list = []
        self.update_settings_box()

        self.stick_mode = False
        self.bonds = True
        self.numbers = False
        self.max_atoms_for_numbers = 999
        self.atom_indices_arrays: tuple[np.ndarray, np.ndarray, np.ndarray] = (np.zeros(1), np.zeros(1), np.zeros(1))

        self.ui.ballSizeSpinBox.setValue(1.0)
        self.ui.stickSizeSpinBox.setValue(1.0)
        self.ui.toggleBondsButton.setText("Hide Bonds")
        self.ui.toggleNumbersButton.setText("Show Indices")
        self.ui.colorSchemeSelect.addItems(["Jmol", "CPK"])

        self.ui.viewModeButton.clicked.connect(self.toggle_stick_mode)
        self.ui.toggleBondsButton.clicked.connect(self.toggle_bonds)
        self.ui.toggleNumbersButton.clicked.connect(self.toggle_numbers)
        self.ui.saveButton.clicked.connect(self.save_settings)
        self.ui.loadButton.clicked.connect(self.load_settings)
        self.ui.deleteButton.clicked.connect(self.delete_settings)

        self.ui.ballSizeSpinBox.valueChanged.connect(self.apply_changes)
        self.ui.stickSizeSpinBox.valueChanged.connect(self.apply_changes)
        self.ui.indexSizeSpinBox.valueChanged.connect(self.apply_changes)
        self.ui.colorSchemeSelect.currentIndexChanged.connect(self.apply_changes)

        self.load_default_settings()

    def load_default_settings(self) -> None:
        """Load the default settings."""
        self.load_settings("Default")

    def update_settings_box(self) -> None:
        """Update the settings box."""
        if not self.home_path.joinpath("settings/structure").exists():
            Path(f"{self.home_path}/settings/structure").mkdir(parents=True, exist_ok=True)
        if not self.home_path.joinpath("settings/structure/Default.json").exists():
            shutil.copy(
                f"{self.src_path}/settings/structure/Default.json",
                f"{self.home_path}/settings/structure/Default.json",
            )
        save_files = [
            f
            for f in listdir(f"{self.home_path}/settings/structure")
            if Path.is_file(self.home_path / "settings" / "structure" / f)
        ]
        self.save_names = [f.split(".")[0] for f in save_files]
        self.save_names.sort()
        self.ui.loadSelect.clear()
        self.ui.loadSelect.addItems(self.save_names)

    def delete_settings(self) -> None:
        """Delete the selected settings."""
        save_name = self.ui.loadSelect.currentText()
        if save_name == "Default":
            return
        settings_file = f"{self.home_path}/settings/structure/{save_name}.json"
        Path(settings_file).unlink()
        self.update_settings_box()

    def load_settings(self, save_name: str = "") -> None:
        """Load the settings from a save file.

        :param save_name: name of the save file
        """
        if not save_name:
            save_name = self.ui.loadSelect.currentText()
        settings_file = f"{self.home_path}/settings/structure/{save_name}.json"
        with Path(settings_file).open() as f:
            settings = json.load(f)
        self.load_settings_dict(settings)
        if self.parent().structure_widget.structures:
            self.apply_changes()

    def create_settings_dict(self) -> dict:
        """Create a dictionary of the settings."""
        return {
            "stick_mode": bool(self.stick_mode),
            "bonds": bool(self.bonds),
            "ball_size": float(self.ui.ballSizeSpinBox.value()),
            "stick_size": float(self.ui.stickSizeSpinBox.value()),
            "atom_numbers": bool(self.numbers),
            "atom_numbers_size": float(self.ui.indexSizeSpinBox.value()),
            "color_scheme": self.ui.colorSchemeSelect.currentText(),
        }

    def load_settings_dict(self, settings: dict) -> None:
        """Load the settings from a dictionary.

        settings: dict: dictionary of settings
        """
        self.stick_mode = settings["stick_mode"]
        if self.stick_mode:
            self.ui.viewModeButton.setText("Ball Mode")
            self.ui.stickSizeSpinBox.setEnabled(True)
            self.ui.ballSizeSpinBox.setEnabled(False)
        else:
            self.ui.viewModeButton.setText("Stick Mode")
            self.ui.stickSizeSpinBox.setEnabled(True)
            self.ui.ballSizeSpinBox.setEnabled(True)
        self.set_bonds(settings["bonds"])
        self.ui.ballSizeSpinBox.setValue(settings["ball_size"])
        self.ui.stickSizeSpinBox.setValue(settings["stick_size"])
        self.numbers = settings["atom_numbers"]
        self.ui.indexSizeSpinBox.setValue(settings["atom_numbers_size"])

        if settings["color_scheme"] == "Jmol":
            self.ui.colorSchemeSelect.setCurrentIndex(0)
        else:
            self.ui.colorSchemeSelect.setCurrentIndex(1)

    def save_settings(self) -> None:
        """Save the settings to a file."""
        save_name = self.ui.saveName.toPlainText()
        if save_name in ("", "Enter name"):
            self.ui.saveName.setPlainText("Enter name")
        else:
            settings = self.create_settings_dict()
            settings_file = f"{self.home_path}/settings/structure/{save_name}.json"
            with Path(settings_file).open("w") as f:
                json.dump(settings, f)
        self.update_settings_box()

    def set_cylinder_and_sphere_att(
        self,
        structure: Structure | Molecule | Crystal,
        ball_size: float,
        stick_size: float,
    ) -> None:
        """Set the sizes of the spheres and cylinders.

        :param structure: structure to set the sizes for
        :param ball_size: size of the spheres
        :param stick_size: size of the cylinders
        """
        structure.drawer.cylinder_radius = stick_size
        structure.drawer.sphere_default_radius = ball_size

        # Set the color scheme
        structure.drawer.color_scheme = self.ui.colorSchemeSelect.currentText()

        if self.stick_mode:
            structure.drawer.sphere_scale = self.ui.stickSizeSpinBox.value()
        else:
            structure.drawer.sphere_scale = self.ui.ballSizeSpinBox.value()
        structure.drawer.set_atom_colors()
        structure.drawer.set_cylinder_colors()
        structure.drawer.set_atom_scales()
        structure.drawer.set_atom_scale_matrices()
        structure.drawer.set_atom_model_matrices()

    def apply_changes(self) -> None:
        """Set the size of the cylinders."""
        structures = self.parent().structure_widget.structures
        for structure in structures:
            if self.stick_mode:
                structure.drawer.stick_mode = True

                atom_radius = 0.15
                stick_radius = atom_radius + 1e-3
            else:
                structure.drawer.stick_mode = False

                atom_radius = 1.0 / 6
                stick_radius = 0.075

            self.set_cylinder_and_sphere_att(structure, atom_radius, stick_radius)

            if self.bonds:
                structure.draw_bonds = True
                structure.drawer.cylinder_scale = self.ui.stickSizeSpinBox.value()
                structure.drawer.set_cylinder_dimensions()
                structure.drawer.set_cylinder_scale_matrices()
                structure.drawer.set_cylinder_model_matrices()
            else:
                structure.draw_bonds = False

        if structures:
            if self.numbers:
                self.parent().structure_widget.atom_indices_arrays = init_atom_number(structures[0])
                self.parent().structure_widget.number_scale = self.ui.indexSizeSpinBox.value()
            self.parent().structure_widget.show_atom_indices = self.numbers

            self.parent().structure_widget.set_vertex_attribute_objects()
        self.parent().structure_widget.update()

    def toggle_stick_mode(self) -> None:
        """Toggle between stick and ball mode."""
        if self.parent().structure_widget.structures[0].has_bonds:
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
            self.apply_changes()

    def toggle_bonds(self) -> None:
        """Toggle bonds on and off."""
        if self.parent().structure_widget.structures[0].has_bonds:
            self.bonds = not self.bonds
            self.set_bonds(self.bonds)
            self.apply_changes()

    def toggle_numbers(self) -> None:
        """Toggle atom numbers on and off."""
        self.numbers = not self.numbers
        self.set_numbers(self.numbers)

    def set_numbers(self, numbers: bool) -> None:
        """Set numbers to True or False."""
        self.numbers = numbers
        structure = self.parent().structure_widget.structures[0]
        if self.numbers:
            if len(structure.atoms) < self.max_atoms_for_numbers:
                self.ui.toggleNumbersButton.setText("Hide Indices")
            else:
                self.numbers = False
                self.atom_indices_arrays = (np.zeros(1), np.zeros(1), np.zeros(1))
        else:
            self.ui.toggleNumbersButton.setText("Show Indices")
        self.apply_changes()

    def set_bonds(self, bonds: bool) -> None:
        """Set bonds to True or False."""
        if self.parent().structure_widget.structures and self.parent().structure_widget.structures[0].has_bonds:
            self.bonds = bonds
            if self.bonds:
                self.ui.toggleBondsButton.setText("Hide Bonds")
            else:
                self.ui.toggleBondsButton.setText("Show Bonds")
            self.apply_changes()
