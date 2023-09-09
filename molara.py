#!/usr/bin/env python3

import sys

from PySide6.QtGui import QSurfaceFormat
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from Gui.ui_form import Ui_MainWindow
from Gui.CrystalDialog import CrystalDialog
from Molecule.Molecule import read_xyz
from Molecule.Crystal import *
from Molecule.Atom import *

format = QSurfaceFormat()
format.setVersion(4, 1)
format.setProfile(QSurfaceFormat.CoreProfile)
QSurfaceFormat.setDefaultFormat(format)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def show_xyz(self):
        fileName = QFileDialog.getOpenFileName(self, "Open .xyz file", "/home", "Image Files (*.xyz)")
        mol = read_xyz(fileName[0])
        widget.ui.openGLWidget.set_molecule(mol)
    
    def create_a_crystal(self):
        latconst = 5.45
        atoms = ['Ce', 'Ce', 'Ce', 'Ce', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']
        positions = np.array([[0, 0, 0], [.5, .5, 0], [.5, 0, .5], [0, .5, .5],
          [.25, .25, .25],
          [.75, .25, .25], [.25, .75, .25], [.25, .25, .75],
          [.75, .75, .25], [.75, .25, .75], [.25, .75, .75],
          [.75, .75, .75]], dtype=np.float64)
        atoms = np.array([element_symbol_to_atomic_number(symb) for symb in atoms], dtype=int)
        mycrystal = Crystal(atoms, positions,
          latconst*np.array([[1, 0, 0], [0, 1, 0], [.25, .25, .8]]), supercell_dimensions=np.array([2, 2, 2]))
        widget.ui.openGLWidget.set_molecule(mycrystal)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    crystal_dialog = CrystalDialog()
    widget.setWindowTitle('Molara')
    widget.show()
    widget.ui.action_xyz.triggered.connect(widget.show_xyz)
    widget.ui.actionReset_View.triggered.connect(widget.ui.openGLWidget.reset_view)
    widget.ui.actionDraw_Axes.triggered.connect(widget.ui.openGLWidget.toggle_axes)
    widget.ui.actionCenter_Molecule.triggered.connect(widget.ui.openGLWidget.center_molecule)
    widget.ui.actionCreate_Lattice.triggered.connect(crystal_dialog.show)
    widget.ui.quit.triggered.connect(widget.close)
    sys.exit(app.exec())
