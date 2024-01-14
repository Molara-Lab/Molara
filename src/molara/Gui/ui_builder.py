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
    QDoubleSpinBox, QHeaderView, QLineEdit, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QTextBrowser,
    QWidget)

class Ui_builder(object):
    def setupUi(self, builder):
        if not builder.objectName():
            builder.setObjectName(u"builder")
        builder.resize(447, 310)
        self.buttonBox = QDialogButtonBox(builder)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 270, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self._1BondDistance = QDoubleSpinBox(builder)
        self._1BondDistance.setObjectName(u"_1BondDistance")
        self._1BondDistance.setGeometry(QRect(100, 230, 61, 31))
        self._1BondDistance.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self._1BondDistance.setMaximum(99999.000000000000000)
        self._2BondAngle = QDoubleSpinBox(builder)
        self._2BondAngle.setObjectName(u"_2BondAngle")
        self._2BondAngle.setGeometry(QRect(180, 230, 61, 31))
        self._2BondAngle.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self._2BondAngle.setMaximum(360.000000000000000)
        self._3DihedralAngle = QDoubleSpinBox(builder)
        self._3DihedralAngle.setObjectName(u"_3DihedralAngle")
        self._3DihedralAngle.setGeometry(QRect(260, 230, 61, 31))
        self._3DihedralAngle.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self._3DihedralAngle.setMaximum(360.000000000000000)
        self.AddAtomButton = QPushButton(builder)
        self.AddAtomButton.setObjectName(u"AddAtomButton")
        self.AddAtomButton.setGeometry(QRect(330, 230, 51, 31))
        self._0Element = QLineEdit(builder)
        self._0Element.setObjectName(u"_0Element")
        self._0Element.setGeometry(QRect(40, 230, 41, 31))
        self._0Element.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.tableWidget = QTableWidget(builder)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(40, 20, 381, 161))
        self.ErrorMessageBrowser = QTextBrowser(builder)
        self.ErrorMessageBrowser.setObjectName(u"ErrorMessageBrowser")
        self.ErrorMessageBrowser.setGeometry(QRect(40, 190, 381, 21))

        self.retranslateUi(builder)
        self.buttonBox.accepted.connect(builder.accept)
        self.buttonBox.rejected.connect(builder.reject)

        QMetaObject.connectSlotsByName(builder)
    # setupUi

    def retranslateUi(self, builder):
        builder.setWindowTitle(QCoreApplication.translate("builder", u"Dialog", None))
        self.AddAtomButton.setText(QCoreApplication.translate("builder", u"Add", None))
    # retranslateUi

