"""The main entry point for the application."""

from __future__ import annotations

import signal
import sys

from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from molara.Gui.main_window import MainWindow

__copyright__ = "Copyright 2024, Molara"


def main() -> None:
    """Run the application."""
    _format = QSurfaceFormat()
    _format.setVersion(4, 1)
    _format.setSamples(4)
    _format.setProfile(QSurfaceFormat.CoreProfile)  # type: ignore[attr-defined]
    QSurfaceFormat.setDefaultFormat(_format)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)

    widget = MainWindow()

    widget.setWindowTitle("Molara")

    widget.show()

    if len(sys.argv) > 1:
        widget.show_init_xyz()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
