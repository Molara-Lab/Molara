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
from molara.Structure.molecules import Molecules
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QMenuBar

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot

import sys

import pytest


@pytest.mark.skipif(sys.platform == "win32", reason="Test is not compatible with Windows")
def test_main_window(qtbot: QtBot) -> None:
    """Creates a MainWindow object.

    :param qtbot: provides methods to simulate user interaction
    """
    workaround_test_main_window = WorkaroundTestMainWindow(qtbot)
    workaround_test_main_window.test_init()
    workaround_test_main_window.test_ui()
    workaround_test_main_window.test_structure_widget()
    workaround_test_main_window.test_show_builder_dialog()
    workaround_test_main_window.test_show_crystal_dialog()
    workaround_test_main_window.tearDown()


class WorkaroundTestMainWindow:
    """This class contains the tests for the MainWindow class.

    It does not inherit from unittest.TestCase, because that does not work with pytest-qt.
    """

    def __init__(self, qtbot: QtBot) -> None:
        """Instantiates the MainWindow object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.app = QApplication.instance() if QApplication.instance() else QApplication([])
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
        assert isinstance(ui.actionAdd_unit_cell_boundaries, QAction)

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
        assert ui.actionAdd_unit_cell_boundaries in ui.menuCrystal.actions()

    def tearDown(self) -> None:
        """Clean up the test."""
        self.app.quit()
        self.window.close()

    def test_structure_widget(self) -> None:
        """Write test code to verify the behavior of the structure_widget property."""
        structure_widget = self.window.structure_widget
        assert structure_widget is not None

    # def test_show_init_xyz(self) -> None:
    #     """Write test code to verify the behavior of show_init_xyz method."""

    # def test_show_file_open_dialog(self) -> None:
    #     """Write test code to verify the behavior of show_file_open_dialog method."""

    # def test_load_molecules(self) -> None:
    #    """Write test code to verify the behavior of load_molecules method."""

    # def test_export_structure(self) -> None:
    #     """Write test code to verify the behavior of export_structure method."""

    def test_show_builder_dialog(self) -> None:
        """Write test code to verify the behavior of show_measurement_dialog method."""
        assert not self.window.builder_dialog.isVisible()
        # ui = self.window.ui
        # ui.actionBuilder.triggered.emit()
        # assert self.window.builder_dialog.isVisible()
        # self.window.builder_dialog.reject()
        # self.window.structure_widget.doneCurrent()

    def test_show_crystal_dialog(self) -> None:
        """Write test code to verify the behavior of show_crystal_dialog method."""
        assert not self.window.crystal_dialog.isVisible()
        ui = self.window.ui
        ui.actionCreate_Lattice.triggered.emit()
        assert self.window.crystal_dialog.isVisible()
        self.window.crystal_dialog.reject()

    # def test_edit_supercell_dims(self) -> None:
    #     """Write test code to verify the behavior of edit_supercell_dims method."""

    # def test_show_poscar(self) -> None:
    #     """Write test code to verify the behavior of show_poscar method."""
