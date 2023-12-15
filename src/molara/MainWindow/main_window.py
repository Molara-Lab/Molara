"""This module contains the main window of the application."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from molara.Gui.crystal_dialog import CrystalDialog
from molara.Gui.supercell_dialog import SupercellDialog
from molara.Gui.trajectory_dialog import TrajectoryDialog
from molara.Gui.ui_form import Ui_MainWindow
from molara.Molecule.crystal import Crystal
from molara.Molecule.io.importer import GeneralImporter, PoscarImporter

if TYPE_CHECKING:
    from os import PathLike


class MainWindow(QMainWindow):
    """Creates a MainWindow object."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Creates a MainWindow object."""
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.trajectory_dialog = TrajectoryDialog(self)  # pass widget as parent
        self.crystal_dialog = CrystalDialog(self)  # pass widget as parent

    def show_init_xyz(self) -> None:
        """Read the file from terminal arguments."""
        file_name = sys.argv[1]

        self.load_molecules(file_name)

    def show_file_open_dialog(self) -> None:
        """Select a file in the file open dialog."""
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open .xyz file",
            "/home",
            "All Files (*.*)",
        )[0]
        self.load_molecules(file_name)

    def load_molecules(self, path: PathLike | str) -> None:
        """Load the molecules from path."""
        importer = GeneralImporter(path)
        self.mols = importer.load()

        self.ui.openGLWidget.set_molecule(self.mols.get_current_mol())

        if self.mols.num_mols > 1:
            self.trajectory_dialog.show()
            self.trajectory_dialog.initial_energy_plot()
            self.trajectory_dialog.set_slider_range()

    def show_poscar(self) -> bool:
        """Reads poscar file and shows the first structure in this file."""
        filename = QFileDialog.getOpenFileName(
            self,
            "Open POSCAR file",
            "/home",
            "POSCAR Files (*)",
        )

        supercell_dims = [-1, -1, -1]
        SupercellDialog.get_supercell_dims(supercell_dims)
        # check if supercell dimensions have successfully been passed (i.e., all are >0)
        if sum(1 for component in supercell_dims if component <= 0):
            return False

        importer = PoscarImporter(filename[0], supercell_dims)
        crystal = importer.load()

        if not isinstance(crystal, Crystal):
            error_message = crystal[1]
            msg_box = QMessageBox()
            msg_box.setText(error_message)
            msg_box.exec()
            return False
        self.ui.openGLWidget.set_molecule(crystal)
        return True

    def toggle_bonds(self) -> None:
        """Toggles the bonds on and off."""
        if self.ui.openGLWidget.molecule:
            self.ui.openGLWidget.bonds = not self.ui.openGLWidget.bonds
            self.ui.openGLWidget.update()
