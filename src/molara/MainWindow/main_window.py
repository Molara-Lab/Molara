import sys
from molara.Molecule.molecule import read_coord, read_xyz
from molara.Gui.ui_form import Ui_MainWindow
from molara.Molecule.crystal import Crystal
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def show_init_xyz(self) -> None:
        """Read the file from terminal arguments."""
        file_name = sys.argv[1]
        mol = read_xyz(file_name)
        self.ui.openGLWidget.set_molecule(mol)

    def show_xyz(self) -> None:
        file_name = QFileDialog.getOpenFileName(self, "Open .xyz file", "/home", "Image Files (*.xyz)")
        mol = read_xyz(file_name[0])
        self.ui.openGLWidget.set_molecule(mol)

    def show_coord(self) -> None:
        file_name = QFileDialog.getOpenFileName(self, "Open coord file", "/home", "Image Files (*)")
        mol = read_coord(file_name[0])
        self.ui.openGLWidget.set_molecule(mol)

    def show_poscar(self) -> bool:
        filename = QFileDialog.getOpenFileName(self, "Open POSCAR file", "/home", "POSCAR Files (*)")
        crystal = Crystal.from_poscar(filename[0])
        if not isinstance(crystal, Crystal):
            error_message = crystal[1]
            msg_box = QMessageBox()
            msg_box.setText(error_message)
            msg_box.exec()
            return False
        self.ui.openGLWidget.set_molecule(crystal)
        return True
