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
from PySide6.QtWidgets import (QApplication, QDialog, QHeaderView, QLabel,
    QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
    QWidget)

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
        self.label_2.setGeometry(QRect(90, 10, 131, 16))
        self.label_3 = QLabel(MOs_dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 30, 91, 16))
        self.orbitalSelector = QTableWidget(MOs_dialog)
        self.orbitalSelector.setObjectName(u"orbitalSelector")
        self.orbitalSelector.setGeometry(QRect(10, 50, 251, 171))

        self.retranslateUi(MOs_dialog)

        QMetaObject.connectSlotsByName(MOs_dialog)
    # setupUi

    def retranslateUi(self, MOs_dialog):
        MOs_dialog.setWindowTitle(QCoreApplication.translate("MOs_dialog", u"Dialog", None))
        self.displayMos.setText(QCoreApplication.translate("MOs_dialog", u"Display Orbital", None))
        self.label.setText(QCoreApplication.translate("MOs_dialog", u"Orbital type:", None))
        self.label_2.setText(QCoreApplication.translate("MOs_dialog", u"Cartesian", None))
        self.label_3.setText(QCoreApplication.translate("MOs_dialog", u"Select Orbital", None))
    # retranslateUi

