from contextlib import suppress

import matplotlib as mpl
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtCore import QTime, QTimer
from PySide6.QtWidgets import QDialog, QGraphicsScene, QMainWindow, QTableWidgetItem, QVBoxLayout, QWidget

from molara.Gui.ui_trajectory import Ui_Dialog
from molara.Molecule.Atom import element_symbol_to_atomic_number
from molara.Molecule.Molecule import Molecule
from molara.Molecule.Molecules import Molecules

mpl.use("Qt5Agg")


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class TrajectoryDialog(QDialog):
    """
    Dialog for manipulating appearance of trajectories.
    """

    def __init__(self, parent: QMainWindow = None):
        super().__init__(
            parent
        )  # main window widget is passed as a parent, so dialog is closed if main window is closed.
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.timer = QTimer(self)

        self.ui.checkBox.stateChanged.connect(self.show_trajectory)
        self.ui.PrevButton.clicked.connect(self.get_prev_mol)
        self.ui.NextButton.clicked.connect(self.get_next_mol)
        self.ui.verticalSlider.valueChanged.connect(self.slide_molecule)

    def show_trajectory(self):
        if self.ui.checkBox.isChecked():
            self.timer.start()
            self.timer.timeout.connect(self.update_molecule)

        else:
            self.timer.stop()

        return

    def get_next_mol(self):
        """
        Calls molecules object to get the next molecule and update it in the GUI.
        """
        self.parent().mols.get_next_mol()
        self.update_molecule()
        return

    def get_prev_mol(self):
        """
        Calls molecules object to get the previous molecule and update it in the GUI.
        """
        self.parent().mols.get_previous_mol()
        self.update_molecule()
        return

    def set_slider_range(self):
        """
        Set the slider range to the max number of molecules.
        """
        self.ui.verticalSlider.setRange(0, int(self.parent().mols.num_mols) - 1)

        return

    def slide_molecule(self):
        index = self.ui.verticalSlider.sliderPosition()
        self.parent().ui.openGLWidget.delete_molecule()
        self.parent().ui.openGLWidget.set_molecule(self.parent().mols.get_index_mol(index))

        return

    def update_molecule(self):
        """
        Update molecule in the ui widget by deleting the
        current molecule and calling the next molecule in the molecules object.
        """
        self.parent().ui.openGLWidget.delete_molecule()

        self.parent().ui.openGLWidget.set_molecule(self.parent().mols.get_next_mol())

        if self.parent().mols.mol_index + 1 == self.parent().mols.num_mols:
            self.timer.stop()

        return

    def plot_energies(self):
        """
        Plot the energies of the molecules in the molecules object.
        """
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot(np.arange(self.parent().mols.num_mols), self.parent().mols.energies, "x-")
        layout = QVBoxLayout()
        layout.addWidget(sc)

        self.ui.widget.setLayout(layout)

        return
