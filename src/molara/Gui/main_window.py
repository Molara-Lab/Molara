"""This module contains the main window of the application."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from molara.Gui.crystal_dialog import CrystalDialog
from molara.Gui.supercell_dialog import SupercellDialog
from molara.Gui.trajectory_dialog import TrajectoryDialog
from molara.Gui.ui_form import Ui_MainWindow
from molara.Structure.crystal import Crystal
from molara.Structure.crystals import Crystals
from molara.Structure.io.exporter import GeneralExporter
from molara.Structure.io.importer import GeneralImporter, PoscarImporter

if TYPE_CHECKING:
    from os import PathLike

__copyright__ = "Copyright 2024, Molara"


class MainWindow(QMainWindow):
    """Creates a MainWindow object."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Creates a MainWindow object.

        :param parent: parent widget
        """
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.structure_widget = self.ui.openGLWidget

        # instantiate dialog windows, pass main window as parent.
        self.trajectory_dialog = TrajectoryDialog(self)
        self.crystal_dialog = CrystalDialog(self)

        self.set_action_triggers()

    def set_action_triggers(self) -> None:
        """Connect Triggers of menu actions with the corresponding routines."""
        # Start
        self.ui.actionImport.triggered.connect(self.show_file_open_dialog)
        self.ui.actionExport.triggered.connect(self.export_structure)
        self.ui.actionExport_Snapshot.triggered.connect(self.structure_widget.export_snapshot)
        self.ui.quit.triggered.connect(self.close)

        # View
        self.ui.actionReset_View.triggered.connect(self.structure_widget.reset_view)
        self.ui.actionto_x_axis.triggered.connect(self.structure_widget.set_view_to_x_axis)
        self.ui.actionto_y_axis.triggered.connect(self.structure_widget.set_view_to_y_axis)
        self.ui.actionto_z_axis.triggered.connect(self.structure_widget.set_view_to_z_axis)
        self.ui.actionDraw_Axes.triggered.connect(self.structure_widget.toggle_axes)
        self.ui.actionCenter_Molecule.triggered.connect(
            self.structure_widget.center_structure,
        )
        self.ui.actionToggle_Bonds.triggered.connect(self.toggle_bonds)
        self.ui.actionOpen_Trajectory_Dialog.triggered.connect(
            self.trajectory_dialog.show,
        )

        # Tools
        self.ui.actionBuilder.triggered.connect(
            self.structure_widget.show_builder_dialog,
        )
        self.ui.actionMeasure.triggered.connect(
            self.show_measurement_dialog,
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
        """Load the molecules from path.

        :param path: input file path
        """
        importer = GeneralImporter(path)
        self.mols = importer.load()

        self.structure_widget.set_structure(self.mols.get_current_mol())

        if self.mols.num_mols > 1:
            self.trajectory_dialog.show()
            self.trajectory_dialog.initial_energy_plot()
            self.trajectory_dialog.set_slider_range()

    def export_structure(self) -> None:
        """Save structure to file."""
        if not self.structure_widget.structure:
            return
        filename = QFileDialog.getSaveFileName(
            self,
            "Export structure to file",
            ".",
            "*",
        )
        exporter = GeneralExporter(filename[0])
        exporter.write_structure(self.structure_widget.structure)

    def toggle_bonds(self) -> None:
        """Toggles the bonds on and off."""
        if self.structure_widget.structure:
            self.structure_widget.structure.toggle_bonds()
            self.structure_widget.bonds = not self.structure_widget.bonds
            self.structure_widget.update()

    def show_measurement_dialog(self) -> None:
        """Show the measurement dialog."""
        if self.structure_widget.structure_is_set:
            self.measurement_dialog.ini_labels()
            self.measurement_dialog.show()

    def show_builder_dialog(self) -> None:
        """Show the builder dialog."""
        self.builder_dialog.show()

    def edit_supercell_dims(self) -> bool:
        """Open dialog window to edit supercell dimensions."""
        if not isinstance(self.structure_widget.structure, Crystal):
            # insert error message?
            return False
        crystal = self.structure_widget.structure
        supercell_dims = crystal.supercell_dims
        SupercellDialog.get_supercell_dims(supercell_dims)
        # check if supercell dimensions have successfully been passed (i.e., all are >0)
        if sum(1 for component in supercell_dims if component <= 0):
            return False
        crystal.make_supercell(supercell_dims)
        self.structure_widget.set_structure(crystal)
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
        self.structure_widget.set_structure(struct=crystals.get_current_mol())
        return True