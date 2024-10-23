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

from molara.gui.ui_trajectory import Ui_traj_dialog

if TYPE_CHECKING:
    from molara.gui.main_window import MainWindow

__copyright__ = "Copyright 2024, Molara"

mpl.use("Qt5Agg")


class MplCanvas(FigureCanvasQTAgg):
    """A class to generate a plot from matplotlib in QT."""

    def __init__(
        self,
        # This argument is necessary to be surpassed.
        parent: MainWindow | None = None,  # noqa: ARG002
        width: int = 5,
        height: int = 4,
        dpi: int = 100,
    ) -> None:
        """Initialize a Figure by generating a subplot.

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

    def __init__(self, parent: QMainWindow | None = None) -> None:
        """Initialize the trajectory dialog.

        :param parent: parent widget (main window)
        """
        super().__init__(
            parent,
        )  # main window widget is passed as a parent, so dialog is closed if main window is closed.

        self.ui = Ui_traj_dialog()
        self.ui.setupUi(self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.get_next_mol)
        self.timer.setInterval(40)

        # self.ui.checkBox.stateChanged.connect(self.show_trajectory)
        self.ui.playStopButton.clicked.connect(self.show_trajectory)
        self.ui.PrevButton.clicked.connect(self.get_prev_mol)
        self.ui.NextButton.clicked.connect(self.get_next_mol)
        self.ui.overlayButton.clicked.connect(self.show_all_molecules)
        # self.ui.verticalSlider.valueChanged.connect(self.slide_molecule)
        self.ui.verticalSlider.sliderMoved.connect(self.slide_molecule)
        self.ui.speedDial.valueChanged.connect(self.change_speed)

        layout = QVBoxLayout(self.ui.widget)
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.sc)
        self.ui.widget.setLayout(layout)

        self.show_all = False

    def show_trajectory(self) -> None:
        """Show the all molecules in the current Molecules class automatically."""
        if not self.parent().mols.num_mols > 1:
            return

        if self.timer.isActive():
            self.timer.stop()
            self.ui.playStopButton.setText("Play")
            return
        self.timer.start()
        self.ui.playStopButton.setText("Stop")

    def show_all_molecules(self) -> None:
        """Show all molecules in the current Molecules class automatically."""
        if not self.parent().mols.num_mols > 1:
            return
        self.show_all = not self.show_all
        if self.show_all:
            self.ui.overlayButton.setText("Show current")
            self.parent().structure_widget.set_structure(self.parent().mols.all_molecules, reset_view=False)
        else:
            self.ui.overlayButton.setText("Show all")
            self.parent().structure_widget.set_structure([self.parent().mols.get_current_mol()], reset_view=False)

    def get_next_mol(self) -> None:
        """Call molecules object to get the next molecule and update it in the GUI."""
        if not self.parent().mols.num_mols > 1:
            return

        val = self.parent().mols.mol_index
        self.ui.verticalSlider.setValue(val + 1)
        self.parent().mols.set_next_mol()
        self.update_molecule()
        if self.parent().mols.mol_index + 1 == self.parent().mols.num_mols:
            self.timer.stop()
            self.ui.playStopButton.setText("Play")

    def get_prev_mol(self) -> None:
        """Call molecules object to get the previous molecule and update it in the GUI."""
        if not self.parent().mols.num_mols > 1:
            return

        val = self.parent().mols.mol_index
        self.ui.verticalSlider.setValue(val - 1)
        self.parent().mols.set_previous_mol()
        self.update_molecule()

    def set_slider_range(self) -> None:
        """Set the slider range to the max number of molecules."""
        self.ui.verticalSlider.setRange(0, int(self.parent().mols.num_mols) - 1)

    def slide_molecule(self) -> None:
        """Update the molecule and energy plot in dependence of the slider position."""
        if not self.parent().mols.num_mols > 1:
            return

        index = self.ui.verticalSlider.sliderPosition()
        self.parent().mols.set_mol_by_id(index)
        self.update_molecule()

    def update_molecule(self) -> None:
        """Update molecule and delete old molecule."""
        self.parent().structure_widget.delete_structure()
        self.parent().structure_widget.set_structure(
            [self.parent().mols.get_current_mol()],
            reset_view=False,
        )
        self.update_energy_plot()
        if self.show_all:
            self.ui.overlayButton.setText("Show all")
            self.show_all = False

    def change_speed(self, value: int) -> None:
        """Change speed (/ time interval) of trajectory animation.

        :param value: value that is passed from the speed dial
        """
        min_interval = 1
        max_interval = 500
        self.timer.setInterval(min_interval * (max_interval / min_interval) ** (value * 0.001))

    def initial_energy_plot(self) -> None:
        """Plot the energies of the molecules in the molecules object."""
        self.sc.axes.cla()
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
        self.sc.axes.set_ylabel(r"energy$\,/\,E_\mathrm{h}$")
        self.sc.fig.tight_layout()
        self.sc.fig.subplots_adjust(bottom=0.22, right=0.99)
        self.sc.draw()

    def update_energy_plot(self) -> None:
        """Update the energy plot, where the current structure is shown in a different color."""
        energies, mol_index = self.parent().mols.energies, self.parent().mols.mol_index
        self.current_energy_plot.set_xdata([mol_index])
        self.current_energy_plot.set_ydata([energies[mol_index]])
        self.sc.draw()

    def reset(self) -> None:
        """Clear the energy plot, update slider range."""
        self.sc.axes.cla()
        self.sc.draw()
        self.set_slider_range()
