# -*- coding: utf-8 -*-

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


class Ui_Dialog(object):
    def setupUi(self, Dialog: QDialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(400, 350)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setGeometry(QRect(40, 310, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonAddAtom = QPushButton(Dialog)
        self.buttonAddAtom.setObjectName("buttonAddAtom")
        self.buttonAddAtom.setGeometry(QRect(300, 70, 90, 28))
        self.checkBoxPreview = QCheckBox(Dialog)
        self.checkBoxPreview.setObjectName("checkBoxPreview")
        self.checkBoxPreview.setEnabled(False)
        self.checkBoxPreview.setGeometry(QRect(200, 280, 131, 21))
        self.line = QFrame(Dialog)
        self.line.setObjectName("line")
        self.line.setGeometry(QRect(110, 10, 20, 331))
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.selectCrystalSystem = QComboBox(Dialog)
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.addItem("")
        self.selectCrystalSystem.setObjectName("selectCrystalSystem")
        self.selectCrystalSystem.setEnabled(True)
        self.selectCrystalSystem.setGeometry(QRect(20, 10, 76, 24))
        self.selectSpaceGroup = QComboBox(Dialog)
        self.selectSpaceGroup.addItem("")
        self.selectSpaceGroup.addItem("")
        self.selectSpaceGroup.addItem("")
        self.selectSpaceGroup.setObjectName("selectSpaceGroup")
        self.selectSpaceGroup.setEnabled(True)
        self.selectSpaceGroup.setGeometry(QRect(20, 40, 76, 24))
        self.inputLatConst_a = QDoubleSpinBox(Dialog)
        self.inputLatConst_a.setObjectName("inputLatConst_a")
        self.inputLatConst_a.setGeometry(QRect(50, 110, 62, 26))
        self.inputLatConst_a.setMinimum(0.010000000000000)
        self.inputLatConst_a.setSingleStep(0.010000000000000)
        self.inputLatConst_a.setValue(1.000000000000000)
        self.inputLatConst_b = QDoubleSpinBox(Dialog)
        self.inputLatConst_b.setObjectName("inputLatConst_b")
        self.inputLatConst_b.setEnabled(False)
        self.inputLatConst_b.setGeometry(QRect(50, 140, 62, 26))
        self.inputLatConst_b.setMinimum(0.010000000000000)
        self.inputLatConst_b.setSingleStep(0.010000000000000)
        self.inputLatConst_b.setValue(1.000000000000000)
        self.inputLatConst_c = QDoubleSpinBox(Dialog)
        self.inputLatConst_c.setObjectName("inputLatConst_c")
        self.inputLatConst_c.setEnabled(False)
        self.inputLatConst_c.setGeometry(QRect(50, 170, 62, 26))
        self.inputLatConst_c.setMinimum(0.010000000000000)
        self.inputLatConst_c.setSingleStep(0.010000000000000)
        self.inputLatConst_c.setValue(1.000000000000000)
        self.inputAtomCoord_a = QDoubleSpinBox(Dialog)
        self.inputAtomCoord_a.setObjectName("inputAtomCoord_a")
        self.inputAtomCoord_a.setGeometry(QRect(190, 30, 62, 26))
        self.inputAtomCoord_a.setMaximum(0.990000000000000)
        self.inputAtomCoord_a.setSingleStep(0.010000000000000)
        self.inputAtomCoord_b = QDoubleSpinBox(Dialog)
        self.inputAtomCoord_b.setObjectName("inputAtomCoord_b")
        self.inputAtomCoord_b.setGeometry(QRect(260, 30, 62, 26))
        self.inputAtomCoord_b.setMaximum(0.990000000000000)
        self.inputAtomCoord_b.setSingleStep(0.010000000000000)
        self.inputAtomCoord_c = QDoubleSpinBox(Dialog)
        self.inputAtomCoord_c.setObjectName("inputAtomCoord_c")
        self.inputAtomCoord_c.setGeometry(QRect(330, 30, 62, 26))
        self.inputAtomCoord_c.setMaximum(0.990000000000000)
        self.inputAtomCoord_c.setSingleStep(0.010000000000000)
        self.inputElementSymbol = QLineEdit(Dialog)
        self.inputElementSymbol.setObjectName("inputElementSymbol")
        self.inputElementSymbol.setEnabled(True)
        self.inputElementSymbol.setGeometry(QRect(130, 30, 51, 28))
        self.labelElementSymbol = QLabel(Dialog)
        self.labelElementSymbol.setObjectName("labelElementSymbol")
        self.labelElementSymbol.setGeometry(QRect(130, 10, 58, 16))
        self.labelCoord_a = QLabel(Dialog)
        self.labelCoord_a.setObjectName("labelCoord_a")
        self.labelCoord_a.setGeometry(QRect(190, 10, 58, 16))
        self.labelCoord_b = QLabel(Dialog)
        self.labelCoord_b.setObjectName("labelCoord_b")
        self.labelCoord_b.setGeometry(QRect(260, 10, 58, 16))
        self.labelCoord_c = QLabel(Dialog)
        self.labelCoord_c.setObjectName("labelCoord_c")
        self.labelCoord_c.setGeometry(QRect(330, 10, 58, 16))
        self.labelLatConst_a = QLabel(Dialog)
        self.labelLatConst_a.setObjectName("labelLatConst_a")
        self.labelLatConst_a.setGeometry(QRect(20, 110, 16, 20))
        self.labelLatConst_b = QLabel(Dialog)
        self.labelLatConst_b.setObjectName("labelLatConst_b")
        self.labelLatConst_b.setGeometry(QRect(20, 140, 16, 20))
        self.labelLatConst_C = QLabel(Dialog)
        self.labelLatConst_C.setObjectName("labelLatConst_C")
        self.labelLatConst_C.setGeometry(QRect(20, 170, 16, 20))
        self.labelTitleLatConst = QLabel(Dialog)
        self.labelTitleLatConst.setObjectName("labelTitleLatConst")
        self.labelTitleLatConst.setGeometry(QRect(10, 90, 101, 16))
        self.inputSupercell_a = QSpinBox(Dialog)
        self.inputSupercell_a.setObjectName("inputSupercell_a")
        self.inputSupercell_a.setGeometry(QRect(50, 240, 42, 26))
        self.inputSupercell_a.setMinimum(1)
        self.inputSupercell_b = QSpinBox(Dialog)
        self.inputSupercell_b.setObjectName("inputSupercell_b")
        self.inputSupercell_b.setGeometry(QRect(50, 270, 42, 26))
        self.inputSupercell_b.setMinimum(1)
        self.inputSupercell_c = QSpinBox(Dialog)
        self.inputSupercell_c.setObjectName("inputSupercell_c")
        self.inputSupercell_c.setGeometry(QRect(50, 300, 42, 26))
        self.inputSupercell_c.setMinimum(1)
        self.labelTitleSupercell = QLabel(Dialog)
        self.labelTitleSupercell.setObjectName("labelTitleSupercell")
        self.labelTitleSupercell.setGeometry(QRect(10, 210, 101, 16))
        self.labelSupercell_a = QLabel(Dialog)
        self.labelSupercell_a.setObjectName("labelSupercell_a")
        self.labelSupercell_a.setGeometry(QRect(20, 240, 16, 20))
        self.labelSupercell_b = QLabel(Dialog)
        self.labelSupercell_b.setObjectName("labelSupercell_b")
        self.labelSupercell_b.setGeometry(QRect(20, 270, 16, 20))
        self.labelSupercell_c = QLabel(Dialog)
        self.labelSupercell_c.setObjectName("labelSupercell_c")
        self.labelSupercell_c.setGeometry(QRect(20, 300, 16, 20))
        self.listAtoms = QTableWidget(Dialog)
        self.listAtoms.setObjectName("listAtoms")
        self.listAtoms.setGeometry(QRect(130, 110, 256, 161))
        self.listAtoms.horizontalHeader().setCascadingSectionResizes(False)
        self.listAtoms.horizontalHeader().setMinimumSectionSize(30)
        self.listAtoms.horizontalHeader().setDefaultSectionSize(60)
        self.listAtoms.horizontalHeader().setStretchLastSection(True)
        self.pushButton = QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setGeometry(QRect(130, 70, 90, 28))

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog: QDialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Dialog", None))
        self.buttonAddAtom.setText(QCoreApplication.translate("Dialog", "Add Atom", None))
        self.checkBoxPreview.setText(QCoreApplication.translate("Dialog", "Show Preview", None))
        self.selectCrystalSystem.setItemText(0, QCoreApplication.translate("Dialog", "Cubic", None))
        self.selectCrystalSystem.setItemText(1, QCoreApplication.translate("Dialog", "Tetragonal", None))
        self.selectCrystalSystem.setItemText(2, QCoreApplication.translate("Dialog", "Orthorhombic", None))

        self.selectSpaceGroup.setItemText(0, QCoreApplication.translate("Dialog", "m3m", None))
        self.selectSpaceGroup.setItemText(1, QCoreApplication.translate("Dialog", "4/mmm", None))
        self.selectSpaceGroup.setItemText(2, QCoreApplication.translate("Dialog", "mmm", None))

        self.labelElementSymbol.setText(QCoreApplication.translate("Dialog", "Element", None))
        self.labelCoord_a.setText(QCoreApplication.translate("Dialog", "coord. a", None))
        self.labelCoord_b.setText(QCoreApplication.translate("Dialog", "coord. b", None))
        self.labelCoord_c.setText(QCoreApplication.translate("Dialog", "coord. c", None))
        self.labelLatConst_a.setText(QCoreApplication.translate("Dialog", "a", None))
        self.labelLatConst_b.setText(QCoreApplication.translate("Dialog", "b", None))
        self.labelLatConst_C.setText(QCoreApplication.translate("Dialog", "c", None))
        self.labelTitleLatConst.setText(QCoreApplication.translate("Dialog", "Lattice constants", None))
        self.labelTitleSupercell.setText(QCoreApplication.translate("Dialog", "Supercell", None))
        self.labelSupercell_a.setText(
            QCoreApplication.translate("Dialog", "<html><head/><body><p>N<sub>a</sub><br/></p></body></html>", None)
        )
        self.labelSupercell_b.setText(
            QCoreApplication.translate("Dialog", "<html><head/><body><p>N<sub>b</sub><br/></p></body></html>", None)
        )
        self.labelSupercell_c.setText(
            QCoreApplication.translate("Dialog", "<html><head/><body><p>N<sub>c</sub><br/></p></body></html>", None)
        )
        self.pushButton.setText(QCoreApplication.translate("Dialog", "Clear Atoms", None))

    # retranslateUi
