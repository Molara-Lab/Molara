
################################################################################
## Form generated from reading UI file 'crystalstructure_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

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


class Ui_CrystalDialog:
    def setupUi(self, CrystalDialog):
        if not CrystalDialog.objectName():
            CrystalDialog.setObjectName("CrystalDialog")
        CrystalDialog.resize(400, 350)
        self.buttonBox = QDialogButtonBox(CrystalDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setGeometry(QRect(40, 310, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonAddAtom = QPushButton(CrystalDialog)
        self.buttonAddAtom.setObjectName("buttonAddAtom")
        self.buttonAddAtom.setGeometry(QRect(300, 70, 90, 28))
        self.checkBoxPreview = QCheckBox(CrystalDialog)
        self.checkBoxPreview.setObjectName("checkBoxPreview")
        self.checkBoxPreview.setEnabled(False)
        self.checkBoxPreview.setGeometry(QRect(200, 280, 131, 21))
        self.line = QFrame(CrystalDialog)
        self.line.setObjectName("line")
        self.line.setGeometry(QRect(110, 10, 20, 331))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.selectCrystalSystem = QComboBox(CrystalDialog)
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.setObjectName("selectCrystalSystem")
        self.selectCrystalSystem.setEnabled(True)
        self.selectCrystalSystem.setGeometry(QRect(20, 10, 76, 24))
        self.selectSpaceGroup = QComboBox(CrystalDialog)
        self.selectSpaceGroup.addItem("")
        self.selectSpaceGroup.addItem("")
        self.selectSpaceGroup.addItem("")
        self.selectSpaceGroup.setObjectName("selectSpaceGroup")
        self.selectSpaceGroup.setEnabled(True)
        self.selectSpaceGroup.setGeometry(QRect(20, 40, 76, 24))
        self.inputLatConst_a = QDoubleSpinBox(CrystalDialog)
        self.inputLatConst_a.setObjectName("inputLatConst_a")
        self.inputLatConst_a.setGeometry(QRect(50, 110, 62, 26))
        self.inputLatConst_a.setMinimum(0.010000000000000)
        self.inputLatConst_a.setSingleStep(0.010000000000000)
        self.inputLatConst_a.setValue(1.000000000000000)
        self.inputLatConst_b = QDoubleSpinBox(CrystalDialog)
        self.inputLatConst_b.setObjectName("inputLatConst_b")
        self.inputLatConst_b.setEnabled(False)
        self.inputLatConst_b.setGeometry(QRect(50, 140, 62, 26))
        self.inputLatConst_b.setMinimum(0.010000000000000)
        self.inputLatConst_b.setSingleStep(0.010000000000000)
        self.inputLatConst_b.setValue(1.000000000000000)
        self.inputLatConst_c = QDoubleSpinBox(CrystalDialog)
        self.inputLatConst_c.setObjectName("inputLatConst_c")
        self.inputLatConst_c.setEnabled(False)
        self.inputLatConst_c.setGeometry(QRect(50, 170, 62, 26))
        self.inputLatConst_c.setMinimum(0.010000000000000)
        self.inputLatConst_c.setSingleStep(0.010000000000000)
        self.inputLatConst_c.setValue(1.000000000000000)
        self.inputAtomCoord_a = QDoubleSpinBox(CrystalDialog)
        self.inputAtomCoord_a.setObjectName("inputAtomCoord_a")
        self.inputAtomCoord_a.setGeometry(QRect(190, 30, 62, 26))
        self.inputAtomCoord_a.setMaximum(0.990000000000000)
        self.inputAtomCoord_a.setSingleStep(0.010000000000000)
        self.inputAtomCoord_b = QDoubleSpinBox(CrystalDialog)
        self.inputAtomCoord_b.setObjectName("inputAtomCoord_b")
        self.inputAtomCoord_b.setGeometry(QRect(260, 30, 62, 26))
        self.inputAtomCoord_b.setMaximum(0.990000000000000)
        self.inputAtomCoord_b.setSingleStep(0.010000000000000)
        self.inputAtomCoord_c = QDoubleSpinBox(CrystalDialog)
        self.inputAtomCoord_c.setObjectName("inputAtomCoord_c")
        self.inputAtomCoord_c.setGeometry(QRect(330, 30, 62, 26))
        self.inputAtomCoord_c.setMaximum(0.990000000000000)
        self.inputAtomCoord_c.setSingleStep(0.010000000000000)
        self.inputElementSymbol = QLineEdit(CrystalDialog)
        self.inputElementSymbol.setObjectName("inputElementSymbol")
        self.inputElementSymbol.setEnabled(True)
        self.inputElementSymbol.setGeometry(QRect(130, 30, 51, 28))
        self.labelElementSymbol = QLabel(CrystalDialog)
        self.labelElementSymbol.setObjectName("labelElementSymbol")
        self.labelElementSymbol.setGeometry(QRect(130, 10, 58, 16))
        self.labelCoord_a = QLabel(CrystalDialog)
        self.labelCoord_a.setObjectName("labelCoord_a")
        self.labelCoord_a.setGeometry(QRect(190, 10, 58, 16))
        self.labelCoord_b = QLabel(CrystalDialog)
        self.labelCoord_b.setObjectName("labelCoord_b")
        self.labelCoord_b.setGeometry(QRect(260, 10, 58, 16))
        self.labelCoord_c = QLabel(CrystalDialog)
        self.labelCoord_c.setObjectName("labelCoord_c")
        self.labelCoord_c.setGeometry(QRect(330, 10, 58, 16))
        self.labelLatConst_a = QLabel(CrystalDialog)
        self.labelLatConst_a.setObjectName("labelLatConst_a")
        self.labelLatConst_a.setGeometry(QRect(20, 110, 16, 20))
        self.labelLatConst_b = QLabel(CrystalDialog)
        self.labelLatConst_b.setObjectName("labelLatConst_b")
        self.labelLatConst_b.setGeometry(QRect(20, 140, 16, 20))
        self.labelLatConst_C = QLabel(CrystalDialog)
        self.labelLatConst_C.setObjectName("labelLatConst_C")
        self.labelLatConst_C.setGeometry(QRect(20, 170, 16, 20))
        self.labelTitleLatConst = QLabel(CrystalDialog)
        self.labelTitleLatConst.setObjectName("labelTitleLatConst")
        self.labelTitleLatConst.setGeometry(QRect(10, 90, 101, 16))
        self.inputSupercell_a = QSpinBox(CrystalDialog)
        self.inputSupercell_a.setObjectName("inputSupercell_a")
        self.inputSupercell_a.setGeometry(QRect(50, 240, 42, 26))
        self.inputSupercell_a.setMinimum(1)
        self.inputSupercell_b = QSpinBox(CrystalDialog)
        self.inputSupercell_b.setObjectName("inputSupercell_b")
        self.inputSupercell_b.setGeometry(QRect(50, 270, 42, 26))
        self.inputSupercell_b.setMinimum(1)
        self.inputSupercell_c = QSpinBox(CrystalDialog)
        self.inputSupercell_c.setObjectName("inputSupercell_c")
        self.inputSupercell_c.setGeometry(QRect(50, 300, 42, 26))
        self.inputSupercell_c.setMinimum(1)
        self.labelTitleSupercell = QLabel(CrystalDialog)
        self.labelTitleSupercell.setObjectName("labelTitleSupercell")
        self.labelTitleSupercell.setGeometry(QRect(10, 210, 101, 16))
        self.labelSupercell_a = QLabel(CrystalDialog)
        self.labelSupercell_a.setObjectName("labelSupercell_a")
        self.labelSupercell_a.setGeometry(QRect(20, 240, 16, 20))
        self.labelSupercell_b = QLabel(CrystalDialog)
        self.labelSupercell_b.setObjectName("labelSupercell_b")
        self.labelSupercell_b.setGeometry(QRect(20, 270, 16, 20))
        self.labelSupercell_c = QLabel(CrystalDialog)
        self.labelSupercell_c.setObjectName("labelSupercell_c")
        self.labelSupercell_c.setGeometry(QRect(20, 300, 16, 20))
        self.listAtoms = QTableWidget(CrystalDialog)
        self.listAtoms.setObjectName("listAtoms")
        self.listAtoms.setGeometry(QRect(130, 110, 256, 161))
        self.listAtoms.horizontalHeader().setCascadingSectionResizes(False)
        self.listAtoms.horizontalHeader().setMinimumSectionSize(30)
        self.listAtoms.horizontalHeader().setDefaultSectionSize(60)
        self.listAtoms.horizontalHeader().setStretchLastSection(True)
        self.pushButton = QPushButton(CrystalDialog)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(130, 70, 90, 28))

        self.retranslateUi(CrystalDialog)
        self.buttonBox.accepted.connect(CrystalDialog.accept)
        self.buttonBox.rejected.connect(CrystalDialog.reject)

        QMetaObject.connectSlotsByName(CrystalDialog)

    # setupUi

    def retranslateUi(self, CrystalDialog):
        CrystalDialog.setWindowTitle(
            QCoreApplication.translate("CrystalDialog", "Create custom crystal structure", None)
        )
        self.buttonAddAtom.setText(QCoreApplication.translate("CrystalDialog", "Add Atom", None))
        self.checkBoxPreview.setText(QCoreApplication.translate("CrystalDialog", "Show Preview", None))
        self.selectCrystalSystem.setItemText(0, QCoreApplication.translate("CrystalDialog", "Cubic", None))
        self.selectCrystalSystem.setItemText(1, QCoreApplication.translate("CrystalDialog", "Tetragonal", None))
        self.selectCrystalSystem.setItemText(2, QCoreApplication.translate("CrystalDialog", "Orthorhombic", None))

        self.selectSpaceGroup.setItemText(0, QCoreApplication.translate("CrystalDialog", "m3m", None))
        self.selectSpaceGroup.setItemText(1, QCoreApplication.translate("CrystalDialog", "4/mmm", None))
        self.selectSpaceGroup.setItemText(2, QCoreApplication.translate("CrystalDialog", "mmm", None))

        self.labelElementSymbol.setText(QCoreApplication.translate("CrystalDialog", "Element", None))
        self.labelCoord_a.setText(QCoreApplication.translate("CrystalDialog", "coord. a", None))
        self.labelCoord_b.setText(QCoreApplication.translate("CrystalDialog", "coord. b", None))
        self.labelCoord_c.setText(QCoreApplication.translate("CrystalDialog", "coord. c", None))
        self.labelLatConst_a.setText(QCoreApplication.translate("CrystalDialog", "a", None))
        self.labelLatConst_b.setText(QCoreApplication.translate("CrystalDialog", "b", None))
        self.labelLatConst_C.setText(QCoreApplication.translate("CrystalDialog", "c", None))
        self.labelTitleLatConst.setText(QCoreApplication.translate("CrystalDialog", "Lattice constants", None))
        self.labelTitleSupercell.setText(QCoreApplication.translate("CrystalDialog", "Supercell", None))
        self.labelSupercell_a.setText(
            QCoreApplication.translate(
                "CrystalDialog", "<html><head/><body><p>N<sub>a</sub><br/></p></body></html>", None
            )
        )
        self.labelSupercell_b.setText(
            QCoreApplication.translate(
                "CrystalDialog", "<html><head/><body><p>N<sub>b</sub><br/></p></body></html>", None
            )
        )
        self.labelSupercell_c.setText(
            QCoreApplication.translate(
                "CrystalDialog", "<html><head/><body><p>N<sub>c</sub><br/></p></body></html>", None
            )
        )
        self.pushButton.setText(QCoreApplication.translate("CrystalDialog", "Clear Atoms", None))

    # retranslateUi
