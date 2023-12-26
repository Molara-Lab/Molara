"""This module contains the main window of the application."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from molara.Gui.trajectory_dialog import TrajectoryDialog
from molara.Gui.ui_form import Ui_MainWindow
from molara.Molecule.crystal import Crystal
from molara.Molecule.io.importer import GeneralImporter

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

    def show_init_xyz(self) -> None:
        """Read the file from terminal arguments."""
        file_name = sys.argv[1]

        self.load_molecules(file_name)

    def show_file_open_dialog(self) -> None:
        """Select a file in the file open dialog."""
        file_name = QFileDialog.getOpenFileName(
            self,
            dir=".",
        )[0]
        self.load_molecules(file_name)

    def load_molecules(self, path: PathLike | str) -> None:
        """Load the molecules from path."""
        importer = GeneralImporter(path)
        self.mols = importer.load()

        self.ui.openGLWidget.set_structure(self.mols.get_current_mol())

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

        crystal = Crystal.from_poscar(filename[0])
        if not isinstance(crystal, Crystal):
            error_message = crystal[1]
            msg_box = QMessageBox()
            msg_box.setText(error_message)
            msg_box.exec()
            return False
        self.ui.openGLWidget.set_structure(crystal)
        return True

    def toggle_bonds(self) -> None:
        """Toggles the bonds on and off."""
        if self.ui.openGLWidget.structure:
            self.ui.openGLWidget.structure.toggle_bonds()
            self.ui.openGLWidget.bonds = not self.ui.openGLWidget.bonds
            self.ui.openGLWidget.update()
