"""This module contains the test cases for the main window of the application."""

from __future__ import annotations

from typing import TYPE_CHECKING

from molara.Gui.builder import BuilderDialog
from molara.Gui.crystal_dialog import CrystalDialog
from molara.Gui.main_window import MainWindow
from molara.Gui.measuring_tool_dialog import MeasurementDialog
from molara.Gui.structure_widget import StructureWidget
from molara.Gui.trajectory_dialog import TrajectoryDialog
from molara.Gui.ui_form import Ui_MainWindow
from molara.Structure.crystal import Crystal
from molara.Structure.crystals import Crystals
from molara.Structure.molecule import Molecule
from molara.Structure.molecules import Molecules
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QMenuBar

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

import sys
from unittest import mock


class WorkaroundTestMainWindow:
    """This class contains the tests for the MainWindow class.

    It does not inherit from unittest.TestCase, because that does not work with pytest-qt.
    """

    def __init__(self, qtbot: QtBot) -> None:
        """Instantiates the MainWindow object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.app = QApplication([]) if QApplication.instance() is None else QApplication.instance()
        self.window = MainWindow()

    def test_init(self) -> None:
        """Write test code to verify the behavior of the __init__ method."""
        assert isinstance(self.window, MainWindow)
        assert isinstance(self.window.trajectory_dialog, TrajectoryDialog)
        assert isinstance(self.window.crystal_dialog, CrystalDialog)
        assert isinstance(self.window.measurement_dialog, MeasurementDialog)
        assert isinstance(self.window.builder_dialog, BuilderDialog)
        assert isinstance(self.window.mols, Molecules)
        assert isinstance(self.window.structure_widget, StructureWidget)
        # Add more assertions for the __init__ method

    def test_ui(self) -> None:
        """Write test code to verify that the ui has been set up correctly."""
        assert isinstance(self.window.ui, Ui_MainWindow)
        ui = self.window.ui
        assert isinstance(ui.openGLWidget, StructureWidget)
        assert self.window.structure_widget is ui.openGLWidget
        # test that all the actions have been set up
        assert isinstance(ui.quit, QAction)
        assert isinstance(ui.action_xyz, QAction)
        assert isinstance(ui.actionCenter_Molecule, QAction)
        assert isinstance(ui.actionReset_View, QAction)
        assert isinstance(ui.actionto_x_axis, QAction)
        assert isinstance(ui.actionto_y_axis, QAction)
        assert isinstance(ui.actionto_z_axis, QAction)
        assert isinstance(ui.actionDraw_Axes, QAction)
        assert isinstance(ui.actionCreate_Lattice, QAction)
        assert isinstance(ui.actionRead_POSCAR, QAction)
        assert isinstance(ui.action_coord, QAction)
        assert isinstance(ui.actionOpen_Trajectory_Dialog, QAction)
        assert isinstance(ui.actionImport, QAction)
        assert isinstance(ui.actionToggle_Bonds, QAction)
        assert isinstance(ui.actionMeasure, QAction)
        assert isinstance(ui.actionSupercell, QAction)
        assert isinstance(ui.actionBuilder, QAction)
        assert isinstance(ui.actionExport, QAction)
        assert isinstance(ui.actionExport_Snapshot, QAction)
        assert isinstance(ui.actionToggle_UnitCellBoundaries, QAction)

        # test that the menus have been set up correctly.
        assert isinstance(ui.menubar, QMenuBar)
        assert isinstance(ui.menuFile, QMenu)
        assert isinstance(ui.menuEdit, QMenu)
        assert isinstance(ui.menuTools, QMenu)
        assert isinstance(ui.menubar.actions(), list)
        assert ui.menuFile.menuAction() in ui.menubar.actions()
        assert ui.menuEdit.menuAction() in ui.menubar.actions()
        assert ui.menuTools.menuAction() in ui.menubar.actions()
        assert ui.menuCrystal.menuAction() in ui.menubar.actions()
        assert isinstance(ui.menuEdit, QMenu)
        assert isinstance(ui.menuRotate, QMenu)
        assert isinstance(ui.menuCrystal, QMenu)

        self.test_ui_file_menu()
        self.test_ui_edit_menu()
        self.test_ui_crystal_menu()

    def test_ui_file_menu(self) -> None:
        """Tests the file menu of the ui."""
        ui = self.window.ui
        assert isinstance(ui.menuFile.actions(), list)
        assert ui.quit in ui.menuFile.actions()
        assert ui.actionImport in ui.menuFile.actions()
        assert ui.actionExport in ui.menuFile.actions()
        assert ui.actionExport_Snapshot in ui.menuFile.actions()

    def test_ui_edit_menu(self) -> None:
        """Tests the edit menu of the ui."""
        ui = self.window.ui
        assert isinstance(ui.menuEdit.actions(), list)
        assert ui.actionReset_View in ui.menuEdit.actions()
        assert ui.actionCenter_Molecule in ui.menuEdit.actions()
        assert ui.actionToggle_Bonds in ui.menuEdit.actions()
        assert ui.actionOpen_Trajectory_Dialog in ui.menuEdit.actions()
        assert ui.menuRotate.menuAction() in ui.menuEdit.actions()
        assert ui.actionDraw_Axes in ui.menuEdit.actions()
        # menu "view"->rotate
        assert isinstance(ui.menuRotate.actions(), list)
        assert ui.actionto_x_axis in ui.menuRotate.actions()
        assert ui.actionto_y_axis in ui.menuRotate.actions()
        assert ui.actionto_z_axis in ui.menuRotate.actions()

    def test_ui_crystal_menu(self) -> None:
        """Tests the crystal menu of the ui."""
        ui = self.window.ui
        assert isinstance(ui.menuCrystal.actions(), list)
        assert ui.actionRead_POSCAR in ui.menuCrystal.actions()
        assert ui.actionCreate_Lattice in ui.menuCrystal.actions()
        assert ui.actionSupercell in ui.menuCrystal.actions()
        assert ui.actionToggle_UnitCellBoundaries in ui.menuCrystal.actions()

    def tearDown(self) -> None:
        """Clean up the test."""
        self.window.close()
        QApplication.instance().shutdown() if QApplication.instance() is not None else None

    def test_structure_widget(self) -> None:
        """Write test code to verify the behavior of the structure_widget property."""
        structure_widget = self.window.structure_widget
        assert structure_widget is not None

    def test_show_builder_dialog(self) -> None:
        """Write test code to verify the behavior of show_measurement_dialog method."""
        assert not self.window.builder_dialog.isVisible()
        ui = self.window.ui
        ui.actionBuilder.triggered.emit()
        assert self.window.builder_dialog.isVisible()
        self.window.builder_dialog.reject()
        assert not self.window.builder_dialog.isVisible()

    def test_show_crystal_dialog(self) -> None:
        """Write test code to verify the behavior of show_crystal_dialog method."""
        assert not self.window.crystal_dialog.isVisible()
        ui = self.window.ui
        ui.actionCreate_Lattice.triggered.emit()
        assert self.window.crystal_dialog.isVisible()
        self.window.crystal_dialog.reject()
        assert not self.window.crystal_dialog.isVisible()

    def test_show_init_xyz(self) -> None:
        """Write test code to verify the behavior of show_init_xyz method."""
        testargs = ["molara", "examples/xyz/pentane.xyz"]
        with mock.patch.object(sys, "argv", testargs):
            window = self.window
            window.show_init_xyz()
            assert isinstance(window.mols, Molecules)
            assert isinstance(window.structure_widget.structure, Molecule)
            assert window.structure_widget.structure_is_set
            assert window.structure_widget.structure is window.mols.get_current_mol()

    def test_load_molecules(self) -> None:
        """Write test code to verify the behavior of load_molecules method."""
        window = self.window
        # test coord file
        window.load_molecules("examples/coord/coord1.coord")
        assert isinstance(window.mols, Molecules)
        assert isinstance(window.structure_widget.structure, Molecule)
        assert window.structure_widget.structure_is_set
        assert window.structure_widget.structure is window.mols.get_current_mol()
        # test xyz file
        window.load_molecules("examples/xyz/ferrocene.xyz")
        assert isinstance(window.mols, Molecules)
        assert isinstance(window.structure_widget.structure, Molecule)
        assert window.structure_widget.structure_is_set
        assert window.structure_widget.structure is window.mols.get_current_mol()
        # test POSCAR file
        window.load_molecules("examples/POSCAR/Ba2YCu3O7_POSCAR")
        assert isinstance(window.mols, Crystals)
        assert isinstance(window.structure_widget.structure, Crystal)
        assert window.structure_widget.structure_is_set
        assert window.structure_widget.structure is window.mols.get_current_mol()

    def test_show_measurement_dialog(self) -> None:
        """Write test code to verify the behavior of show_measurement_dialog method.

        a test where a molecule has been loaded must be executed before this test! (see test_load_molecules)
        """
        window = self.window
        ui = window.ui
        measurement_dialog = window.measurement_dialog
        assert not measurement_dialog.isVisible()
        ui.actionMeasure.triggered.emit()
        assert measurement_dialog.isVisible()
        measurement_dialog.reject()
        assert not measurement_dialog.isVisible()

    def test_show_trajectory_dialog(self) -> None:
        """Write test code to verify the behavior of show_trajectory_dialog method."""
        window = self.window
        window.load_molecules("examples/xyz/opt.xyz")
        # trajectory dialog should be opened since a trajectory has been loaded
        assert self.window.trajectory_dialog.isVisible()
        self.window.trajectory_dialog.reject()
        assert not self.window.trajectory_dialog.isVisible()
        # now open trajectory dialog by triggering the menu action
        window.ui.actionOpen_Trajectory_Dialog.triggered.emit()
        assert self.window.trajectory_dialog.isVisible()
        self.window.trajectory_dialog.reject()
        assert not self.window.trajectory_dialog.isVisible()

    # def test_show_file_open_dialog(self) -> None:
    #     """Write test code to verify the behavior of show_file_open_dialog method."""

    # def test_edit_supercell_dims(self) -> None:
    #     """Write test code to verify the behavior of edit_supercell_dims method."""

    # def test_show_poscar(self) -> None:
    #     """Write test code to verify the behavior of show_poscar method."""
