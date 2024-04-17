# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'structure_customizer.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QDoubleSpinBox, QLabel,
    QPushButton, QSizePolicy, QWidget)

class Ui_structure_customizer(object):
    def setupUi(self, structure_customizer):
        if not structure_customizer.objectName():
            structure_customizer.setObjectName(u"structure_customizer")
        structure_customizer.resize(400, 71)
        structure_customizer.setMinimumSize(QSize(400, 71))
        structure_customizer.setMaximumSize(QSize(400, 71))
        self.viewModeButton = QPushButton(structure_customizer)
        self.viewModeButton.setObjectName(u"viewModeButton")
        self.viewModeButton.setGeometry(QRect(10, 5, 100, 32))
        self.ballSizeSpinBox = QDoubleSpinBox(structure_customizer)
        self.ballSizeSpinBox.setObjectName(u"ballSizeSpinBox")
        self.ballSizeSpinBox.setGeometry(QRect(190, 10, 62, 22))
        self.ballSizeSpinBox.setMinimum(0.100000000000000)
        self.ballSizeSpinBox.setSingleStep(0.100000000000000)
        self.ballSizeSpinBox.setValue(1.000000000000000)
        self.stickSizeSpinBox = QDoubleSpinBox(structure_customizer)
        self.stickSizeSpinBox.setObjectName(u"stickSizeSpinBox")
        self.stickSizeSpinBox.setGeometry(QRect(190, 40, 62, 22))
        self.stickSizeSpinBox.setMinimum(0.100000000000000)
        self.stickSizeSpinBox.setSingleStep(0.100000000000000)
        self.applyButton = QPushButton(structure_customizer)
        self.applyButton.setObjectName(u"applyButton")
        self.applyButton.setGeometry(QRect(280, 20, 100, 32))
        self.ballSizeLabel = QLabel(structure_customizer)
        self.ballSizeLabel.setObjectName(u"ballSizeLabel")
        self.ballSizeLabel.setGeometry(QRect(128, 10, 60, 16))
        self.stickSizeLabel = QLabel(structure_customizer)
        self.stickSizeLabel.setObjectName(u"stickSizeLabel")
        self.stickSizeLabel.setGeometry(QRect(120, 40, 61, 20))
        self.toggleBondsButton = QPushButton(structure_customizer)
        self.toggleBondsButton.setObjectName(u"toggleBondsButton")
        self.toggleBondsButton.setGeometry(QRect(10, 35, 100, 32))

        self.retranslateUi(structure_customizer)

        QMetaObject.connectSlotsByName(structure_customizer)
    # setupUi

    def retranslateUi(self, structure_customizer):
        structure_customizer.setWindowTitle(QCoreApplication.translate("structure_customizer", u"Structure Customizer", None))
        self.viewModeButton.setText(QCoreApplication.translate("structure_customizer", u"Stick Mode", None))
        self.applyButton.setText(QCoreApplication.translate("structure_customizer", u"Apply Changes", None))
        self.ballSizeLabel.setText(QCoreApplication.translate("structure_customizer", u"Ball Size:", None))
        self.stickSizeLabel.setText(QCoreApplication.translate("structure_customizer", u"Stick Size:", None))
        self.toggleBondsButton.setText(QCoreApplication.translate("structure_customizer", u"Toggle Bonds", None))
    # retranslateUi
