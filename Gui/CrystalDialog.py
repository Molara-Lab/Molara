from PySide6.QtWidgets import QDialog
from Gui.ui_crystalstructure_dialog import Ui_Dialog

class CrystalDialog(QDialog):
  def __init__(self, parent=None):
    super().__init__()
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)
    self.change_crystal_system('Cubic')
    self.ui.comboBox.currentTextChanged.connect(self.change_crystal_system)
  def change_crystal_system(self, value):
    comboBox = self.ui.comboBox_2
    view = comboBox.view()
    if value == 'Cubic':
      view.setRowHidden(0, False)
      view.setRowHidden(1, True)
      view.setRowHidden(2, True)
      comboBox.setCurrentIndex(0)
    elif value=='Tetragonal':
      view.setRowHidden(0, True)
      view.setRowHidden(1, False)
      view.setRowHidden(2, True)
      comboBox.setCurrentIndex(1)
    elif value=='Orthorhombic':
      view.setRowHidden(0, True)
      view.setRowHidden(1, True)
      view.setRowHidden(2, False)
      comboBox.setCurrentIndex(2)