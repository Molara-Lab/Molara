"""Module for the crystal structure dialog."""

################################################################################
## Form generated from reading UI file 'crystalstructure_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    Qt,
    QTime,
    QUrl,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFrame,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

if TYPE_CHECKING:
    from molara.Gui.crystal_dialog import CrystalDialog


class UiCrystalDialog:
    """Class for the crystal structure dialog."""

    def setup_ui(self, crystal_dialog: CrystalDialog) -> None:
        """Set up crystal structure ui."""
        if not crystal_dialog.objectName():
            crystal_dialog.setObjectName("crystal_dialog")
        crystal_dialog.resize(400, 476)
        self.buttonBox = QDialogButtonBox(crystal_dialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setGeometry(QRect(50, 440, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonAddAtom = QPushButton(crystal_dialog)
        self.buttonAddAtom.setObjectName("buttonAddAtom")
        self.buttonAddAtom.setGeometry(QRect(300, 70, 90, 28))
        self.checkBoxPreview = QCheckBox(crystal_dialog)
        self.checkBoxPreview.setObjectName("checkBoxPreview")
        self.checkBoxPreview.setEnabled(False)
        self.checkBoxPreview.setGeometry(QRect(200, 410, 131, 21))
        self.line = QFrame(crystal_dialog)
        self.line.setObjectName("line")
        self.line.setGeometry(QRect(110, 10, 20, 461))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.setup_symmetry_properties(crystal_dialog)

        self.setup_atom_inputs(crystal_dialog)

        self.setup_supercell_measures(crystal_dialog)

        self.listAtoms = QTableWidget(crystal_dialog)
        self.listAtoms.setObjectName("listAtoms")
        self.listAtoms.setGeometry(QRect(130, 110, 256, 291))
        self.listAtoms.horizontalHeader().setCascadingSectionResizes(False)
        self.listAtoms.horizontalHeader().setMinimumSectionSize(30)
        self.listAtoms.horizontalHeader().setDefaultSectionSize(60)
        self.listAtoms.horizontalHeader().setStretchLastSection(True)
        self.pushButton = QPushButton(crystal_dialog)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(130, 70, 90, 28))

        self.setup_lattice_constants(crystal_dialog)
        self.setup_lattice_angles(crystal_dialog)

        self.retranslate_ui(crystal_dialog)
        self.buttonBox.accepted.connect(crystal_dialog.accept)
        self.buttonBox.rejected.connect(crystal_dialog.reject)

        QMetaObject.connectSlotsByName(crystal_dialog)

    def setup_atom_inputs(self, crystal_dialog: CrystalDialog) -> None:
        """Set up input elements for entering atomic species and coordinates."""
        self.inputAtomCoord_a = QDoubleSpinBox(crystal_dialog)
        self.inputAtomCoord_a.setObjectName("inputAtomCoord_a")
        self.inputAtomCoord_a.setGeometry(QRect(190, 30, 62, 26))
        self.inputAtomCoord_a.setMaximum(0.990000000000000)
        self.inputAtomCoord_a.setSingleStep(0.010000000000000)
        self.inputAtomCoord_b = QDoubleSpinBox(crystal_dialog)
        self.inputAtomCoord_b.setObjectName("inputAtomCoord_b")
        self.inputAtomCoord_b.setGeometry(QRect(260, 30, 62, 26))
        self.inputAtomCoord_b.setMaximum(0.990000000000000)
        self.inputAtomCoord_b.setSingleStep(0.010000000000000)
        self.inputAtomCoord_c = QDoubleSpinBox(crystal_dialog)
        self.inputAtomCoord_c.setObjectName("inputAtomCoord_c")
        self.inputAtomCoord_c.setGeometry(QRect(330, 30, 62, 26))
        self.inputAtomCoord_c.setMaximum(0.990000000000000)
        self.inputAtomCoord_c.setSingleStep(0.010000000000000)
        self.inputElementSymbol = QLineEdit(crystal_dialog)
        self.inputElementSymbol.setObjectName("inputElementSymbol")
        self.inputElementSymbol.setEnabled(True)
        self.inputElementSymbol.setGeometry(QRect(130, 30, 51, 28))
        self.labelElementSymbol = QLabel(crystal_dialog)
        self.labelElementSymbol.setObjectName("labelElementSymbol")
        self.labelElementSymbol.setGeometry(QRect(130, 10, 58, 16))
        self.labelCoord_a = QLabel(crystal_dialog)
        self.labelCoord_a.setObjectName("labelCoord_a")
        self.labelCoord_a.setGeometry(QRect(190, 10, 58, 16))
        self.labelCoord_b = QLabel(crystal_dialog)
        self.labelCoord_b.setObjectName("labelCoord_b")
        self.labelCoord_b.setGeometry(QRect(260, 10, 58, 16))
        self.labelCoord_c = QLabel(crystal_dialog)
        self.labelCoord_c.setObjectName("labelCoord_c")
        self.labelCoord_c.setGeometry(QRect(330, 10, 58, 16))

    def setup_symmetry_properties(self, crystal_dialog: CrystalDialog) -> None:
        """Set up input elements for entering crystal system and space group."""
        self.selectCrystalSystem = QComboBox(crystal_dialog)
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.setObjectName("selectCrystalSystem")
        self.selectCrystalSystem.setEnabled(True)
        self.selectCrystalSystem.setGeometry(QRect(20, 10, 76, 24))
        self.selectSpaceGroup = QComboBox(crystal_dialog)
        self.selectSpaceGroup.addItem("")
        self.selectSpaceGroup.addItem("")
        self.selectSpaceGroup.addItem("")
        self.selectSpaceGroup.addItem("")
        self.selectSpaceGroup.setObjectName("selectSpaceGroup")
        self.selectSpaceGroup.setEnabled(True)
        self.selectSpaceGroup.setGeometry(QRect(20, 40, 76, 24))

    def setup_lattice_constants(self, crystal_dialog: CrystalDialog) -> None:
        """Set up input elements for entering lattice constants."""
        self.labelLatConst_a = QLabel(crystal_dialog)
        self.labelLatConst_a.setObjectName("labelLatConst_a")
        self.labelLatConst_a.setGeometry(QRect(20, 110, 16, 20))
        self.labelLatConst_b = QLabel(crystal_dialog)
        self.labelLatConst_b.setObjectName("labelLatConst_b")
        self.labelLatConst_b.setGeometry(QRect(20, 140, 16, 20))
        self.labelLatConst_C = QLabel(crystal_dialog)
        self.labelLatConst_C.setObjectName("labelLatConst_C")
        self.labelLatConst_C.setGeometry(QRect(20, 170, 16, 20))
        self.labelTitleLatConst = QLabel(crystal_dialog)
        self.labelTitleLatConst.setObjectName("labelTitleLatConst")
        self.labelTitleLatConst.setGeometry(QRect(10, 90, 101, 16))
        self.inputLatConst_a = QDoubleSpinBox(crystal_dialog)
        self.inputLatConst_a.setObjectName("inputLatConst_a")
        self.inputLatConst_a.setGeometry(QRect(47, 110, 65, 26))
        self.inputLatConst_a.setMinimum(0.010000000000000)
        self.inputLatConst_a.setSingleStep(0.010000000000000)
        self.inputLatConst_a.setValue(1.000000000000000)
        self.inputLatConst_b = QDoubleSpinBox(crystal_dialog)
        self.inputLatConst_b.setObjectName("inputLatConst_b")
        self.inputLatConst_b.setEnabled(False)
        self.inputLatConst_b.setGeometry(QRect(47, 140, 65, 26))
        self.inputLatConst_b.setMinimum(0.010000000000000)
        self.inputLatConst_b.setSingleStep(0.010000000000000)
        self.inputLatConst_b.setValue(1.000000000000000)
        self.inputLatConst_c = QDoubleSpinBox(crystal_dialog)
        self.inputLatConst_c.setObjectName("inputLatConst_c")
        self.inputLatConst_c.setEnabled(False)
        self.inputLatConst_c.setGeometry(QRect(47, 170, 65, 26))
        self.inputLatConst_c.setMinimum(0.010000000000000)
        self.inputLatConst_c.setSingleStep(0.010000000000000)
        self.inputLatConst_c.setValue(1.000000000000000)

    def setup_lattice_angles(self, crystal_dialog: CrystalDialog) -> None:
        """Set up input elements for entering lattice angles."""
        self.labelTitleLatAngles = QLabel(crystal_dialog)
        self.labelTitleLatAngles.setObjectName("labelTitleLatAngles")
        self.labelTitleLatAngles.setGeometry(QRect(10, 210, 101, 16))
        self.inputLatAngle_beta = QDoubleSpinBox(crystal_dialog)
        self.inputLatAngle_beta.setObjectName("inputLatAngle_beta")
        self.inputLatAngle_beta.setEnabled(False)
        self.inputLatAngle_beta.setGeometry(QRect(47, 270, 65, 26))
        self.inputLatAngle_beta.setMinimum(0.010000000000000)
        self.inputLatAngle_beta.setMaximum(179.990000000000009)
        self.inputLatAngle_beta.setSingleStep(0.010000000000000)
        self.inputLatAngle_beta.setValue(90.000000000000000)
        self.labelLatAngle_alpha = QLabel(crystal_dialog)
        self.labelLatAngle_alpha.setObjectName("labelLatAngle_alpha")
        self.labelLatAngle_alpha.setGeometry(QRect(20, 240, 16, 20))
        self.labelLatAngle_beta = QLabel(crystal_dialog)
        self.labelLatAngle_beta.setObjectName("labelLatAngle_beta")
        self.labelLatAngle_beta.setGeometry(QRect(20, 270, 16, 20))
        self.inputLatAngle_alpha = QDoubleSpinBox(crystal_dialog)
        self.inputLatAngle_alpha.setObjectName("inputLatAngle_alpha")
        self.inputLatAngle_alpha.setGeometry(QRect(47, 240, 65, 26))
        self.inputLatAngle_alpha.setMinimum(0.010000000000000)
        self.inputLatAngle_alpha.setMaximum(179.990000000000009)
        self.inputLatAngle_alpha.setSingleStep(0.010000000000000)
        self.inputLatAngle_alpha.setValue(90.000000000000000)
        self.inputLatAngle_gamma = QDoubleSpinBox(crystal_dialog)
        self.inputLatAngle_gamma.setObjectName("inputLatAngle_gamma")
        self.inputLatAngle_gamma.setEnabled(False)
        self.inputLatAngle_gamma.setGeometry(QRect(47, 300, 65, 26))
        self.inputLatAngle_gamma.setMinimum(0.010000000000000)
        self.inputLatAngle_gamma.setMaximum(179.990000000000009)
        self.inputLatAngle_gamma.setSingleStep(0.010000000000000)
        self.inputLatAngle_gamma.setValue(90.000000000000000)
        self.labelLatAngle_gamma = QLabel(crystal_dialog)
        self.labelLatAngle_gamma.setObjectName("labelLatAngle_gamma")
        self.labelLatAngle_gamma.setGeometry(QRect(20, 300, 16, 20))

    def setup_supercell_measures(self, crystal_dialog: CrystalDialog) -> None:
        """Set up input elements for entering supercell dimensions."""
        self.inputSupercell_a = QSpinBox(crystal_dialog)
        self.inputSupercell_a.setObjectName("inputSupercell_a")
        self.inputSupercell_a.setGeometry(QRect(50, 380, 42, 26))
        self.inputSupercell_a.setMinimum(1)
        self.inputSupercell_b = QSpinBox(crystal_dialog)
        self.inputSupercell_b.setObjectName("inputSupercell_b")
        self.inputSupercell_b.setGeometry(QRect(50, 410, 42, 26))
        self.inputSupercell_b.setMinimum(1)
        self.inputSupercell_c = QSpinBox(crystal_dialog)
        self.inputSupercell_c.setObjectName("inputSupercell_c")
        self.inputSupercell_c.setGeometry(QRect(50, 440, 42, 26))
        self.inputSupercell_c.setMinimum(1)
        self.labelTitleSupercell = QLabel(crystal_dialog)
        self.labelTitleSupercell.setObjectName("labelTitleSupercell")
        self.labelTitleSupercell.setGeometry(QRect(10, 350, 101, 16))
        self.labelSupercell_a = QLabel(crystal_dialog)
        self.labelSupercell_a.setObjectName("labelSupercell_a")
        self.labelSupercell_a.setGeometry(QRect(20, 380, 16, 20))
        self.labelSupercell_b = QLabel(crystal_dialog)
        self.labelSupercell_b.setObjectName("labelSupercell_b")
        self.labelSupercell_b.setGeometry(QRect(20, 410, 16, 20))
        self.labelSupercell_c = QLabel(crystal_dialog)
        self.labelSupercell_c.setObjectName("labelSupercell_c")
        self.labelSupercell_c.setGeometry(QRect(20, 440, 16, 20))

    # setup_ui

    def retranslate_ui(self, crystal_dialog: CrystalDialog) -> None:
        """Set labels etc."""
        crystal_dialog.setWindowTitle(
            QCoreApplication.translate("crystal_dialog", "Create custom crystal structure", None),
        )
        self.buttonAddAtom.setText(QCoreApplication.translate("crystal_dialog", "Add Atom", None))
        self.checkBoxPreview.setText(QCoreApplication.translate("crystal_dialog", "Show Preview", None))
        self.selectCrystalSystem.setItemText(0, QCoreApplication.translate("crystal_dialog", "Cubic", None))
        self.selectCrystalSystem.setItemText(1, QCoreApplication.translate("crystal_dialog", "Tetragonal", None))
        self.selectCrystalSystem.setItemText(2, QCoreApplication.translate("crystal_dialog", "Orthorhombic", None))
        self.selectCrystalSystem.setItemText(3, QCoreApplication.translate("CrystalDialog", u"Hexagonal", None))
        self.selectCrystalSystem.setItemText(4, QCoreApplication.translate("CrystalDialog", u"Monoclinic", None))
        self.selectCrystalSystem.setItemText(5, QCoreApplication.translate("CrystalDialog", u"Triclinic", None))
        self.selectCrystalSystem.setItemText(6, QCoreApplication.translate("CrystalDialog", u"(Trigonal)", None))

        self.selectSpaceGroup.setItemText(0, QCoreApplication.translate("CrystalDialog", u"\u2013", None))
        self.selectSpaceGroup.setItemText(1, QCoreApplication.translate("crystal_dialog", "m3m", None))
        self.selectSpaceGroup.setItemText(2, QCoreApplication.translate("crystal_dialog", "4/mmm", None))
        self.selectSpaceGroup.setItemText(3, QCoreApplication.translate("crystal_dialog", "mmm", None))

        self.labelElementSymbol.setText(QCoreApplication.translate("crystal_dialog", "Element", None))
        self.labelCoord_a.setText(QCoreApplication.translate("crystal_dialog", "coord. a", None))
        self.labelCoord_b.setText(QCoreApplication.translate("crystal_dialog", "coord. b", None))
        self.labelCoord_c.setText(QCoreApplication.translate("crystal_dialog", "coord. c", None))
        self.labelLatConst_a.setText(QCoreApplication.translate("crystal_dialog", "a", None))
        self.labelLatConst_b.setText(QCoreApplication.translate("crystal_dialog", "b", None))
        self.labelLatConst_C.setText(QCoreApplication.translate("crystal_dialog", "c", None))
        self.labelTitleLatConst.setText(QCoreApplication.translate("crystal_dialog", "Lattice constants", None))
        self.labelTitleSupercell.setText(QCoreApplication.translate("crystal_dialog", "Supercell", None))
        self.labelSupercell_a.setText(
            QCoreApplication.translate(
                "crystal_dialog",
                "<html><head/><body><p>N<sub>a</sub><br/></p></body></html>",
                None,
            ),
        )
        self.labelSupercell_b.setText(
            QCoreApplication.translate(
                "crystal_dialog",
                "<html><head/><body><p>N<sub>b</sub><br/></p></body></html>",
                None,
            ),
        )
        self.labelSupercell_c.setText(
            QCoreApplication.translate(
                "crystal_dialog",
                "<html><head/><body><p>N<sub>c</sub><br/></p></body></html>",
                None,
            ),
        )
        self.pushButton.setText(QCoreApplication.translate("crystal_dialog", "Clear Atoms", None))
        self.labelTitleLatAngles.setText(QCoreApplication.translate("crystal_dialog", "Lattice angles", None))
        self.labelLatAngle_alpha.setText(QCoreApplication.translate("crystal_dialog", "\u03b1", None))
        self.labelLatAngle_beta.setText(QCoreApplication.translate("crystal_dialog", "\u03b2", None))
        self.labelLatAngle_gamma.setText(QCoreApplication.translate("crystal_dialog", "\u03b3", None))

    # retranslateUi
