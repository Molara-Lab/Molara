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
from PySide6.QtWidgets import (QApplication, QDialog, QPushButton, QSizePolicy,
    QWidget)

class Ui_Surface3D_dialog(object):
    def setupUi(self, Surface3D_dialog):
        if not Surface3D_dialog.objectName():
            Surface3D_dialog.setObjectName(u"Surface3D_dialog")
        Surface3D_dialog.resize(425, 317)
        Surface3D_dialog.setMinimumSize(QSize(425, 317))
        Surface3D_dialog.setMaximumSize(QSize(425, 317))
        self.visualize_surface = QPushButton(Surface3D_dialog)
        self.visualize_surface.setObjectName(u"visualize_surface")
        self.visualize_surface.setGeometry(QRect(50, 60, 100, 32))

        self.retranslateUi(Surface3D_dialog)

        QMetaObject.connectSlotsByName(Surface3D_dialog)
    # setupUi

    def retranslateUi(self, Surface3D_dialog):
        Surface3D_dialog.setWindowTitle(QCoreApplication.translate("Surface3D_dialog", u"3D Surface", None))
        self.visualize_surface.setText(QCoreApplication.translate("Surface3D_dialog", u"PushButton", None))
    # retranslateUi

