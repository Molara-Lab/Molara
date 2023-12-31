"""Dialog for specifying supercell dims."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtWidgets import QDialog, QMainWindow

from molara.Gui.ui_supercell_dialog import Ui_Dialog

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Annotated


class SupercellDialog(QDialog):
    """Dialog for specifying supercell dimensions.

    Supercell size given by user, object of type Crystal is instantiated
    and passed to main window"s OpenGL widget for rendering.
    """

    def __init__(self, parent: QMainWindow = None) -> None:
        """Creates a CrystalDialog object."""
        super().__init__(
            parent,
        )  # main window widget is passed as a parent, so dialog is closed if main window is closed.
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # the supercell_dims attribute's purpose is to be overwritten
        # by a list that is passed by a Crystal object. The entries of this
        # list are changed in the accept routine, thus changing the original
        # list in the crystal object.
        self.supercell_dims = [1, 1, 1]

    @staticmethod
    def get_supercell_dims(supercell_dims: Annotated[Sequence[int], 3]) -> bool:
        """Opens dialog for supercell size specification."""
        dialog = SupercellDialog()
        dialog.set_supercell_dims(supercell_dims)
        return dialog.exec()

    def set_supercell_dims(self, supercell_dims: Annotated[Sequence[int], 3]) -> None:
        """Set supercell dimensions."""
        self.supercell_dims = supercell_dims
        self.ui.set_supercell_dims(self.supercell_dims)

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
        self.supercell_dims[0] = dim_a
        self.supercell_dims[1] = dim_b
        self.supercell_dims[2] = dim_c
        self.close()
