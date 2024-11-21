# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'normalization_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QLabel,
    QPushButton, QSizePolicy, QWidget)

class Ui_normalization_dialog(object):
    def setupUi(self, normalization_dialog):
        if not normalization_dialog.objectName():
            normalization_dialog.setObjectName(u"normalization_dialog")
        normalization_dialog.resize(211, 140)
        normalization_dialog.setMinimumSize(QSize(211, 140))
        normalization_dialog.setMaximumSize(QSize(211, 140))
        self.normalizationFrame = QFrame(normalization_dialog)
        self.normalizationFrame.setObjectName(u"normalizationFrame")
        self.normalizationFrame.setGeometry(QRect(0, 1, 211, 140))
        self.normalizationFrame.setFrameShape(QFrame.StyledPanel)
        self.normalizationFrame.setFrameShadow(QFrame.Raised)
        self.label_2 = QLabel(self.normalizationFrame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 40, 131, 20))
        self.label_8 = QLabel(self.normalizationFrame)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setGeometry(QRect(10, 80, 161, 20))
        self.exactCountLabel = QLabel(self.normalizationFrame)
        self.exactCountLabel.setObjectName(u"exactCountLabel")
        self.exactCountLabel.setGeometry(QRect(10, 60, 180, 20))
        self.normalizationButton = QPushButton(self.normalizationFrame)
        self.normalizationButton.setObjectName(u"normalizationButton")
        self.normalizationButton.setGeometry(QRect(10, 10, 190, 32))
        self.normalizationButton.setAutoDefault(False)
        self.calculatedCountLabel = QLabel(self.normalizationFrame)
        self.calculatedCountLabel.setObjectName(u"calculatedCountLabel")
        self.calculatedCountLabel.setGeometry(QRect(10, 100, 180, 20))

        self.retranslateUi(normalization_dialog)

        QMetaObject.connectSlotsByName(normalization_dialog)
    # setupUi

    def retranslateUi(self, normalization_dialog):
        normalization_dialog.setWindowTitle(QCoreApplication.translate("normalization_dialog", u"Normalization", None))
        self.label_2.setText(QCoreApplication.translate("normalization_dialog", u"Exact Electroncount:", None))
        self.label_8.setText(QCoreApplication.translate("normalization_dialog", u"Calculated Electroncount:", None))
        self.exactCountLabel.setText("")
        self.normalizationButton.setText(QCoreApplication.translate("normalization_dialog", u"Check Normalization", None))
        self.calculatedCountLabel.setText("")
    # retranslateUi
