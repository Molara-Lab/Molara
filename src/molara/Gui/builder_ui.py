# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'builder.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QSizePolicy, QWidget)

class Ui_builder(object):
    def setupUi(self, builder):
        if not builder.objectName():
            builder.setObjectName(u"builder")
        builder.resize(400, 300)
        self.buttonBox = QDialogButtonBox(builder)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.retranslateUi(builder)
        self.buttonBox.accepted.connect(builder.accept)
        self.buttonBox.rejected.connect(builder.reject)

        QMetaObject.connectSlotsByName(builder)
    # setupUi

    def retranslateUi(self, builder):
        builder.setWindowTitle(QCoreApplication.translate("builder", u"Dialog", None))
    # retranslateUi

