# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'isoline_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QFrame,
    QHeaderView, QLabel, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_isoline_dialog(object):
    def setupUi(self, isoline_dialog):
        if not isoline_dialog.objectName():
            isoline_dialog.setObjectName(u"isoline_dialog")
        isoline_dialog.resize(425, 411)
        isoline_dialog.setMinimumSize(QSize(425, 317))
        self.label = QLabel(isoline_dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 81, 16))
        self.orbTypeLabel = QLabel(isoline_dialog)
        self.orbTypeLabel.setObjectName(u"orbTypeLabel")
        self.orbTypeLabel.setGeometry(QRect(90, 10, 101, 16))
        self.orbTypeLabel.setMaximumSize(QSize(101, 16))
        self.label_3 = QLabel(isoline_dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 50, 91, 16))
        self.orbitalSelector = QTableWidget(isoline_dialog)
        self.orbitalSelector.setObjectName(u"orbitalSelector")
        self.orbitalSelector.setGeometry(QRect(10, 70, 191, 331))
        self.label_7 = QLabel(isoline_dialog)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 30, 91, 16))
        self.alphaCheckBox = QCheckBox(isoline_dialog)
        self.alphaCheckBox.setObjectName(u"alphaCheckBox")
        self.alphaCheckBox.setGeometry(QRect(90, 30, 61, 21))
        self.betaCheckBox = QCheckBox(isoline_dialog)
        self.betaCheckBox.setObjectName(u"betaCheckBox")
        self.betaCheckBox.setGeometry(QRect(150, 30, 61, 20))
        self.restrictedLabel = QLabel(isoline_dialog)
        self.restrictedLabel.setObjectName(u"restrictedLabel")
        self.restrictedLabel.setGeometry(QRect(90, 30, 61, 16))
        self.frame = QFrame(isoline_dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(210, 260, 211, 141))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 40, 131, 20))
        self.label_8 = QLabel(self.frame)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(10, 80, 161, 20))
        self.exactCountLabel = QLabel(self.frame)
        self.exactCountLabel.setObjectName(u"exactCountLabel")
        self.exactCountLabel.setGeometry(QRect(10, 60, 131, 20))
        self.normalizationButton = QPushButton(self.frame)
        self.normalizationButton.setObjectName(u"normalizationButton")
        self.normalizationButton.setGeometry(QRect(10, 10, 190, 32))
        self.normalizationButton.setAutoDefault(False)
        self.calculatedCountLabel = QLabel(self.frame)
        self.calculatedCountLabel.setObjectName(u"calculatedCountLabel")
        self.calculatedCountLabel.setGeometry(QRect(10, 100, 131, 20))
        self.displayMos = QPushButton(isoline_dialog)
        self.displayMos.setObjectName(u"displayMos")
        self.displayMos.setGeometry(QRect(220, 10, 190, 32))
        self.displayMos.setAutoDefault(False)
        self.frame_3 = QFrame(isoline_dialog)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setGeometry(QRect(210, 170, 211, 91))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.label_12 = QLabel(self.frame_3)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(10, 60, 58, 16))
        self.colorPlusButton = QPushButton(self.frame_3)
        self.colorPlusButton.setObjectName(u"colorPlusButton")
        self.colorPlusButton.setGeometry(QRect(90, 10, 100, 32))
        self.label_11 = QLabel(self.frame_3)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(10, 20, 58, 16))
        self.colorMinusButton = QPushButton(self.frame_3)
        self.colorMinusButton.setObjectName(u"colorMinusButton")
        self.colorMinusButton.setGeometry(QRect(90, 50, 100, 32))

        self.retranslateUi(isoline_dialog)

        QMetaObject.connectSlotsByName(isoline_dialog)
    # setupUi

    def retranslateUi(self, isoline_dialog):
        isoline_dialog.setWindowTitle(QCoreApplication.translate("isoline_dialog", u"Orbitals", None))
        self.label.setText(QCoreApplication.translate("isoline_dialog", u"Orbital type:", None))
        self.orbTypeLabel.setText(QCoreApplication.translate("isoline_dialog", u"Cartesian", None))
        self.label_3.setText(QCoreApplication.translate("isoline_dialog", u"Select Orbital:", None))
        self.label_7.setText(QCoreApplication.translate("isoline_dialog", u"Select Spin:", None))
        self.alphaCheckBox.setText(QCoreApplication.translate("isoline_dialog", u"Alpha", None))
        self.betaCheckBox.setText(QCoreApplication.translate("isoline_dialog", u"Beta", None))
        self.restrictedLabel.setText(QCoreApplication.translate("isoline_dialog", u"Restricted", None))
        self.label_2.setText(QCoreApplication.translate("isoline_dialog", u"Exact Electroncount:", None))
        self.label_8.setText(QCoreApplication.translate("isoline_dialog", u"Calculated Electroncount:", None))
        self.exactCountLabel.setText("")
        self.normalizationButton.setText(QCoreApplication.translate("isoline_dialog", u"Check Normalization", None))
        self.calculatedCountLabel.setText("")
        self.displayMos.setText(QCoreApplication.translate("isoline_dialog", u"Display Orbital", None))
        self.label_12.setText(QCoreApplication.translate("isoline_dialog", u"Color -", None))
        self.colorPlusButton.setText(QCoreApplication.translate("isoline_dialog", u"Select", None))
        self.label_11.setText(QCoreApplication.translate("isoline_dialog", u"Color +", None))
        self.colorMinusButton.setText(QCoreApplication.translate("isoline_dialog", u"Select", None))
    # retranslateUi

