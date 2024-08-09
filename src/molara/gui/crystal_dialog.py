"""Dialog for specifying a crystal structure."""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import SIGNAL
from PySide6.QtWidgets import QDialog, QMainWindow, QTableWidgetItem

from molara.gui.ui_crystalstructure_dialog import Ui_CrystalDialog
from molara.structure.atom import element_symbol_to_atomic_number
from molara.structure.crystal import Crystal

RIGHTANGLE = 90.0
ENABLED, DISABLED = True, False

__copyright__ = "Copyright 2024, Molara"


class CrystalDialog(QDialog):
    """Dialog for specifying a crystal structure.

    Element symbols, coordinates, lattice constants, supercell size given by user,
    object of type Crystal is instantiated and passed to main window"s OpenGL widget for rendering.
    """

    def __init__(self, parent: QMainWindow | None = None) -> None:
        """Create a CrystalDialog object.

        :param parent: parent widget (main window)
        """
        super().__init__(
            parent,
        )  # main window widget is passed as a parent, so dialog is closed if main window is closed.
        self.ui = Ui_CrystalDialog()
        self.ui.setupUi(self)
        self.list_of_coordinates: list = []
        self.list_of_atomic_numbers: list[int] = []
        self.change_crystal_system("Cubic")
        self.ui.selectCrystalSystem.currentTextChanged.connect(
            self.change_crystal_system,
        )
        self.ui.buttonAddAtom.clicked.connect(self.add_atom)
        self.ui.pushButton.clicked.connect(self.reset)
        self.ui.listAtoms.setColumnCount(4)
        select_space_group = self.ui.selectSpaceGroup
        select_space_group.setCurrentIndex(0)
        self.hide_space_groups([False, True, True, True])

    def reset(self) -> None:
        """Reset the dialog."""
        self.list_of_atomic_numbers = []
        self.list_of_coordinates = []
        self.ui.listAtoms.setRowCount(0)

    def add_atom(self) -> None:
        """Add an atom to the list of atoms."""
        element_symbol = self.ui.inputElementSymbol.text()
        atomic_number = element_symbol_to_atomic_number(element_symbol)
        coord_a, coord_b, coord_c = (
            self.ui.inputAtomCoord_a.value(),
            self.ui.inputAtomCoord_b.value(),
            self.ui.inputAtomCoord_c.value(),
        )
        self.list_of_coordinates += [[coord_a, coord_b, coord_c]]
        self.list_of_atomic_numbers += [atomic_number]
        row_id = len(self.list_of_atomic_numbers) - 1
        self.ui.listAtoms.setRowCount(row_id + 1)
        item_element_symbol = QTableWidgetItem(element_symbol)
        item_coord_a = QTableWidgetItem(str(coord_a))
        item_coord_b = QTableWidgetItem(str(coord_b))
        item_coord_c = QTableWidgetItem(str(coord_c))
        self.ui.listAtoms.setItem(row_id, 0, item_element_symbol)
        self.ui.listAtoms.setItem(row_id, 1, item_coord_a)
        self.ui.listAtoms.setItem(row_id, 2, item_coord_b)
        self.ui.listAtoms.setItem(row_id, 3, item_coord_c)

    def accept(self) -> None:
        """Accept the dialog and passes the crystal to the main window."""
        dim_a, dim_b, dim_c = (
            self.ui.inputSupercell_a.value(),
            self.ui.inputSupercell_b.value(),
            self.ui.inputSupercell_c.value(),
        )
        supercell_dims = [dim_a, dim_b, dim_c]
        a, b, c = (
            self.ui.inputLatConst_a.value(),
            self.ui.inputLatConst_b.value(),
            self.ui.inputLatConst_c.value(),
        )
        alpha, beta, gamma = (
            self.ui.inputLatAngle_alpha.value(),
            self.ui.inputLatAngle_beta.value(),
            self.ui.inputLatAngle_gamma.value(),
        )
        if alpha == RIGHTANGLE and beta == RIGHTANGLE and gamma == RIGHTANGLE:
            basis_vectors = np.diag([a, b, c]).tolist()
        else:
            cosalpha = np.cos(alpha / 180.0 * np.pi)
            cosbeta = np.cos(beta / 180.0 * np.pi)
            cosgamma = np.cos(gamma / 180.0 * np.pi)
            avec = [a, 0.0, 0.0]
            bvec = [
                b * cosgamma,
                b * np.sqrt(1.0 - cosgamma**2),
                0.0,
            ]
            cvec = [
                c * cosbeta,
                c * (cosalpha - cosbeta * cosgamma) / np.sqrt(1.0 - cosgamma**2),
                c
                * np.sqrt(
                    (1.0 - cosalpha**2 - cosbeta**2 - cosgamma**2 + 2 * cosalpha * cosbeta * cosgamma)
                    / (1.0 - cosgamma**2),
                ),
            ]
            basis_vectors = np.array([avec, bvec, cvec]).tolist()
        mycrystal = Crystal(
            self.list_of_atomic_numbers,
            self.list_of_coordinates,
            basis_vectors=basis_vectors,
            supercell_dims=supercell_dims,
        )
        self.parent().ui.openGLWidget.set_structure([mycrystal])  # type: ignore[attr-defined]

    def bc_equals_a(self, value: float) -> None:
        """Set b and c lattice constants equal to a.

        :param value: value of lattice constant 'a'
        """
        self.ui.inputLatConst_b.setValue(value)
        self.ui.inputLatConst_c.setValue(value)

    def b_equals_a(self, value: float) -> None:
        """Set b lattice constant equal to a.

        :param value: value of lattice constant 'a'
        """
        self.ui.inputLatConst_b.setValue(value)

    def angles_hexagonal(self) -> None:
        """Set lattice angles to 90°, 90°, and 120° for a hexagonal cell."""
        self.ui.inputLatAngle_alpha.setValue(90.0)
        self.ui.inputLatAngle_beta.setValue(90.0)
        self.ui.inputLatAngle_gamma.setValue(120.0)
        self.ui.inputLatAngle_alpha.setEnabled(DISABLED)
        self.ui.inputLatAngle_beta.setEnabled(DISABLED)
        self.ui.inputLatAngle_gamma.setEnabled(DISABLED)

    def angles_monoclinic(self) -> None:
        """Set lattice angles to 90°, 90°, and <arbitrary> for a monoclinic cell."""
        self.ui.inputLatAngle_alpha.setValue(90.0)
        self.ui.inputLatAngle_gamma.setValue(90.0)
        self.ui.inputLatAngle_alpha.setEnabled(DISABLED)
        self.ui.inputLatAngle_beta.setEnabled(ENABLED)
        self.ui.inputLatAngle_gamma.setEnabled(DISABLED)

    def angles_orthorhombic(self) -> None:
        """Set lattice angles to 90°, 90°, and 90° for an orthorhombic cell."""
        self.ui.inputLatAngle_alpha.setValue(90.0)
        self.ui.inputLatAngle_beta.setValue(90.0)
        self.ui.inputLatAngle_gamma.setValue(90.0)
        self.ui.inputLatAngle_alpha.setEnabled(DISABLED)
        self.ui.inputLatAngle_beta.setEnabled(DISABLED)
        self.ui.inputLatAngle_gamma.setEnabled(DISABLED)

    def angles_triclinic(self) -> None:
        """Enable lattice inputs for a triclinic cell."""
        self.ui.inputLatAngle_alpha.setEnabled(ENABLED)
        self.ui.inputLatAngle_beta.setEnabled(ENABLED)
        self.ui.inputLatAngle_gamma.setEnabled(ENABLED)

    def enable_lattice_constants(self, ids: list[int]) -> None:
        """Enable or disable inputs for lattice constants, depending on crystal system.

        :param ids: list that contains ids of inputs that shall be enabled
        """
        aid, bid, cid = 0, 1, 2
        self.ui.inputLatConst_a.setEnabled(aid in ids)
        self.ui.inputLatConst_b.setEnabled(bid in ids)
        self.ui.inputLatConst_c.setEnabled(cid in ids)
        receivers_count = self.ui.inputLatConst_a.receivers(
            SIGNAL("valueChanged(double)"),
        )
        if receivers_count > 0:
            self.ui.inputLatConst_a.valueChanged.disconnect()
        if cid in ids and bid not in ids:
            self.ui.inputLatConst_a.valueChanged.connect(self.b_equals_a)
            self.b_equals_a(self.ui.inputLatConst_a.value())
        elif cid not in ids and bid not in ids:
            self.ui.inputLatConst_a.valueChanged.connect(self.bc_equals_a)
            self.bc_equals_a(self.ui.inputLatConst_a.value())

    def hide_space_groups(self, hide: list[bool]) -> None:
        """Hide space-group entries depending on crystal system.

        :param hide: list of bools that specify which space-group entries should be hidden
        """
        view = self.ui.selectSpaceGroup.view()
        for i, hide_i in enumerate(hide):
            view.setRowHidden(i, hide_i)

    def change_crystal_system(self, value: str) -> None:
        """Change the crystal system.

        :param value: name of the crystal system
        """
        self.crystal_system = value
        if value == "Cubic":
            # self.hide_space_groups([False, False, True, True])
            self.enable_lattice_constants([0])
            self.angles_orthorhombic()
        elif value == "Tetragonal":
            # self.hide_space_groups([False, True, False, True])
            self.enable_lattice_constants([0, 2])
            self.angles_orthorhombic()
        elif value == "Orthorhombic":
            # self.hide_space_groups([False, True, True, False])
            self.enable_lattice_constants([0, 1, 2])
            self.angles_orthorhombic()
        elif value == "Hexagonal":
            # self.hide_space_groups([False, True, True, True])
            self.enable_lattice_constants([0, 2])
            self.angles_hexagonal()
        elif value == "Monoclinic":
            # self.hide_space_groups([False, True, True, True])
            self.enable_lattice_constants([0, 1, 2])
            self.angles_monoclinic()
        elif value == "Triclinic":
            # self.hide_space_groups([False, True, True, True])
            self.enable_lattice_constants([0, 1, 2])
            self.angles_triclinic()
