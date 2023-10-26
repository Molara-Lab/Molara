from __future__ import annotations

import sys

from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from molara.Gui.trajectory_dialog import TrajectoryDialog
from molara.Gui.ui_form import Ui_MainWindow
from molara.Molecule.crystal import Crystal
from molara.Molecule.importer import read_coord, read_xyz


class MainWindow(QMainWindow):
    def __init__(self, parent: QMainWindow = None) -> None:
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.trajectory_dialog = TrajectoryDialog(self)  # pass widget as parent

    def show_init_xyz(self) -> None:
        """
        read the file from terminal arguments
        """
        file_name = sys.argv[1]

        self.mols = read_xyz(file_name)

        self.ui.openGLWidget.set_molecule(self.mols.get_current_mol())

        if self.mols.num_mols > 1:
            self.trajectory_dialog.show()
            self.trajectory_dialog.initial_energy_plot()
            self.trajectory_dialog.set_slider_range()

    def show_xyz(self) -> None:
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open .xyz file",
            "/home",
            "Image Files (*.xyz)",
        )

        self.mols = read_xyz(file_name[0])

        self.ui.openGLWidget.set_molecule(self.mols.get_current_mol())

        if self.mols.num_mols > 1:
            self.trajectory_dialog.show()
            self.trajectory_dialog.initial_energy_plot()

    def show_coord(self) -> None:
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open coord file",
            "/home",
            "Image Files (*)",
        )

        self.mols = read_coord(file_name[0])

        self.ui.openGLWidget.set_molecule(self.mols.get_current_mol())

    def show_poscar(self) -> bool:
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
        self.ui.openGLWidget.set_molecule(crystal)
        return True
