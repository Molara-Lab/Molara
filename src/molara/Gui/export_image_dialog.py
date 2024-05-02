"""Dialog for exporting a snapshot of the rendered structure."""

from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtWidgets import QDialog, QMainWindow

from molara.Gui.ui_export_image_dialog import Ui_Dialog
from molara.Gui.virtual_rendering_window import VirtualRenderingWindow


class ExportImageDialog(QDialog):
    """Dialog for exporting a snapshot of the rendered structure."""

    def __init__(self, parent: QMainWindow) -> None:
        """Instantiate the dialog object."""
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.tabWidget.setTabEnabled(1, False)  # noqa: FBT003 (disable the "Advanced" tab for now)

        self.main_window = parent

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
