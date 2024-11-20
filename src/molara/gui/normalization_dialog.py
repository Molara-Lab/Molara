"""Dialog for checking if the basis set is properly normalized."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QMainWindow

from molara.eval.populationanalysis import PopulationAnalysis
from molara.gui.ui_normalization_dialog import Ui_normalization_dialog

if TYPE_CHECKING:
    from PySide6.QtCore import QEvent

    from molara.structure.molecule import Molecule


class NormalizationDialog(QDialog):
    """Dialog for exporting a snapshot of the rendered structure."""

    def __init__(self, parent: QMainWindow) -> None:
        """Instantiate the dialog object."""
        super().__init__(parent)

        self.molecule: Molecule | None = None

        self.ui = Ui_normalization_dialog()
        self.ui.setupUi(self)

        self.ui.normalizationButton.clicked.connect(self.run_population_analysis)

    def initialize_dialog(self) -> None:
        """Initialize the dialog."""
        """Call all the functions to initialize all the labels and buttons and so on."""
        # Check if a structure with MOs is loaded
        if not self.parent().structure_widget.structures:
            return
        if self.parent().structure_widget.structures[0].mos.coefficients.size == 0:
            return

        # Set molecule
        self.molecule = self.parent().structure_widget.structures[0]

        self.show()

    def closeEvent(self, event: QEvent) -> None:  # noqa: N802
        """Close the dialog."""
        self.ui.exactCountLabel.setText("")
        self.ui.calculatedCountLabel.setText("")
        event.accept()

    def run_population_analysis(self) -> None:
        """Run the population analysis to check if the calculated number of electrons matches the exact one."""
        # Use QThreadpool in the future :)
        population = PopulationAnalysis(self.parent().structure_widget.structures[0])
        self.ui.exactCountLabel.setText(str(round(population.number_of_electrons, 15)))
        self.ui.calculatedCountLabel.setText(str(round(population.calculated_number_of_electrons, 15)))
