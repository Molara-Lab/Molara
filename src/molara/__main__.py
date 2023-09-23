import signal
import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from molara.Gui.CrystalDialog import CrystalDialog

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from molara.Gui.ui_form import Ui_MainWindow
from molara.Molecule.Crystal import Crystal
from molara.Molecule.Molecule import read_coord, read_xyz


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
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)

        def show_init_xyz(self):
            """
            read the file from terminal arguments

            """
            fileName = sys.argv[1]
            mol = read_xyz(fileName)
            widget.ui.openGLWidget.set_molecule(mol)

        def show_xyz(self):
            fileName = QFileDialog.getOpenFileName(self, "Open .xyz file", "/home", "Image Files (*.xyz)")
            mol = read_xyz(fileName[0])
            widget.ui.openGLWidget.set_molecule(mol)

        def show_coord(self):
            fileName = QFileDialog.getOpenFileName(self, "Open coord file", "/home", "Image Files (*)")
            mol = read_coord(fileName[0])
            widget.ui.openGLWidget.set_molecule(mol)

        def show_POSCAR(self):
            filename = QFileDialog.getOpenFileName(self, "Open POSCAR file", "/home", "POSCAR Files (*)")
            crystal = Crystal.from_POSCAR(filename[0])
            if not isinstance(crystal, Crystal):
                error_message = crystal[1]
                msgBox = QMessageBox()
                msgBox.setText(error_message)
                msgBox.exec()
                return False
            widget.ui.openGLWidget.set_molecule(crystal)
            return True

        def disable_bonds(self):
            if self.ui.openGLWidget.molecule:
                self.ui.openGLWidget.molecule.draw_bonds = not self.ui.openGLWidget.molecule.draw_bonds
                self.ui.openGLWidget.update()


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
    widget.ui.actionRead_POSCAR.triggered.connect(widget.show_POSCAR)
    widget.ui.actionCreate_Lattice.triggered.connect(crystal_dialog.show)
    widget.ui.actionDisable_Bonds.triggered.connect(widget.disable_bonds)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
