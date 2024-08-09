"""Dialog for specifying supercell dims."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QMainWindow

from molara.gui.ui_supercell_dialog import Ui_Dialog
from molara.structure.crystal import Crystal

if TYPE_CHECKING:
    intvec3 = list[int]

__copyright__ = "Copyright 2024, Molara"


class SupercellDialog(QDialog):
    """Dialog for specifying supercell dimensions.

    Supercell size given by user, object of type Crystal is instantiated
    and passed to main window"s OpenGL widget for rendering.
    """

    def __init__(self, parent: QMainWindow) -> None:
        """Create a CrystalDialog object.

        :param parent: parent widget (main window)
        """
        super().__init__(
            parent,
        )  # main window widget is passed as a parent, so dialog is closed if main window is closed.
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.main_window = parent
        # the supercell_dims attribute's purpose is to be overwritten
        # by a list that is passed by a Crystal object. The entries of this
        # list are changed in the accept routine, thus changing the original
        # list in the crystal object.
        self.supercell_dims: list[int] = [1, 1, 1]

        self.set_event_handlers()

    def get_supercell_dims(self, supercell_dims: list[int]) -> bool:
        """Open dialog for supercell size specification.

        :param supercell_dims: supercell dimensions (e.g. [2, 4, 3] for 2x4x3 supercell)
        """
        self.set_supercell_dims(supercell_dims)
        return self.exec()

    def set_event_handlers(self) -> None:
        """Set event handlers for supercell dialog."""
        self.ui.inputSupercell_a.valueChanged.connect(self.update_num_atoms_label)
        self.ui.inputSupercell_b.valueChanged.connect(self.update_num_atoms_label)
        self.ui.inputSupercell_c.valueChanged.connect(self.update_num_atoms_label)

    def set_supercell_dims(self, supercell_dims: intvec3) -> None:
        """Set supercell dimensions.

        :param supercell_dims: supercell dimensions (e.g. [2, 4, 3] for 2x4x3 supercell)
        """
        self.supercell_dims = supercell_dims
        self.ui.inputSupercell_a.setValue(supercell_dims[0])
        self.ui.inputSupercell_b.setValue(supercell_dims[1])
        self.ui.inputSupercell_c.setValue(supercell_dims[2])
        self.update_num_atoms_label()

    def update_num_atoms_label(self) -> None:
        """Update number of atoms label."""
        if not self.main_window.structure_widget.structures:
            return
        crystal = self.main_window.structure_widget.structures[0]
        if not isinstance(crystal, Crystal):
            return

        dim_a, dim_b, dim_c = (
            self.ui.inputSupercell_a.value(),
            self.ui.inputSupercell_b.value(),
            self.ui.inputSupercell_c.value(),
        )
        self.ui.labelNumAtoms.setText(
            f"Number of atoms:\n{crystal.calc_number_of_supercell_atoms([dim_a, dim_b, dim_c])}",
        )

    def accept(self) -> None:
        """Submit contents of supercell dialog.

        entries of supercell_dims are changed in order to pass
        the user-specified dimensions to the Crystal object.
        """
        dim_a, dim_b, dim_c = (
            self.ui.inputSupercell_a.value(),
            self.ui.inputSupercell_b.value(),
            self.ui.inputSupercell_c.value(),
        )
        # the purpose of the single assign of the elements is not to overwrite the list object.
        self.supercell_dims[0] = dim_a
        self.supercell_dims[1] = dim_b
        self.supercell_dims[2] = dim_c
        self.close()
