# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'builder.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QHeaderView, QLineEdit, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QTextBrowser,
    QWidget)

class Ui_builder(object):
    def setupUi(self, builder):
        if not builder.objectName():
            builder.setObjectName(u"builder")
        builder.resize(447, 310)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(builder.sizePolicy().hasHeightForWidth())
        builder.setSizePolicy(sizePolicy)
        builder.setMinimumSize(QSize(447, 310))
        builder.setMaximumSize(QSize(447, 310))
        self.buttonBox = QDialogButtonBox(builder)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(90, 270, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.Box_1BondDistance = QDoubleSpinBox(builder)
        self.Box_1BondDistance.setObjectName(u"Box_1BondDistance")
        self.Box_1BondDistance.setGeometry(QRect(80, 230, 61, 31))
        self.Box_1BondDistance.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.Box_1BondDistance.setMaximum(99999.000000000000000)
        self.Box_2BondAngle = QDoubleSpinBox(builder)
        self.Box_2BondAngle.setObjectName(u"Box_2BondAngle")
        self.Box_2BondAngle.setGeometry(QRect(160, 230, 61, 31))
        self.Box_2BondAngle.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.Box_2BondAngle.setMaximum(360.000000000000000)
        self.Box_3DihedralAngle = QDoubleSpinBox(builder)
        self.Box_3DihedralAngle.setObjectName(u"Box_3DihedralAngle")
        self.Box_3DihedralAngle.setGeometry(QRect(240, 230, 61, 31))
        self.Box_3DihedralAngle.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.Box_3DihedralAngle.setMaximum(360.000000000000000)
        self.AddAtomButton = QPushButton(builder)
        self.AddAtomButton.setObjectName(u"AddAtomButton")
        self.AddAtomButton.setGeometry(QRect(310, 230, 51, 31))
        self.Box_0Element = QLineEdit(builder)
        self.Box_0Element.setObjectName(u"Box_0Element")
        self.Box_0Element.setGeometry(QRect(20, 230, 41, 31))
        self.Box_0Element.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.tableWidget = QTableWidget(builder)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(20, 20, 401, 161))
        self.ErrorMessageBrowser = QTextBrowser(builder)
        self.ErrorMessageBrowser.setObjectName(u"ErrorMessageBrowser")
        self.ErrorMessageBrowser.setGeometry(QRect(20, 190, 381, 21))
        self.DeleteAtomButton = QPushButton(builder)
        self.DeleteAtomButton.setObjectName(u"DeleteAtomButton")
        self.DeleteAtomButton.setGeometry(QRect(370, 230, 51, 31))
        QWidget.setTabOrder(self.tableWidget, self.ErrorMessageBrowser)
        QWidget.setTabOrder(self.ErrorMessageBrowser, self.Box_0Element)
        QWidget.setTabOrder(self.Box_0Element, self.Box_1BondDistance)
        QWidget.setTabOrder(self.Box_1BondDistance, self.Box_2BondAngle)
        QWidget.setTabOrder(self.Box_2BondAngle, self.Box_3DihedralAngle)
        QWidget.setTabOrder(self.Box_3DihedralAngle, self.AddAtomButton)
        QWidget.setTabOrder(self.AddAtomButton, self.DeleteAtomButton)

        self.retranslateUi(builder)
        self.buttonBox.accepted.connect(builder.accept)
        self.buttonBox.rejected.connect(builder.reject)

        QMetaObject.connectSlotsByName(builder)
    # setupUi

    def retranslateUi(self, builder):
        builder.setWindowTitle(QCoreApplication.translate("builder", u"Z-Matrix Builder", None))
        self.AddAtomButton.setText(QCoreApplication.translate("builder", u"Add", None))
        self.DeleteAtomButton.setText(QCoreApplication.translate("builder", u"Delete", None))
    # retranslateUi
