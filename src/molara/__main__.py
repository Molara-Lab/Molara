import signal
import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from molara.Gui.crystal_dialog import CrystalDialog

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from molara.Gui.ui_form import UiMainwindow
from molara.Molecule.crystal import Crystal
from molara.Molecule.molecule import read_coord, read_xyz


def main() -> None:
    format = QSurfaceFormat()
    format.setVersion(4, 1)
    format.setSamples(4)
    format.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(format)

    def sigint_handler(*args):
        app.quit()

    class MainWindow(QMainWindow):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.ui = UiMainwindow()
            self.ui.setup_ui(self)

        def show_init_xyz(self):
            """Read the file from terminal arguments."""
            file_name = sys.argv[1]
            mol = read_xyz(file_name)
            widget.ui.openGLWidget.set_molecule(mol)

        def show_xyz(self):
            file_name = QFileDialog.getOpenFileName(self, "Open .xyz file", "/home", "Image Files (*.xyz)")
            mol = read_xyz(file_name[0])
            widget.ui.openGLWidget.set_molecule(mol)

        def show_coord(self):
            file_name = QFileDialog.getOpenFileName(self, "Open coord file", "/home", "Image Files (*)")
            mol = read_coord(file_name[0])
            widget.ui.openGLWidget.set_molecule(mol)

        def show_poscar(self):
            filename = QFileDialog.getOpenFileName(self, "Open POSCAR file", "/home", "POSCAR Files (*)")
            crystal = Crystal.from_poscar(filename[0])
            if not isinstance(crystal, Crystal):
                error_message = crystal[1]
                msg_box = QMessageBox()
                msg_box.setText(error_message)
                msg_box.exec()
                return False
            widget.ui.openGLWidget.set_molecule(crystal)
            return True

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
    widget.ui.action_coord.triggered.connect(widget.show_coord)
    widget.ui.actionReset_View.triggered.connect(widget.ui.openGLWidget.reset_view)
    widget.ui.actionDraw_Axes.triggered.connect(widget.ui.openGLWidget.toggle_axes)
    widget.ui.actionCenter_Molecule.triggered.connect(widget.ui.openGLWidget.center_molecule)
    widget.ui.quit.triggered.connect(widget.close)
    widget.ui.actionRead_POSCAR.triggered.connect(widget.show_poscar)
    widget.ui.actionCreate_Lattice.triggered.connect(crystal_dialog.show)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
