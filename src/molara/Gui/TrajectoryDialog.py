from contextlib import suppress

import numpy as np
from PySide6.QtWidgets import QDialog, QMainWindow, QTableWidgetItem
from PySide6.QtCore import QTime,QTimer

from molara.Gui.ui_trajectory import Ui_Dialog
from molara.Molecule.Atom import element_symbol_to_atomic_number
from molara.Molecule.Molecules import Molecules
from molara.Molecule.Molecule import Molecule


class TrajectoryDialog(QDialog):
    """
    Dialog for trajectories.
    """

    def __init__(self, parent: QMainWindow = None):
        super().__init__(
            parent
        )  # main window widget is passed as a parent, so dialog is closed if main window is closed.
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.timer = QTimer(self)
        self.ui.checkBox.stateChanged.connect(self.show_trajectory)
        self.ui.pushButton.clicked.connect(self.get_prev_mol)
        self.ui.pushButton_2.clicked.connect(self.get_prev_mol)

    def show_trajectory(self):
        
        if self.ui.checkBox.isChecked():
            self.timer.start(25)
            self.timer.timeout.connect(self.update_molecule)

        else:
            
            self.timer.stop()
                
        return 
    
    def get_next_mol(self):
        self.parent().mols.get_next_mol
        self.update_molecule()
        return
    
    def get_prev_mol(self):
        self.parent().mols.get_previous_mol
        self.update_molecule()
        return
    
    def update_molecule(self):

        self.parent().ui.openGLWidget.delete_molecule()

        self.parent().ui.openGLWidget.set_molecule(self.parent().mols.get_next_mol())

        return 