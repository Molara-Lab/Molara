# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'trajectory.ui'
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
from PySide6.QtWidgets import (QApplication, QDial, QDialog, QLabel,
    QPushButton, QSizePolicy, QSlider, QWidget)

class Ui_traj_dialog(object):
    def setupUi(self, traj_dialog):
        if not traj_dialog.objectName():
            traj_dialog.setObjectName(u"traj_dialog")
        traj_dialog.resize(400, 300)
        traj_dialog.setCursor(QCursor(Qt.ArrowCursor))
        self.PrevButton = QPushButton(traj_dialog)
        self.PrevButton.setObjectName(u"PrevButton")
        self.PrevButton.setGeometry(QRect(10, 260, 50, 32))
        self.NextButton = QPushButton(traj_dialog)
        self.NextButton.setObjectName(u"NextButton")
        self.NextButton.setGeometry(QRect(60, 260, 50, 32))
        self.verticalSlider = QSlider(traj_dialog)
        self.verticalSlider.setObjectName(u"verticalSlider")
        self.verticalSlider.setGeometry(QRect(370, 60, 22, 160))
        self.verticalSlider.setOrientation(Qt.Vertical)
        self.widget = QWidget(traj_dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(19, 19, 351, 231))
        self.speedDial = QDial(traj_dialog)
        self.speedDial.setObjectName(u"speedDial")
        self.speedDial.setGeometry(QRect(350, 250, 40, 40))
        self.speedDial.setMaximum(1000)
        self.speedDial.setValue(500)
        self.speedDial.setInvertedAppearance(True)
        self.speedDial.setInvertedControls(False)
        self.playStopButton = QPushButton(traj_dialog)
        self.playStopButton.setObjectName(u"playStopButton")
        self.playStopButton.setGeometry(QRect(120, 260, 50, 32))
        self.label = QLabel(traj_dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(310, 260, 41, 20))
        self.overlayButton = QPushButton(traj_dialog)
        self.overlayButton.setObjectName(u"overlayButton")
        self.overlayButton.setGeometry(QRect(180, 260, 100, 32))
        QWidget.setTabOrder(self.PrevButton, self.NextButton)
        QWidget.setTabOrder(self.NextButton, self.playStopButton)
        QWidget.setTabOrder(self.playStopButton, self.speedDial)
        QWidget.setTabOrder(self.speedDial, self.verticalSlider)

        self.retranslateUi(traj_dialog)

        QMetaObject.connectSlotsByName(traj_dialog)
    # setupUi

    def retranslateUi(self, traj_dialog):
        traj_dialog.setWindowTitle(QCoreApplication.translate("traj_dialog", u"Molecules Controller", None))
        self.PrevButton.setText(QCoreApplication.translate("traj_dialog", u"<", None))
        self.NextButton.setText(QCoreApplication.translate("traj_dialog", u">", None))
        self.playStopButton.setText(QCoreApplication.translate("traj_dialog", u"Play", None))
        self.label.setText(QCoreApplication.translate("traj_dialog", u"Speed:", None))
        self.overlayButton.setText(QCoreApplication.translate("traj_dialog", u"Show all", None))
    # retranslateUi
