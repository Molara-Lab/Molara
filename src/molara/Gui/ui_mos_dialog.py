# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mos_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.6.0
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
from PySide6.QtWidgets import (QApplication, QDialog, QPushButton, QSizePolicy,
    QWidget)

class Ui_MOs_dialog(object):
    def setupUi(self, MOs_dialog):
        if not MOs_dialog.objectName():
            MOs_dialog.setObjectName(u"MOs_dialog")
        MOs_dialog.resize(400, 300)
        self.pushButton = QPushButton(MOs_dialog)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(90, 100, 100, 32))

        self.retranslateUi(MOs_dialog)

        QMetaObject.connectSlotsByName(MOs_dialog)
    # setupUi

    def retranslateUi(self, MOs_dialog):
        MOs_dialog.setWindowTitle(QCoreApplication.translate("MOs_dialog", u"Dialog", None))
        self.pushButton.setText(QCoreApplication.translate("MOs_dialog", u"PushButton", None))
    # retranslateUi

