# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'supercell_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QSizePolicy, QSpinBox, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(257, 204)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(60, 160, 181, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.inputSupercell_a = QSpinBox(Dialog)
        self.inputSupercell_a.setObjectName(u"inputSupercell_a")
        self.inputSupercell_a.setGeometry(QRect(30, 50, 42, 26))
        self.inputSupercell_a.setMinimum(1)
        self.inputSupercell_b = QSpinBox(Dialog)
        self.inputSupercell_b.setObjectName(u"inputSupercell_b")
        self.inputSupercell_b.setGeometry(QRect(80, 50, 42, 26))
        self.inputSupercell_b.setMinimum(1)
        self.inputSupercell_c = QSpinBox(Dialog)
        self.inputSupercell_c.setObjectName(u"inputSupercell_c")
        self.inputSupercell_c.setGeometry(QRect(130, 50, 42, 26))
        self.inputSupercell_c.setMinimum(1)
        self.labelSupercell_a = QLabel(Dialog)
        self.labelSupercell_a.setObjectName(u"labelSupercell_a")
        self.labelSupercell_a.setGeometry(QRect(40, 80, 21, 16))
        self.labelSupercell_b = QLabel(Dialog)
        self.labelSupercell_b.setObjectName(u"labelSupercell_b")
        self.labelSupercell_b.setGeometry(QRect(90, 80, 21, 16))
        self.labelSupercell_c = QLabel(Dialog)
        self.labelSupercell_c.setObjectName(u"labelSupercell_c")
        self.labelSupercell_c.setGeometry(QRect(140, 80, 21, 16))
        self.labelNumAtoms = QLabel(Dialog)
        self.labelNumAtoms.setObjectName(u"labelNumAtoms")
        self.labelNumAtoms.setGeometry(QRect(20, 110, 211, 41))
        self.labelNumAtoms.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 20, 171, 16))

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Change Supercell Dimensions", None))
        self.labelSupercell_a.setText(QCoreApplication.translate("Dialog", u"N<sub>a</sub>", None))
        self.labelSupercell_b.setText(QCoreApplication.translate("Dialog", u"N<sub>b</sub>", None))
        self.labelSupercell_c.setText(QCoreApplication.translate("Dialog", u"N<sub>c</sub>", None))
        self.labelNumAtoms.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Enter supercell dimensions", None))
    # retranslateUi
