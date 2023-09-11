from PySide6.QtWidgets import QDialog
from molara.Gui.ui_crystalstructure_dialog import Ui_Dialog
from molara.Molecule.Crystal import Crystal
from molara.Molecule.Atom import element_symbol_to_atomic_number
import numpy as np

class CrystalDialog(QDialog):
  '''
  Dialog for specifying a crystal structure.
  Element symbols, coordinates, lattice constants, supercell size given by user,
  object of type Crystal is instantiated and passed to main window's OpenGL widget for rendering.
  '''
  def __init__(self, parent=None):
    super().__init__(parent)# main window widget is passed as a parent, so dialog is closed if main window is closed.
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)
    self.change_crystal_system('Cubic')
    self.ui.selectCrystalSystem.currentTextChanged.connect(self.change_crystal_system)
    self.ui.buttonAddAtom.clicked.connect(self.add_atom)
    self.list_of_coordinates = []
    self.list_of_atomic_numbers = []
  def add_atom(self):
    element_symbol = self.ui.inputElementSymbol.text()
    atomic_number = element_symbol_to_atomic_number(element_symbol)
    coord_a, coord_b, coord_c = self.ui.inputAtomCoord_a.text(),\
      self.ui.inputAtomCoord_b.text(), self.ui.inputAtomCoord_c.text()
    coord_a, coord_b, coord_c = coord_a.replace(',', '.'), coord_b.replace(',', '.'), coord_c.replace(',', '.')
    try:
      coord_a, coord_b, coord_c = float(coord_a), float(coord_b), float(coord_c)
    except ValueError:
      print ("Value Error. Could not add atom.")
      return False
    self.list_of_coordinates += [[coord_a, coord_b, coord_c]]
    self.list_of_atomic_numbers += [atomic_number]
    print ("Added Atom:")
    print (element_symbol, atomic_number, "|", coord_a, coord_b, coord_c)
  def accept(self):
    dim_a, dim_b, dim_c = self.ui.inputSupercell_a.value(),\
      self.ui.inputSupercell_b.value(), self.ui.inputSupercell_c.value()
    supercell_dimensions = np.array([dim_a, dim_b, dim_c])
    a, b, c = self.ui.inputLatConst_a.value(), self.ui.inputLatConst_b.value(), self.ui.inputLatConst_c.value()
    if self.crystal_system=='Cubic':
      b, c = a, a
    elif self.crystal_system=='Tetragonal':
      b = a
    list_of_coordinates = np.array(self.list_of_coordinates)
    mycrystal = Crystal(
      self.list_of_atomic_numbers,
      list_of_coordinates,
      np.diag([a, b, c]),
      supercell_dimensions=supercell_dimensions)
    self.parent().ui.openGLWidget.set_molecule(mycrystal)
  def change_crystal_system(self, value):
    self.crystal_system = value
    selectSpaceGroup = self.ui.selectSpaceGroup
    view = selectSpaceGroup.view()
    if value == 'Cubic':
      view.setRowHidden(0, False)
      view.setRowHidden(1, True)
      view.setRowHidden(2, True)
      selectSpaceGroup.setCurrentIndex(0)
    elif value=='Tetragonal':
      view.setRowHidden(0, True)
      view.setRowHidden(1, False)
      view.setRowHidden(2, True)
      selectSpaceGroup.setCurrentIndex(1)
    elif value=='Orthorhombic':
      view.setRowHidden(0, True)
      view.setRowHidden(1, True)
      view.setRowHidden(2, False)
      selectSpaceGroup.setCurrentIndex(2)