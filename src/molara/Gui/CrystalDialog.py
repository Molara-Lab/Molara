from contextlib import suppress

import numpy as np
from PySide6.QtWidgets import QDialog, QTableWidgetItem

from molara.Gui.ui_crystalstructure_dialog import Ui_Dialog
from molara.Molecule.Atom import element_symbol_to_atomic_number
from molara.Molecule.Crystal import Crystal


class CrystalDialog(QDialog):
    """
    Dialog for specifying a crystal structure.
    Element symbols, coordinates, lattice constants, supercell size given by user,
    object of type Crystal is instantiated and passed to main window"s OpenGL widget for rendering.
    """

    def __init__(self, parent=None):
        super().__init__(
            parent
        )  # main window widget is passed as a parent, so dialog is closed if main window is closed.
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.list_of_coordinates = []
        self.list_of_atomic_numbers = []
        self.change_crystal_system("Cubic")
        self.ui.selectCrystalSystem.currentTextChanged.connect(self.change_crystal_system)
        self.ui.buttonAddAtom.clicked.connect(self.add_atom)
        self.ui.pushButton.clicked.connect(self.reset)
        self.ui.listAtoms.setColumnCount(4)

    def reset(self):
        self.list_of_atomic_numbers = []
        self.list_of_coordinates = []
        self.ui.listAtoms.setRowCount(0)

    def add_atom(self):
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

    def accept(self):
        dim_a, dim_b, dim_c = (
            self.ui.inputSupercell_a.value(),
            self.ui.inputSupercell_b.value(),
            self.ui.inputSupercell_c.value(),
        )
        supercell_dimensions = np.array([dim_a, dim_b, dim_c])
        a, b, c = self.ui.inputLatConst_a.value(), self.ui.inputLatConst_b.value(), self.ui.inputLatConst_c.value()
        list_of_coordinates = np.array(self.list_of_coordinates)
        mycrystal = Crystal(
            self.list_of_atomic_numbers,
            list_of_coordinates,
            np.diag([a, b, c]),
            supercell_dimensions=supercell_dimensions,
        )
        self.parent().ui.openGLWidget.set_molecule(mycrystal)

    def change_crystal_system(self, value):
        self.crystal_system = value
        selectSpaceGroup = self.ui.selectSpaceGroup
        view = selectSpaceGroup.view()
        if value == "Cubic":
            view.setRowHidden(0, False)
            view.setRowHidden(1, True)
            view.setRowHidden(2, True)
            selectSpaceGroup.setCurrentIndex(0)
            self.ui.inputLatConst_a.setEnabled(True)
            self.ui.inputLatConst_b.setEnabled(False)
            self.ui.inputLatConst_c.setEnabled(False)

            def bc_equals_a(value):
                self.ui.inputLatConst_b.setValue(value)
                self.ui.inputLatConst_c.setValue(value)

            with suppress(Exception):
                self.ui.inputLatConst_a.valueChanged.disconnect()
            self.ui.inputLatConst_a.valueChanged.connect(bc_equals_a)
            bc_equals_a(self.ui.inputLatConst_a.value())
        elif value == "Tetragonal":
            view.setRowHidden(0, True)
            view.setRowHidden(1, False)
            view.setRowHidden(2, True)
            selectSpaceGroup.setCurrentIndex(1)
            self.ui.inputLatConst_a.setEnabled(True)
            self.ui.inputLatConst_b.setEnabled(False)
            self.ui.inputLatConst_c.setEnabled(True)

            def b_equals_a(value):
                self.ui.inputLatConst_b.setValue(value)

            with suppress(Exception):
                self.ui.inputLatConst_a.valueChanged.disconnect()
            self.ui.inputLatConst_a.valueChanged.connect(b_equals_a)
            b_equals_a(self.ui.inputLatConst_a.value())
        elif value == "Orthorhombic":
            view.setRowHidden(0, True)
            view.setRowHidden(1, True)
            view.setRowHidden(2, False)
            selectSpaceGroup.setCurrentIndex(2)
            self.ui.inputLatConst_a.setEnabled(True)
            self.ui.inputLatConst_b.setEnabled(True)
            self.ui.inputLatConst_c.setEnabled(True)
            with suppress(Exception):
                self.ui.inputLatConst_a.valueChanged.disconnect()
