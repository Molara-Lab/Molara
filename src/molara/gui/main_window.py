"""Contains the main window of the application."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from molara.gui.builder import BuilderDialog
from molara.gui.crystal_dialog import CrystalDialog
from molara.gui.export_image_dialog import ExportImageDialog
from molara.gui.measuring_tool_dialog import MeasurementDialog
from molara.gui.mos_dialog import MOsDialog
from molara.gui.structure_customizer_dialog import StructureCustomizerDialog
from molara.gui.supercell_dialog import SupercellDialog
from molara.gui.surface_3d_dialog import CubeFileDialog
from molara.gui.trajectory_dialog import TrajectoryDialog
from molara.gui.ui_form import Ui_MainWindow
from molara.structure.crystal import Crystal
from molara.structure.crystals import Crystals
from molara.structure.io.exporter import GeneralExporter
from molara.structure.io.importer import GeneralImporter, PoscarImporter
from molara.structure.molecules import Molecules

if TYPE_CHECKING:
    from os import PathLike

    from molara.gui.structure_widget import StructureWidget

__copyright__ = "Copyright 2024, Molara"


ENABLED, DISABLED = True, False


class MainWindow(QMainWindow):
    """Creates a MainWindow object."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        """Create a MainWindow object.

        :param parent: parent widget
        """
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.export_image_dialog = ExportImageDialog(self)

        # instantiate dialog windows, pass main window as parent.
        self.trajectory_dialog = TrajectoryDialog(self)
        self.crystal_dialog = CrystalDialog(self)
        self.measurement_dialog = MeasurementDialog(self)
        self.builder_dialog = BuilderDialog(self)
        self.supercell_dialog = SupercellDialog(self)
        self.structure_customizer_dialog = StructureCustomizerDialog(self)
        self.mo_dialog = MOsDialog(self)
        self.surface_3d_dialog = CubeFileDialog(self)
        self.mols = Molecules()

        self.set_action_triggers()
        self.update_action_texts()

    @property
    def structure_widget(self) -> StructureWidget:
        """Returns the StructureWidget (openGLWidget)."""
        return self.ui.openGLWidget

    def set_action_triggers(self) -> None:
        """Connect Triggers of menu actions with the corresponding routines."""
        # Start
        self.ui.actionImport.triggered.connect(self.show_file_open_dialog)
        self.ui.actionExport.triggered.connect(self.export_structure)
        self.ui.quit.triggered.connect(self.close)

        self.ui.actionExport_Snapshot.triggered.connect(
            self.export_image_dialog.show_dialog,
        )  # self.virtual_rendering_window.draw_spheres_and_export)

        # View
        self.ui.actionReset_View.triggered.connect(self.structure_widget.reset_view)
        self.ui.actionto_x_axis.triggered.connect(lambda: self.structure_widget.set_view_to_axis("x"))
        self.ui.actionto_y_axis.triggered.connect(lambda: self.structure_widget.set_view_to_axis("y"))
        self.ui.actionto_z_axis.triggered.connect(lambda: self.structure_widget.set_view_to_axis("z"))
        self.ui.actionToggle_Axes.triggered.connect(self.structure_widget.toggle_axes)
        self.ui.actionCenter_Molecule.triggered.connect(
            self.structure_widget.center_structure,
        )
        self.ui.actionOpen_Trajectory_Dialog.triggered.connect(
            self.trajectory_dialog.show,
        )
        self.ui.actionToggle_Projection.triggered.connect(self.structure_widget.toggle_projection)
        self.ui.actionExport_CameraSettings.triggered.connect(self.export_camera_settings)
        self.ui.actionImport_CameraSettings.triggered.connect(self.import_camera_settings)
        self.ui.actionOpen_Structure_Customizer.triggered.connect(
            self.show_structure_customizer_dialog,
        )
        # tools
        self.ui.actionBuilder.triggered.connect(
            self.show_builder_dialog,
        )
        self.ui.actionMeasure.triggered.connect(
            self.show_measurement_dialog,
        )
        self.ui.actionDisplay_MOs.triggered.connect(
            self.show_mo_dialog,
        )
        self.ui.actionDisplay_3D_Surface.triggered.connect(
            self.show_surface_3d_dialog,
        )

        self.ui.actionRead_POSCAR.triggered.connect(self.show_poscar)
        self.ui.actionCreate_Lattice.triggered.connect(self.crystal_dialog.show)
        self.ui.actionSupercell.triggered.connect(self.edit_supercell_dims)
        self.ui.actionToggle_UnitCellBoundaries.triggered.connect(self.structure_widget.toggle_unit_cell_boundaries)
        self.update_action_texts()

    def show_mo_dialog(self) -> None:
        """Check if molecular orbitals have been loaded and perform actions accordingly."""
        self.mo_dialog.initialize_dialog()

    def show_surface_3d_dialog(self) -> None:
        """Check if cube file has been loaded and perform actions accordingly."""
        self.surface_3d_dialog.initialize_dialog()

    def show_structure_customizer_dialog(self) -> None:
        """Show the structure customizer dialog."""
        self.structure_customizer_dialog.bonds = self.structure_widget.bonds
        self.structure_customizer_dialog.set_bonds(self.structure_widget.bonds)
        self.structure_customizer_dialog.show()

    def toggle_axes(self) -> None:
        """Toggle the axes."""
        self.structure_widget.toggle_axes()
        self.update_action_texts()

    def update_action_texts(self) -> None:
        """Update the texts of the menu actions."""
        text_axes = "Hide Axes" if self.structure_widget.draw_axes else "Show Axes"
        text_projection = (
            "Perspective Projection" if self.structure_widget.orthographic_projection else "Orthographic Projection"
        )
        text_unit_cell_boundaries = (
            "Hide Unit Cell Boundaries"
            if self.structure_widget.draw_unit_cell_boundaries
            else "Show Unit Cell Boundaries"
        )
        self.ui.actionToggle_Axes.setText(QCoreApplication.translate("MainWindow", text_axes, None))
        self.ui.actionToggle_Projection.setText(QCoreApplication.translate("MainWindow", text_projection, None))
        self.ui.actionToggle_UnitCellBoundaries.setText(
            QCoreApplication.translate("MainWindow", text_unit_cell_boundaries, None),
        )

    def show_init_xyz(self) -> None:
        """Read the file from terminal arguments."""
        file_name = sys.argv[1]

        self.load_molecules(file_name)

    def show_file_open_dialog(self) -> None:
        """Select a file in the file open dialog."""
        file_name = QFileDialog.getOpenFileName(
            self,
            "Import structure from file",
            dir=".",
        )[0]
        if file_name == "":
            return
        self.load_molecules(file_name)

    def load_molecules(self, path: PathLike | str) -> None:
        """Load the molecules from path.

        :param path: input file path
        """
        importer = GeneralImporter(path)
        self.mols = importer.load()

        self.structure_widget.set_structure([self.mols.get_current_mol()])

        if self.mols.num_mols > 1:
            self.ui.actionOpen_Trajectory_Dialog.setEnabled(ENABLED)
            self.trajectory_dialog.show()
            self.trajectory_dialog.initial_energy_plot()
            self.trajectory_dialog.set_slider_range()
            return

        self.trajectory_dialog.reset()
        self.trajectory_dialog.close()
        self.ui.actionOpen_Trajectory_Dialog.setEnabled(DISABLED)

    def export_structure(self) -> None:
        """Save structure to file."""
        if not self.structure_widget.structures:
            return
        file_name = QFileDialog.getSaveFileName(
            self,
            "Export structure to file",
            f"{Path.home()}",
            "*",
        )[0]
        if file_name == "":
            return
        exporter = GeneralExporter(file_name)
        exporter.write_structure(self.structure_widget.structure)

    def export_camera_settings(self) -> None:
        """Export camera settings to .npz file."""
        file_name = QFileDialog.getSaveFileName(
            self,
            "Export camera settings to file",
            ".",
            ".json",
        )[0]
        if file_name == "":
            return
        try:
            self.structure_widget.export_camera_settings(file_name)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"Error: {e}")

    def import_camera_settings(self) -> None:
        """Import camera settings from .npz file."""
        file_name = QFileDialog.getOpenFileName(
            self,
            "Import camera settings from file",
            ".",
            "*.json",
        )[0]
        if file_name == "":
            return
        try:
            self.structure_widget.import_camera_settings(file_name)
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"Error: {e}")

    def show_measurement_dialog(self) -> None:
        """Show the measurement dialog."""
        if len(self.structure_widget.structures) == 1:
            self.measurement_dialog.show()

    def show_builder_dialog(self) -> None:
        """Show the builder dialog."""
        self.builder_dialog.show()

    def edit_supercell_dims(self) -> bool:
        """Open dialog window to edit supercell dimensions."""
        if not isinstance(self.structure_widget.structures[0], Crystal):
            # insert error message?
            return False
        crystal = self.structure_widget.structures[0]
        supercell_dims = crystal.supercell_dims
        self.supercell_dialog.show()
        self.supercell_dialog.get_supercell_dims(supercell_dims)
        # check if supercell dimensions have successfully been passed (i.e., all are >0)
        if sum(1 for component in supercell_dims if component <= 0):
            return False
        crystal.make_supercell(supercell_dims)
        self.structure_widget.set_structure([crystal])
        return True

    def show_poscar(self) -> bool | None:
        """Read poscar file and shows the first structure in this file."""
        file_name = QFileDialog.getOpenFileName(
            self,
            caption="Open POSCAR file",
            dir=".",
            filter="POSCAR Files (*)",
        )[0]
        if file_name == "":
            return None

        importer = PoscarImporter(file_name)
        crystals = importer.load()

        if not isinstance(crystals, Crystals):
            crystal = crystals.get_current_mol()
            error_message = crystal[1]
            msg_box = QMessageBox()
            msg_box.setText(error_message)
            msg_box.exec()
            return False
        self.structure_widget.set_structure(structs=[crystals.get_current_mol()])
        return True
