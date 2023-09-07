import sys

from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py

from .Gui.ui_form import Ui_MainWindow
from .Molecule.Molecule import read_xyz,read_coord

def main() -> None:

    format = QSurfaceFormat()
    format.setVersion(4, 1)
    format.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(format)

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

    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.setWindowTitle('Molara')
    widget.show()

    if len(sys.argv) > 1:
        widget.show_init_xyz()

    widget.ui.action_xyz.triggered.connect(widget.show_xyz)
    widget.ui.actionReset_View.triggered.connect(widget.ui.openGLWidget.reset_view)
    widget.ui.actionDraw_Axes.triggered.connect(widget.ui.openGLWidget.toggle_axes)
    widget.ui.actionCenter_Molecule.triggered.connect(widget.ui.openGLWidget.center_molecule)
    widget.ui.quit.triggered.connect(widget.close)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
