# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mos_dialog.ui'
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
    QHeaderView, QLabel, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_MOs_dialog(object):
    def setupUi(self, MOs_dialog):
        if not MOs_dialog.objectName():
            MOs_dialog.setObjectName(u"MOs_dialog")
        MOs_dialog.resize(400, 300)
        self.displayMos = QPushButton(MOs_dialog)
        self.displayMos.setObjectName(u"displayMos")
        self.displayMos.setGeometry(QRect(280, 250, 100, 32))
        self.label = QLabel(MOs_dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 81, 16))
        self.label_2 = QLabel(MOs_dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(90, 10, 101, 16))
        self.label_3 = QLabel(MOs_dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 30, 91, 16))
        self.orbitalSelector = QTableWidget(MOs_dialog)
        self.orbitalSelector.setObjectName(u"orbitalSelector")
        self.orbitalSelector.setGeometry(QRect(10, 50, 171, 171))
        self.label_4 = QLabel(MOs_dialog)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(210, 10, 91, 16))
        self.cubeBoxSizeSpinBox = QDoubleSpinBox(MOs_dialog)
        self.cubeBoxSizeSpinBox.setObjectName(u"cubeBoxSizeSpinBox")
        self.cubeBoxSizeSpinBox.setGeometry(QRect(310, 7, 62, 22))
        self.cubeBoxSizeSpinBox.setDecimals(1)
        self.cubeBoxSizeSpinBox.setMinimum(-1.900000000000000)
        self.cubeBoxSizeSpinBox.setMaximum(20.000000000000000)
        self.cubeBoxSizeSpinBox.setSingleStep(0.100000000000000)
        self.cubeBoxSizeSpinBox.setValue(0.000000000000000)
        self.toggleDisplayBoxButton = QPushButton(MOs_dialog)
        self.toggleDisplayBoxButton.setObjectName(u"toggleDisplayBoxButton")
        self.toggleDisplayBoxButton.setGeometry(QRect(210, 30, 161, 32))
        self.voxelSizeSpinBox = QDoubleSpinBox(MOs_dialog)
        self.voxelSizeSpinBox.setObjectName(u"voxelSizeSpinBox")
        self.voxelSizeSpinBox.setGeometry(QRect(310, 57, 62, 22))
        self.voxelSizeSpinBox.setDecimals(2)
        self.voxelSizeSpinBox.setMinimum(0.050000000000000)
        self.voxelSizeSpinBox.setMaximum(1.000000000000000)
        self.voxelSizeSpinBox.setSingleStep(0.050000000000000)
        self.voxelSizeSpinBox.setValue(0.200000000000000)
        self.label_5 = QLabel(MOs_dialog)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(210, 60, 91, 16))
        self.label_6 = QLabel(MOs_dialog)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(210, 83, 91, 16))
        self.isoValueSpinBox = QDoubleSpinBox(MOs_dialog)
        self.isoValueSpinBox.setObjectName(u"isoValueSpinBox")
        self.isoValueSpinBox.setGeometry(QRect(310, 80, 62, 22))
        self.isoValueSpinBox.setDecimals(3)
        self.isoValueSpinBox.setMinimum(0.001000000000000)
        self.isoValueSpinBox.setMaximum(1.000000000000000)
        self.isoValueSpinBox.setSingleStep(0.010000000000000)
        self.isoValueSpinBox.setValue(0.200000000000000)
        self.checkBoxWireMesh = QCheckBox(MOs_dialog)
        self.checkBoxWireMesh.setObjectName(u"checkBoxWireMesh")
        self.checkBoxWireMesh.setGeometry(QRect(210, 100, 85, 20))

        self.retranslateUi(MOs_dialog)

        QMetaObject.connectSlotsByName(MOs_dialog)
    # setupUi

    def retranslateUi(self, MOs_dialog):
        MOs_dialog.setWindowTitle(QCoreApplication.translate("MOs_dialog", u"Dialog", None))
        self.displayMos.setText(QCoreApplication.translate("MOs_dialog", u"Display Orbital", None))
        self.label.setText(QCoreApplication.translate("MOs_dialog", u"Orbital type:", None))
        self.label_2.setText(QCoreApplication.translate("MOs_dialog", u"Cartesian", None))
        self.label_3.setText(QCoreApplication.translate("MOs_dialog", u"Select Orbital", None))
        self.label_4.setText(QCoreApplication.translate("MOs_dialog", u"Box Size", None))
        self.toggleDisplayBoxButton.setText(QCoreApplication.translate("MOs_dialog", u"Display Box", None))
        self.label_5.setText(QCoreApplication.translate("MOs_dialog", u"Voxel Size", None))
        self.label_6.setText(QCoreApplication.translate("MOs_dialog", u"Isovalue", None))
        self.checkBoxWireMesh.setText(QCoreApplication.translate("MOs_dialog", u"Wire Mesh", None))
    # retranslateUi

