# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pda.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QDoubleSpinBox, QFrame,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpinBox, QTreeWidget, QTreeWidgetItem,
    QWidget)

class Ui_pda(object):
    def setupUi(self, pda):
        if not pda.objectName():
            pda.setObjectName(u"pda")
        pda.resize(642, 398)
        pda.setMinimumSize(QSize(100, 100))
        pda.setMaximumSize(QSize(700, 600))
        self.structurSelector = QTreeWidget(pda)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.structurSelector.setHeaderItem(__qtreewidgetitem)
        self.structurSelector.setObjectName(u"structurSelector")
        self.structurSelector.setGeometry(QRect(0, 0, 310, 391))
        self.frame = QFrame(pda)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(320, 0, 321, 131))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.show_all_of_clusterButton = QPushButton(self.frame)
        self.show_all_of_clusterButton.setObjectName(u"show_all_of_clusterButton")
        self.show_all_of_clusterButton.setGeometry(QRect(10, 10, 151, 32))
        self.show_spin_corrButton = QPushButton(self.frame)
        self.show_spin_corrButton.setObjectName(u"show_spin_corrButton")
        self.show_spin_corrButton.setGeometry(QRect(10, 40, 151, 32))
        self.deselect_all_button = QPushButton(self.frame)
        self.deselect_all_button.setObjectName(u"deselect_all_button")
        self.deselect_all_button.setGeometry(QRect(10, 70, 151, 32))
        self.Spin_correlationSpinBox = QDoubleSpinBox(self.frame)
        self.Spin_correlationSpinBox.setObjectName(u"Spin_correlationSpinBox")
        self.Spin_correlationSpinBox.setGeometry(QRect(240, 47, 70, 20))
        self.Spin_correlationSpinBox.setDecimals(1)
        self.Spin_correlationSpinBox.setValue(100.000000000000000)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(170, 48, 61, 16))
        self.reference_phiLineEdit = QLineEdit(self.frame)
        self.reference_phiLineEdit.setObjectName(u"reference_phiLineEdit")
        self.reference_phiLineEdit.setGeometry(QRect(170, 100, 140, 21))
        self.label_7 = QLabel(self.frame)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 100, 150, 16))
        self.frame_2 = QFrame(pda)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setGeometry(QRect(320, 140, 321, 91))
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.label_4 = QLabel(self.frame_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 0, 81, 16))
        self.label_5 = QLabel(self.frame_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(160, 0, 81, 16))
        self.eigenvalueLabel = QLabel(self.frame_2)
        self.eigenvalueLabel.setObjectName(u"eigenvalueLabel")
        self.eigenvalueLabel.setGeometry(QRect(240, 0, 81, 16))
        self.eigenvectorSpinBox = QSpinBox(self.frame_2)
        self.eigenvectorSpinBox.setObjectName(u"eigenvectorSpinBox")
        self.eigenvectorSpinBox.setGeometry(QRect(90, 0, 60, 22))
        self.label_6 = QLabel(self.frame_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 30, 71, 16))
        self.deflectionSpinBox = QDoubleSpinBox(self.frame_2)
        self.deflectionSpinBox.setObjectName(u"deflectionSpinBox")
        self.deflectionSpinBox.setGeometry(QRect(90, 30, 62, 22))
        self.deflectionSpinBox.setDecimals(1)
        self.deflectionSpinBox.setMinimum(-10.000000000000000)
        self.deflectionSpinBox.setMaximum(10.000000000000000)
        self.deflectionSpinBox.setSingleStep(0.100000000000000)
        self.deflectionSpinBox.setValue(1.000000000000000)
        self.show_eigenvectorButton = QPushButton(self.frame_2)
        self.show_eigenvectorButton.setObjectName(u"show_eigenvectorButton")
        self.show_eigenvectorButton.setGeometry(QRect(10, 50, 151, 32))

        self.retranslateUi(pda)

        QMetaObject.connectSlotsByName(pda)
    # setupUi

    def retranslateUi(self, pda):
        pda.setWindowTitle(QCoreApplication.translate("pda", u"Probability Density Analysis", None))
        self.show_all_of_clusterButton.setText(QCoreApplication.translate("pda", u"PushButton", None))
        self.show_spin_corrButton.setText(QCoreApplication.translate("pda", u"PushButton", None))
        self.deselect_all_button.setText(QCoreApplication.translate("pda", u"PushButton", None))
        self.label.setText(QCoreApplication.translate("pda", u"Value / %", None))
        self.label_7.setText(QCoreApplication.translate("pda", u"Reference Phi Value:", None))
        self.label_4.setText(QCoreApplication.translate("pda", u"Eigenvector:", None))
        self.label_5.setText(QCoreApplication.translate("pda", u"Eigenvalue:", None))
        self.eigenvalueLabel.setText("")
        self.label_6.setText(QCoreApplication.translate("pda", u"Deflection:", None))
        self.show_eigenvectorButton.setText(QCoreApplication.translate("pda", u"PushButton", None))
    # retranslateUi

