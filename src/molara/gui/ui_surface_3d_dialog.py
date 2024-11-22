# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'surface_3d_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QDoubleSpinBox,
    QLabel, QPushButton, QSizePolicy, QWidget)

class Ui_Surface3D_dialog(object):
    def setupUi(self, Surface3D_dialog):
        if not Surface3D_dialog.objectName():
            Surface3D_dialog.setObjectName(u"Surface3D_dialog")
        Surface3D_dialog.resize(198, 184)
        Surface3D_dialog.setMaximumSize(QSize(425, 317))
        self.visualize_surfaceButton = QPushButton(Surface3D_dialog)
        self.visualize_surfaceButton.setObjectName(u"visualize_surfaceButton")
        self.visualize_surfaceButton.setGeometry(QRect(10, 150, 181, 32))
        self.isoSpinBox = QDoubleSpinBox(Surface3D_dialog)
        self.isoSpinBox.setObjectName(u"isoSpinBox")
        self.isoSpinBox.setGeometry(QRect(110, 10, 62, 22))
        self.isoSpinBox.setDecimals(4)
        self.isoSpinBox.setMinimum(0.000100000000000)
        self.isoSpinBox.setMaximum(1.000000000000000)
        self.isoSpinBox.setSingleStep(0.005000000000000)
        self.isoSpinBox.setValue(0.200000000000000)
        self.label_12 = QLabel(Surface3D_dialog)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(10, 90, 58, 16))
        self.colorPlusButton = QPushButton(Surface3D_dialog)
        self.colorPlusButton.setObjectName(u"colorPlusButton")
        self.colorPlusButton.setGeometry(QRect(90, 40, 100, 32))
        self.label_11 = QLabel(Surface3D_dialog)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(10, 50, 58, 16))
        self.colorMinusButton = QPushButton(Surface3D_dialog)
        self.colorMinusButton.setObjectName(u"colorMinusButton")
        self.colorMinusButton.setGeometry(QRect(90, 80, 100, 32))
        self.label = QLabel(Surface3D_dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 58, 16))
        self.checkBoxWireMesh = QCheckBox(Surface3D_dialog)
        self.checkBoxWireMesh.setObjectName(u"checkBoxWireMesh")
        self.checkBoxWireMesh.setGeometry(QRect(10, 130, 85, 20))

        self.retranslateUi(Surface3D_dialog)

        QMetaObject.connectSlotsByName(Surface3D_dialog)
    # setupUi

    def retranslateUi(self, Surface3D_dialog):
        Surface3D_dialog.setWindowTitle(QCoreApplication.translate("Surface3D_dialog", u"3D Surface", None))
        self.visualize_surfaceButton.setText(QCoreApplication.translate("Surface3D_dialog", u"Display Surface", None))
        self.label_12.setText(QCoreApplication.translate("Surface3D_dialog", u"Color -", None))
        self.colorPlusButton.setText(QCoreApplication.translate("Surface3D_dialog", u"Select", None))
        self.label_11.setText(QCoreApplication.translate("Surface3D_dialog", u"Color +", None))
        self.colorMinusButton.setText(QCoreApplication.translate("Surface3D_dialog", u"Select", None))
        self.label.setText(QCoreApplication.translate("Surface3D_dialog", u"Isovalue:", None))
        self.checkBoxWireMesh.setText(QCoreApplication.translate("Surface3D_dialog", u"Wire Mesh", None))
    # retranslateUi
