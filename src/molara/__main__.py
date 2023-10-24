import signal
import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication

from molara.Gui.crystal_dialog import CrystalDialog

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from molara.MainWindow.main_window import MainWindow


def main() -> None:
    format = QSurfaceFormat()
    format.setVersion(4, 1)
    format.setSamples(4)
    format.setProfile(QSurfaceFormat.CoreProfile)  # type: ignore[attr-defined]
    QSurfaceFormat.setDefaultFormat(format)

    def sigint_handler(*args):
        app.quit()

    signal.signal(signal.SIGINT, sigint_handler)
    app = QApplication(sys.argv)
    timer = QTimer()
    timer.start(500)  # You may change this if you wish.
    timer.timeout.connect(lambda: None)
    widget = MainWindow()
    crystal_dialog = CrystalDialog(widget)  # pass widget as parent
    widget.setWindowTitle("Molara")
    widget.show()

    if len(sys.argv) > 1:
        widget.show_init_xyz()

    widget.ui.action_xyz.triggered.connect(widget.show_xyz)
    widget.ui.actioncoord.triggered.connect(widget.show_coord)
    widget.ui.actionReset_View.triggered.connect(widget.ui.openGLWidget.reset_view)
    widget.ui.actionDraw_Axes.triggered.connect(widget.ui.openGLWidget.toggle_axes)
    widget.ui.actionCenter_Molecule.triggered.connect(widget.ui.openGLWidget.center_molecule)
    widget.ui.quit.triggered.connect(widget.close)
    widget.ui.actionRead_POSCAR.triggered.connect(widget.show_poscar)
    widget.ui.actionCreate_Lattice.triggered.connect(crystal_dialog.show)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
