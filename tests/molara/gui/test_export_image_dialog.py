"""Test the MeasurementDialog class."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from molara.Gui.main_window import MainWindow
    from pytestqt.qtbot import QtBot

import time


class WorkaroundTestExportImageDialog:
    """Contains the tests for the ExportImageDialog class.

    It does not inherit from unittest.TestCase, because that does not work with pytest-qt.
    """

    def __init__(self, qtbot: QtBot, main_window: MainWindow) -> None:
        """Instantiate the WorkaroundTestMeasurementDialog object.

        :param qtbot: provides methods to simulate user interaction
        """
        self.qtbot = qtbot
        self.main_window = main_window
        self.export_image_dialog = main_window.export_image_dialog

    def run_tests(self) -> None:
        """Run the tests."""
        self._test_init()
        self._test_show_dialog()
        self._test_change_width()
        self._test_change_height()
        self._test_export_image()

    def _test_init(self) -> None:
        """Test the initialization of the ExportImageDialog class."""
        assert self.export_image_dialog is not None
        assert self.export_image_dialog.main_window == self.main_window

    def _test_show_dialog(self) -> None:
        """Test showing the dialog."""
        assert not self.export_image_dialog.isVisible()
        ui_main = self.main_window.ui
        ui_main.actionExport_Snapshot.trigger()
        assert self.export_image_dialog.isVisible()

        structure_widget = self.main_window.structure_widget
        width, height = structure_widget.width(), structure_widget.height()
        assert self.export_image_dialog.ui.widthSpinBox.value() == width
        assert self.export_image_dialog.ui.heightSpinBox.value() == height
        ui_export_image = self.export_image_dialog.ui
        assert ui_export_image.filenameInput.text().startswith(f"{Path.home()}/molara_image_")

        self.export_image_dialog.reject()
        assert not self.export_image_dialog.isVisible()

    def _test_change_width(self) -> None:
        """Test changing the width of the image."""
        ui = self.export_image_dialog.ui
        height_structurewidget = self.main_window.structure_widget.height()
        width_structurewidget = self.main_window.structure_widget.width()
        new_width = 194
        ui.widthSpinBox.setValue(new_width)
        assert ui.heightSpinBox.value() == new_width * height_structurewidget // width_structurewidget

    def _test_change_height(self) -> None:
        """Test changing the height of the image."""
        ui = self.export_image_dialog.ui
        height_structurewidget = self.main_window.structure_widget.height()
        width_structurewidget = self.main_window.structure_widget.width()
        new_height = 491
        ui.heightSpinBox.setValue(new_height)
        assert ui.widthSpinBox.value() == new_height * width_structurewidget // height_structurewidget

    def _test_export_image(self) -> None:
        """Test exporting an image."""
        filename = f"tmpfile_{time.time():1.0f}.png"
        ui = self.export_image_dialog.ui
        ui.filenameInput.setText(filename)
        assert ui.filenameInput.text() == filename

        assert not Path(filename).exists()
        ui.buttonBox.accepted.emit()
        assert Path(filename).exists()
        Path(filename).unlink()
        assert not Path(filename).exists()
