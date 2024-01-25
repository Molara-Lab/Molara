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
from molara.Molecule.crystals import Crystals
from molara.Molecule.io.exporter import GeneralExporter
from molara.Molecule.io.importer import GeneralImporter, PoscarImporter

if TYPE_CHECKING:
    from os import PathLike

__copyright__ = "Copyright 2024, Molara"


class MainWindow(QMainWindow):
    """Creates a MainWindow object."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Creates a MainWindow object."""
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.trajectory_dialog = TrajectoryDialog(self)  # pass widget as parent
        self.crystal_dialog = CrystalDialog(self)  # pass widget as parent
        self.set_action_triggers()

    def set_action_triggers(self) -> None:
        """Connect Triggers of menu actions with the corresponding routines."""
        # Start
        self.ui.actionImport.triggered.connect(self.show_file_open_dialog)
        self.ui.actionExport.triggered.connect(self.export_structure)
        self.ui.quit.triggered.connect(self.close)

        # View
        self.ui.actionReset_View.triggered.connect(self.ui.openGLWidget.reset_view)
        self.ui.actionDraw_Axes.triggered.connect(self.ui.openGLWidget.add_unit_cell_boundaries)#toggle_axes)
        self.ui.actionCenter_Molecule.triggered.connect(
            self.ui.openGLWidget.center_molecule,
        )
        self.ui.actionToggle_Bonds.triggered.connect(self.toggle_bonds)
        self.ui.actionOpen_Trajectory_Dialog.triggered.connect(
            self.trajectory_dialog.show,
        )

        # Tools
        self.ui.actionMeasure.triggered.connect(
            self.ui.openGLWidget.show_measurement_dialog,
        )

        self.ui.actionRead_POSCAR.triggered.connect(self.show_poscar)
        self.ui.actionCreate_Lattice.triggered.connect(self.crystal_dialog.show)
        self.ui.actionSupercell.triggered.connect(self.edit_supercell_dims)

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

    def export_structure(self) -> None:
        """Save structure to file."""
        if not self.ui.openGLWidget.structure:
            return
        filename = QFileDialog.getSaveFileName(
            self,
            "Export structure to file",
            ".",
            "*",
        )
        exporter = GeneralExporter(filename[0])
        exporter.write_structure(self.ui.openGLWidget.structure)

    def toggle_bonds(self) -> None:
        """Toggles the bonds on and off."""
        if self.ui.openGLWidget.structure:
            self.ui.openGLWidget.structure.toggle_bonds()
            self.ui.openGLWidget.bonds = not self.ui.openGLWidget.bonds
            self.ui.openGLWidget.update()

    def edit_supercell_dims(self) -> bool:
        """Open dialog window to edit supercell dimensions."""
        if not isinstance(self.ui.openGLWidget.structure, Crystal):
            # insert error message?
            return False
        crystal = self.ui.openGLWidget.structure
        supercell_dims = crystal.supercell_dims
        SupercellDialog.get_supercell_dims(supercell_dims)
        # check if supercell dimensions have successfully been passed (i.e., all are >0)
        if sum(1 for component in supercell_dims if component <= 0):
            return False
        crystal.make_supercell(supercell_dims)
        self.ui.openGLWidget.set_structure(crystal)
        return True

    def show_poscar(self) -> bool:
        """Reads poscar file and shows the first structure in this file."""
        filename = QFileDialog.getOpenFileName(
            self,
            caption="Open POSCAR file",
            dir=".",
            filter="POSCAR Files (*)",
        )

        supercell_dims = [1, 1, 1]

        importer = PoscarImporter(filename[0], supercell_dims)
        crystals = importer.load()

        if not isinstance(crystals, Crystals):
            crystal = crystals.get_current_mol()
            error_message = crystal[1]
            msg_box = QMessageBox()
            msg_box.setText(error_message)
            msg_box.exec()
            return False
        self.ui.openGLWidget.set_structure(struct=crystals.get_current_mol())
        return True
