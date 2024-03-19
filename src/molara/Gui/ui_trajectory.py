# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'trajectory.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
from PySide6.QtWidgets import (QApplication, QDial, QDialog, QLabel,
    QPushButton, QSizePolicy, QSlider, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 300)
        Dialog.setCursor(QCursor(Qt.ArrowCursor))
        self.PrevButton = QPushButton(Dialog)
        self.PrevButton.setObjectName(u"PrevButton")
        self.PrevButton.setGeometry(QRect(10, 260, 50, 32))
        self.NextButton = QPushButton(Dialog)
        self.NextButton.setObjectName(u"NextButton")
        self.NextButton.setGeometry(QRect(60, 260, 50, 32))
        self.verticalSlider = QSlider(Dialog)
        self.verticalSlider.setObjectName(u"verticalSlider")
        self.verticalSlider.setGeometry(QRect(370, 60, 22, 160))
        self.verticalSlider.setOrientation(Qt.Vertical)
        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(19, 19, 351, 231))
        self.speedDial = QDial(Dialog)
        self.speedDial.setObjectName(u"speedDial")
        self.speedDial.setGeometry(QRect(330, 255, 40, 40))
        self.speedDial.setMaximum(1000)
        self.speedDial.setValue(500)
        self.speedDial.setInvertedAppearance(True)
        self.speedDial.setInvertedControls(False)
        self.playStopButton = QPushButton(Dialog)
        self.playStopButton.setObjectName(u"playStopButton")
        self.playStopButton.setGeometry(QRect(120, 260, 50, 32))
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(220, 267, 101, 20))

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.PrevButton.setText(QCoreApplication.translate("Dialog", u"<", None))
        self.NextButton.setText(QCoreApplication.translate("Dialog", u">", None))
        self.playStopButton.setText(QCoreApplication.translate("Dialog", u"Play", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Animation speed:", None))
    # retranslateUi
