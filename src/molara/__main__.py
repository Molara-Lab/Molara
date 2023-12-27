"""The main entry point for the application."""

from __future__ import annotations

import signal
import sys
from typing import TYPE_CHECKING

from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from molara.Gui.ui_form import Ui_MainWindow
from molara.MainWindow.main_window import MainWindow

if TYPE_CHECKING:
    from types import FrameType


def main() -> None:
    """Run the application."""
    _format = QSurfaceFormat()
    _format.setVersion(4, 1)
    _format.setSamples(4)
    _format.setProfile(QSurfaceFormat.CoreProfile)  # type: ignore[attr-defined]
    QSurfaceFormat.setDefaultFormat(_format)

    def sigint_handler(signum: int, frame: FrameType | None) -> None:  # noqa: ARG001
        app.quit()

    signal.signal(signal.SIGINT, sigint_handler)
    app = QApplication(sys.argv)

    widget = MainWindow()

    widget.setWindowTitle("Molara")

    widget.show()

    if len(sys.argv) > 1:
        widget.show_init_xyz()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
