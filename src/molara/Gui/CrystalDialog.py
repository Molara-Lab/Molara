from PySide6.QtWidgets import QDialog
from molara.Gui.ui_crystalstructure_dialog import Ui_Dialog
from molara.Molecule.Crystal import Crystal
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
  def add_atom(self):
    element_symbol = self.ui.inputElementSymbol.text()
    coord_a, coord_b, coord_c = self.ui.inputAtomCoord_a.text(),\
      self.ui.inputAtomCoord_b.text(), self.ui.inputAtomCoord_c.text()
    coord_a, coord_b, coord_c = coord_a.replace(',', '.'), coord_b.replace(',', '.'), coord_c.replace(',', '.')
    try:
      coord_a, coord_b, coord_c = float(coord_a), float(coord_b), float(coord_c)
    except ValueError:
      print ("Value Error. Could not add atom.")
      return False
    self.list_of_coordinates += [[coord_a, coord_b, coord_c]]
    print ("Added Atom:")
    print (element_symbol, coord_a, coord_b, coord_c)
  def accept(self):
    dim_a, dim_b, dim_c = self.ui.inputSupercell_a.value(),\
      self.ui.inputSupercell_b.value(), self.ui.inputSupercell_c.value()
    supercell_dimensions = np.array([dim_a, dim_b, dim_c])
    list_of_coordinates = np.array(self.list_of_coordinates)
    atomic_numbers = np.full(list_of_coordinates.shape[0], 1)# For now all Hydrogen atoms!
    mycrystal = Crystal(
      atomic_numbers,
      list_of_coordinates,
      np.eye(3),
      supercell_dimensions=supercell_dimensions)
    self.parent().ui.openGLWidget.set_molecule(mycrystal)
  def change_crystal_system(self, value):
    selectCrystalSystem = self.ui.selectSpaceGroup
    view = selectCrystalSystem.view()
    if value == 'Cubic':
      view.setRowHidden(0, False)
      view.setRowHidden(1, True)
      view.setRowHidden(2, True)
      selectCrystalSystem.setCurrentIndex(0)
    elif value=='Tetragonal':
      view.setRowHidden(0, True)
      view.setRowHidden(1, False)
      view.setRowHidden(2, True)
      selectCrystalSystem.setCurrentIndex(1)
    elif value=='Orthorhombic':
      view.setRowHidden(0, True)
      view.setRowHidden(1, True)
      view.setRowHidden(2, False)
      selectCrystalSystem.setCurrentIndex(2)