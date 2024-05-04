"""Dialog for exporting a snapshot of the rendered structure."""

from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtWidgets import QDialog, QFileDialog, QMainWindow

from molara.Gui.ui_export_image_dialog import Ui_Dialog
from molara.Gui.virtual_rendering_window import VirtualRenderingWindow


class ExportImageDialog(QDialog):
    """Dialog for exporting a snapshot of the rendered structure."""

    def __init__(self, parent: QMainWindow) -> None:
        """Instantiate the dialog object."""
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.set_event_connections()

        self.main_window = parent

        # temporary adjustments for the dialog until features are implemented
        self.ui.tabWidget.setTabEnabled(1, False)  # noqa: FBT003 (disable the "Advanced" tab for now)
        self.ui.checkBox.setChecked(True)
        self.ui.checkBox.setDisabled(True)

    def set_event_connections(self) -> None:
        """Connect the dialog events to functions."""
        self.ui.widthSpinBox.valueChanged.connect(self.update_height)
        self.ui.heightSpinBox.valueChanged.connect(self.update_width)
        self.ui.pushButton.clicked.connect(self.choose_filename)

    def choose_filename(self) -> None:
        """Open a file dialog to choose a filename."""
        filename, suffix = QFileDialog.getSaveFileName(
            self,
            "Export Image",
            ".",
            "*.png;;*.jpg",
        )
        if not filename:
            return
        if not filename.endswith(suffix[1:]):
            filename += suffix[1:]
        self.ui.filenameInput.setText(filename)

    def update_height(self) -> None:
        """Update the height value in the form."""
        width = self.ui.widthSpinBox.value()
        height = self.main_window.structure_widget.height() * width // self.main_window.structure_widget.width()
        self.ui.heightSpinBox.blockSignals(True)  # noqa: FBT003 (block signals to prevent infinite loop)
        self.ui.heightSpinBox.setValue(height)
        self.ui.heightSpinBox.blockSignals(False)  # noqa: FBT003 (block signals to prevent infinite loop)

    def update_width(self) -> None:
        """Update the width value in the form."""
        height = self.ui.heightSpinBox.value()
        width = self.main_window.structure_widget.width() * height // self.main_window.structure_widget.height()
        self.ui.widthSpinBox.blockSignals(True)  # noqa: FBT003 (block signals to prevent infinite loop)
        self.ui.widthSpinBox.setValue(width)
        self.ui.widthSpinBox.blockSignals(False)  # noqa: FBT003 (block signals to prevent infinite loop)

    def show_dialog(self) -> None:
        """Show the dialog and set default values in the form."""
        self.ui.widthSpinBox.setValue(self.main_window.structure_widget.width())
        self.ui.heightSpinBox.setValue(self.main_window.structure_widget.height())
        self.ui.filenameInput.setText(f"{Path.cwd()}/molara_image_{time.time():1.0f}.png")
        self.show()

    def accept(self) -> None:
        """Export the image and close the dialog."""
        # gather export specifics
        width, height = int(self.ui.widthSpinBox.value()), int(self.ui.heightSpinBox.value())
        virtual_rendering_window = VirtualRenderingWindow(self.main_window)
        virtual_rendering_window.export_image(self.ui.filenameInput.text(), custom_geometry=(width, height))
        del virtual_rendering_window
