"""Virtual (i.e., hidden) window for rendering a structure for snapshot export."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QWidget

from molara.gui.ui_virtual_rendering_window import Ui_Form


class VirtualRenderingWindow(QWidget):
    """Virtual (i.e., hidden) window for rendering a structure for snapshot export."""

    def __init__(self, parent: QMainWindow) -> None:
        """Instantiate the virtual rendering window object."""
        super().__init__(
            parent,
        )
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.main_window = parent
        self.structure_widget = self.ui.openGLWidget

    def export_image(self, filename: str, custom_geometry: tuple[int, int]) -> None:
        """Export the image of the structure to the given filename.

        :param filename: the filename for the exported image
        :param custom_geometry: custom geometry (width, height) for the exported image
        """
        self.structure_widget.grabFramebuffer().save(filename)

        # rendering part
        main_structure_widget = self.main_window.structure_widget
        virtual_structure_widget = self.structure_widget

        # the window must be shown to render (apparently) but can immediately be hidden again
        self.show()
        virtual_structure_widget.adopt_config(main_structure_widget, custom_geometry)
        self.hide()
        virtual_structure_widget.update()
        virtual_structure_widget.grabFramebuffer().save(filename)
