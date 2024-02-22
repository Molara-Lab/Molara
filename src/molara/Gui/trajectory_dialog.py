"""Trajectory class for manipulating the Trajectory Dialog window."""

from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib as mpl
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
    QVBoxLayout,
)

from molara.Gui.ui_trajectory import Ui_Dialog

if TYPE_CHECKING:
    from molara.Gui.main_window import MainWindow

__copyright__ = "Copyright 2024, Molara"

mpl.use("Qt5Agg")


class MplCanvas(FigureCanvasQTAgg):
    """A class to generate a plot from matplotlib in QT."""

    def __init__(
        self,
        # This argument is necessary to be surpassed.
        parent: MainWindow = None,  # noqa: ARG002
        width: int = 5,
        height: int = 4,
        dpi: int = 100,
    ) -> None:
        """Initializes a Figure by generating a subplot.

        :param parent: MainWindow: The widget of the MainWindow
        :param width: int: Width of the figure
        :param height: int: Height of the figure
        :param dpi: int: MISSING INFORMATION.
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)


class TrajectoryDialog(QDialog):
    """Dialog for manipulating appearance of trajectories."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Initializes the trajectory dialog.

        :param parent: parent widget (main window)
        """
        super().__init__(
            parent,
        )  # main window widget is passed as a parent, so dialog is closed if main window is closed.

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.checkBox.stateChanged.connect(self.show_trajectory)
        self.ui.PrevButton.clicked.connect(self.get_prev_mol)
        self.ui.NextButton.clicked.connect(self.get_next_mol)
        self.ui.verticalSlider.valueChanged.connect(self.slide_molecule)

        layout = QVBoxLayout(self.ui.widget)
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.sc)
        self.ui.widget.setLayout(layout)

    def show_trajectory(self) -> None:
        """Shows the all molecules in the current Molecules class automatically."""
        if self.ui.checkBox.isChecked():
            self.timer = QTimer(self)
            self.timer.start()
            self.timer.timeout.connect(self.get_next_mol)

        else:
            self.timer.stop()

    def get_next_mol(self) -> None:
        """Calls molecules object to get the next molecule and update it in the GUI."""
        self.parent().mols.set_next_mol()
        self.update_molecule()

    def get_prev_mol(self) -> None:
        """Calls molecules object to get the previous molecule and update it in the GUI."""
        self.parent().mols.set_previous_mol()
        self.update_molecule()

    def set_slider_range(self) -> None:
        """Set the slider range to the max number of molecules."""
        self.ui.verticalSlider.setRange(0, int(self.parent().mols.num_mols) - 1)

    def slide_molecule(self) -> None:
        """Updates the molecule and energy plot in dependence of the slider position."""
        index = self.ui.verticalSlider.sliderPosition()
        self.parent().ui.openGLWidget.delete_structure()
        self.parent().ui.openGLWidget.set_structure(
            self.parent().mols.get_index_mol(index),
        )
        self.update_energy_plot()

    def update_molecule(self) -> None:
        """Update molecule and delete old molecule."""
        self.parent().ui.openGLWidget.delete_molecule()

        self.update_energy_plot()

        self.parent().ui.openGLWidget.set_structure(
            self.parent().mols.get_current_mol(),
        )

        if self.parent().mols.mol_index + 1 == self.parent().mols.num_mols:
            self.timer.stop()

    def initial_energy_plot(self) -> None:
        """Plot the energies of the molecules in the molecules object."""
        (self.energy_plot,) = self.sc.axes.plot(
            np.arange(self.parent().mols.num_mols),
            self.parent().mols.energies,
            "x-",
        )
        (self.current_energy_plot,) = self.sc.axes.plot(
            self.parent().mols.mol_index,
            self.parent().mols.energies[self.parent().mols.mol_index],
            "o",
        )
        self.sc.axes.set_xlabel(r"steps")
        self.sc.axes.set_ylabel(r"energy$\,/\,\mathrm{eV}$")
        self.sc.fig.tight_layout()
        self.sc.fig.subplots_adjust(bottom=0.22, right=0.99)

    def update_energy_plot(self) -> None:
        """Update the energy plot, where the current structure is shown in a different color."""
        energies, mol_index = self.parent().mols.energies, self.parent().mols.mol_index
        self.current_energy_plot.set_xdata(mol_index)
        self.current_energy_plot.set_ydata(energies[mol_index])
        self.sc.draw()
